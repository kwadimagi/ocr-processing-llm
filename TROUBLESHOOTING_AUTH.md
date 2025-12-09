# Authentication Troubleshooting Guide

## Common Issue: "Invalid token" Error

### Symptom
Browser console shows:
```javascript
{detail: "Invalid token"}
```

### Root Cause
The JWT token cannot be decoded by the backend. This happens when:
1. **JWT_SECRET_KEY mismatch** - Token generated with different secret than validation
2. **Token expired** - Token exceeded `JWT_EXPIRATION_SECONDS`
3. **Corrupted token** - Token damaged in storage/transmission
4. **Manual token decoding** - Custom JWT validation code doesn't match auth system

---

## Quick Fix: Logout and Login

**90% of "Invalid token" errors are fixed by:**

```bash
1. Open browser console (F12)
2. Run: localStorage.clear()
3. Refresh page
4. Login again
```

This forces a new token to be generated with the current JWT_SECRET_KEY.

---

## Detailed Troubleshooting

### Step 1: Check JWT Configuration on Render

**Environment Variables to Verify:**

```bash
# On Render Dashboard → Your Service → Environment
JWT_SECRET_KEY=<must-be-at-least-32-characters>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_SECONDS=604800  # 7 days
```

**How to Generate JWT_SECRET_KEY:**
```bash
# On your machine
openssl rand -hex 32

# Example output:
# a3d8f72b4e9c1a5d7f3e8b2c9d4a6e1f8c3b7a5d2e9f4c1b8a6d3e7f2c5b9a4d
```

**Important:** If you change `JWT_SECRET_KEY`, all existing tokens become invalid!

### Step 2: Verify Token Format

**Check Token in Browser:**
```javascript
// Open browser console
const token = localStorage.getItem('auth_token');
console.log('Token:', token);

// Token should look like:
// eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

// Should have 3 parts separated by dots (.)
```

**Decode Token (Debug Only):**
```javascript
// Visit https://jwt.io and paste token
// Or in console:
const parts = token.split('.');
const payload = JSON.parse(atob(parts[1]));
console.log('Payload:', payload);

// Should show:
// {
//   "sub": "user-uuid-here",
//   "exp": 1234567890,  // Expiration timestamp
//   "iat": 1234567890   // Issued at timestamp
// }
```

### Step 3: Check Token Expiration

**Calculate if token is expired:**
```javascript
const parts = token.split('.');
const payload = JSON.parse(atob(parts[1]));
const expiration = new Date(payload.exp * 1000);
const now = new Date();

console.log('Token expires:', expiration);
console.log('Current time:', now);
console.log('Is expired?', now > expiration);

// If expired, logout and login again
```

### Step 4: Verify Authentication Flow

**Test full auth flow:**

```bash
# 1. Test health endpoint (no auth required)
curl https://adamani-ai-rag-backend.onrender.com/health

# 2. Test login
curl -X POST https://adamani-ai-rag-backend.onrender.com/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=yourpassword"

# Should return:
# {"access_token": "eyJhbG...", "token_type": "bearer"}

# 3. Test protected endpoint with token
curl https://adamani-ai-rag-backend.onrender.com/invoices \
  -H "Authorization: Bearer eyJhbG..."

# Should return invoices array (or empty array)
```

### Step 5: Check CORS Headers

**Verify Authorization header is allowed:**

In `src/adamani_ai_rag/api/app.py`, check:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # ← Must include Authorization
    expose_headers=["*"],
)
```

### Step 6: Check Backend Logs on Render

**View logs:**
1. Go to Render Dashboard
2. Select your backend service
3. Click "Logs" tab
4. Look for JWT-related errors:
   ```
   jose.exceptions.JWTError: Signature verification failed
   jose.exceptions.ExpiredSignatureError: Signature has expired
   ```

---

## The Fix We Applied

### Problem
The `/invoices` endpoint was manually decoding JWT tokens:

```python
# ❌ OLD CODE (Manual token decoding)
token = auth_header.split(" ")[1]
payload = jwt.decode(
    token,
    settings.jwt_secret_key,
    algorithms=[settings.jwt_algorithm]
)
user_id = payload.get("sub")
```

**Issues with this approach:**
- Duplicate JWT decoding logic (error-prone)
- Doesn't respect FastAPI Users configuration
- Hard to maintain
- Easy to introduce bugs

### Solution
Use the built-in `current_active_user` dependency:

```python
# ✅ NEW CODE (Use FastAPI Users dependency)
from ...auth import current_active_user

@router.get("/invoices")
async def get_user_invoices(
    user: User = Depends(current_active_user),  # ← Automatic auth
    db: AsyncSession = Depends(get_db),
):
    # user is already validated and loaded from DB
    query = select(Invoice).where(Invoice.user_id == user.id)
```

**Benefits:**
- Consistent with other protected endpoints
- Automatic token validation
- Better error messages
- Less code to maintain

---

## Prevention: Best Practices

### 1. Use Authentication Dependencies (Not Manual Decoding)

**Always use:**
```python
from ...auth import current_active_user

@router.get("/my-endpoint")
async def my_endpoint(user: User = Depends(current_active_user)):
    # user is authenticated and active
```

**Never manually decode unless absolutely necessary.**

### 2. Secure JWT_SECRET_KEY Management

**Development (.env.local):**
```bash
JWT_SECRET_KEY=dev-secret-key-for-local-testing-only
```

**Production (Render Environment Variables):**
```bash
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>
# Must be different from development!
# Must be at least 32 characters
# Never commit to Git
```

### 3. Handle Token Expiration Gracefully

**Frontend (AuthContext.tsx):**
```typescript
useEffect(() => {
  const loadAuth = async () => {
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken) {
      try {
        const response = await fetch(`${API_BASE}/users/me`, {
          headers: { 'Authorization': `Bearer ${storedToken}` },
        });
        if (response.ok) {
          setUser(await response.json());
        } else {
          // Token invalid or expired → clear it
          localStorage.removeItem('auth_token');
          setToken(null);
        }
      } catch (error) {
        localStorage.removeItem('auth_token');
      }
    }
  };
  loadAuth();
}, []);
```

### 4. Consistent Token Storage

**Use only one storage location:**
```typescript
// ✅ GOOD: Consistent
localStorage.setItem('auth_token', token);
const token = localStorage.getItem('auth_token');

// ❌ BAD: Mixed storage
sessionStorage.setItem('token', token);  // Different key
localStorage.setItem('auth_token', token);  // Different storage
```

### 5. Add Token Refresh (Optional)

For better UX, implement token refresh:

```python
# Backend: Add refresh token endpoint
@router.post("/auth/refresh")
async def refresh_token(
    user: User = Depends(current_active_user)
):
    # Generate new token
    return {"access_token": new_token, "token_type": "bearer"}
```

```typescript
// Frontend: Refresh before expiration
setInterval(async () => {
  if (isAuthenticated) {
    const response = await fetch(`${API_BASE}/auth/refresh`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('auth_token', data.access_token);
    }
  }
}, 6 * 24 * 60 * 60 * 1000); // Refresh every 6 days (token expires in 7 days)
```

---

## Testing Authentication

### Manual Test Script

```bash
#!/bin/bash

API_BASE="https://adamani-ai-rag-backend.onrender.com"
EMAIL="test@example.com"
PASSWORD="testpassword123"

echo "1. Testing health endpoint..."
curl -s $API_BASE/health | jq

echo -e "\n2. Testing registration..."
curl -s -X POST $API_BASE/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"full_name\":\"Test User\"}" | jq

echo -e "\n3. Testing login..."
TOKEN=$(curl -s -X POST $API_BASE/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASSWORD" | jq -r '.access_token')

echo "Token: $TOKEN"

echo -e "\n4. Testing /users/me..."
curl -s $API_BASE/users/me \
  -H "Authorization: Bearer $TOKEN" | jq

echo -e "\n5. Testing /invoices..."
curl -s $API_BASE/invoices \
  -H "Authorization: Bearer $TOKEN" | jq

echo -e "\n✅ All tests complete!"
```

Save as `test-auth.sh`, run with `chmod +x test-auth.sh && ./test-auth.sh`

---

## Common Errors and Solutions

### Error: "Missing or invalid token"
**Cause:** Authorization header not sent or malformed

**Fix:**
```javascript
// Ensure token is sent correctly
fetch(`${API_BASE}/invoices`, {
  headers: {
    'Authorization': `Bearer ${token}`,  // ← Space after Bearer!
  }
})
```

### Error: "Signature verification failed"
**Cause:** JWT_SECRET_KEY mismatch

**Fix:**
1. Check Render environment variables
2. Ensure JWT_SECRET_KEY is set correctly
3. Logout and login to get new token

### Error: "Signature has expired"
**Cause:** Token older than JWT_EXPIRATION_SECONDS

**Fix:**
1. Logout and login to get fresh token
2. Consider increasing JWT_EXPIRATION_SECONDS
3. Implement token refresh

### Error: "User inactive or not found"
**Cause:** User exists in token but not in database

**Fix:**
1. Check if user was deleted
2. Clear localStorage and create new account
3. Check database connection on Render

---

## Debugging Checklist

When authentication fails, check in this order:

- [ ] **Frontend:** Token exists in localStorage?
- [ ] **Frontend:** Token sent in Authorization header?
- [ ] **Network:** Request reaches backend? (check Network tab)
- [ ] **Backend:** JWT_SECRET_KEY set on Render?
- [ ] **Backend:** CORS allows Authorization header?
- [ ] **Backend:** Logs show JWT error? (check Render logs)
- [ ] **Token:** Not expired? (decode at jwt.io)
- [ ] **Token:** Valid format? (3 parts separated by dots)
- [ ] **Database:** User exists and is_active=true?
- [ ] **Quick fix:** Logout, clear localStorage, login again

---

## Summary

**The "Invalid token" error is usually fixed by:**
1. Logout
2. Clear localStorage (`localStorage.clear()`)
3. Login again

**Root cause is typically:**
- JWT_SECRET_KEY mismatch between environments
- Expired token (older than 7 days)
- Manual token decoding that doesn't match auth system

**Best practice:**
- Use `current_active_user` dependency for all protected endpoints
- Never manually decode JWT unless absolutely necessary
- Keep JWT_SECRET_KEY consistent and secure
- Test authentication flow end-to-end after deployment

---

## Need More Help?

1. Check Render logs for detailed error messages
2. Test with curl to isolate frontend vs backend issues
3. Verify JWT_SECRET_KEY is set on Render
4. Ensure token is not expired (decode at jwt.io)
5. Clear localStorage and login again

If issue persists, check GitHub Issues or contact support.
