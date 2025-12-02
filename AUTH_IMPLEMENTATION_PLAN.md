# Authentication Implementation Plan

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Authentication Flow                       │
└─────────────────────────────────────────────────────────────┘

User Signs Up
    ↓
POST /auth/register {email, password, name}
    ↓
Backend: Hash password (bcrypt)
    ↓
PostgreSQL: INSERT INTO users
    ↓
Return: JWT token + user data
    ↓
Frontend: Store token in localStorage
    ↓
All API Requests: Include "Authorization: Bearer {token}"
    ↓
Backend: Verify JWT token
    ↓
If valid: Process request
If invalid: Return 401 Unauthorized
```

---

## Database Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Organizations table (multi-tenancy)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    plan_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT NOW(),
    owner_id UUID REFERENCES users(id)
);

-- Organization members (many-to-many)
CREATE TABLE organization_members (
    organization_id UUID REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),
    role VARCHAR(50) DEFAULT 'member',  -- admin, member, viewer
    joined_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (organization_id, user_id)
);

-- Documents (now tied to organization)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),
    filename VARCHAR(255),
    file_path VARCHAR(500),
    file_size BIGINT,
    file_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'processing',  -- processing, completed, failed
    chunks_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);

-- Sessions (optional, for better security)
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_org_members_user ON organization_members(user_id);
CREATE INDEX idx_org_members_org ON organization_members(organization_id);
CREATE INDEX idx_documents_org ON documents(organization_id);
CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_user ON sessions(user_id);
```

---

## Tech Stack

### Backend:
- **FastAPI-Users**: Authentication library for FastAPI
- **SQLAlchemy**: ORM for database
- **Alembic**: Database migrations
- **PostgreSQL**: Database (Render Postgres)
- **Bcrypt**: Password hashing
- **python-jose**: JWT tokens
- **passlib**: Password utilities

### Frontend:
- **JWT tokens**: Stored in localStorage
- **React Context**: Auth state management
- **Axios interceptors**: Auto-add token to requests

---

## Implementation Steps

### Step 1: Add Dependencies
```bash
# Backend
pip install fastapi-users[sqlalchemy]
pip install asyncpg  # PostgreSQL async driver
pip install alembic  # Database migrations
pip install python-jose[cryptography]  # JWT
pip install passlib[bcrypt]  # Password hashing
```

### Step 2: Database Setup (Render)
```yaml
# render.yaml - Add database
databases:
  - name: adamani-postgres
    databaseName: adamani_rag
    user: adamani_user
    plan: starter  # $7/month
    ipAllowList: []  # Allow all
```

### Step 3: SQLAlchemy Models
```python
# src/adamani_ai_rag/database/models.py
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships
    organizations = relationship("Organization", secondary="organization_members", back_populates="members")
    owned_organizations = relationship("Organization", back_populates="owner")

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    plan_tier = Column(String, default="free")
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    owner = relationship("User", back_populates="owned_organizations")
    members = relationship("User", secondary="organization_members", back_populates="organizations")
    documents = relationship("Document", back_populates="organization")

class OrganizationMember(Base):
    __tablename__ = "organization_members"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role = Column(String, default="member")
    joined_at = Column(DateTime, default=datetime.utcnow)

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String)
    file_path = Column(String)
    file_size = Column(BigInteger)
    file_type = Column(String)
    status = Column(String, default="processing")
    chunks_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)

    # Relationships
    organization = relationship("Organization", back_populates="documents")
    user = relationship("User")
```

### Step 4: FastAPI-Users Setup
```python
# src/adamani_ai_rag/auth/config.py
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTStrategy, AuthenticationBackend, BearerTransport

SECRET = settings.jwt_secret_key  # Store in env

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600 * 24 * 7)  # 7 days

bearer_transport = BearerTransport(tokenUrl="auth/login")

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager,
    [auth_backend],
)

# Routes
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
```

### Step 5: Auth Routes
```python
# src/adamani_ai_rag/api/routes/auth.py
from fastapi import APIRouter

router = APIRouter()

# Register route
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"]
)

# Register endpoint
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
)

# User management
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"]
)
```

### Step 6: Protect Existing Routes
```python
# Before (unprotected):
@app.post("/chat/")
async def chat(request: ChatRequest):
    ...

# After (protected):
@app.post("/chat/")
async def chat(
    request: ChatRequest,
    user: User = Depends(current_active_user)  # ← Require authentication
):
    # Get user's organization
    org = await get_user_organization(user.id)

    # Query only from their organization's vector store
    result = await rag_service.query(
        question=request.question,
        organization_id=org.id,  # ← Isolate by org
        session_id=request.session_id,
        k=request.k
    )
    return result
```

### Step 7: Frontend Auth Integration
```typescript
// frontend/src/lib/auth.ts
interface User {
  id: string;
  email: string;
  full_name: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export async function register(email: string, password: string, full_name: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, full_name })
  });

  if (!response.ok) {
    throw new Error('Registration failed');
  }

  const data = await response.json();

  // Store token
  localStorage.setItem('auth_token', data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));

  return data;
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: email, password })
  });

  if (!response.ok) {
    throw new Error('Login failed');
  }

  const data = await response.json();
  localStorage.setItem('auth_token', data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));

  return data;
}

export function logout() {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user');
}

export function getToken(): string | null {
  return localStorage.getItem('auth_token');
}

export function getUser(): User | null {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
}

export function isAuthenticated(): boolean {
  return !!getToken();
}
```

### Step 8: Auth Context (React)
```typescript
// frontend/src/contexts/AuthContext.tsx
import { createContext, useContext, useState, useEffect } from 'react';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Check if user is logged in
    const storedUser = getUser();
    if (storedUser) {
      setUser(storedUser);
    }
  }, []);

  const handleLogin = async (email: string, password: string) => {
    const data = await login(email, password);
    setUser(data.user);
  };

  const handleRegister = async (email: string, password: string, name: string) => {
    const data = await register(email, password, name);
    setUser(data.user);
  };

  const handleLogout = () => {
    logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{
      user,
      login: handleLogin,
      register: handleRegister,
      logout: handleLogout,
      isAuthenticated: !!user
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

### Step 9: Protected Routes (Frontend)
```typescript
// frontend/src/components/ProtectedRoute.tsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

// Usage in App.tsx
<Routes>
  <Route path="/login" element={<LoginPage />} />
  <Route path="/register" element={<RegisterPage />} />
  <Route path="/" element={
    <ProtectedRoute>
      <HomePage />
    </ProtectedRoute>
  } />
</Routes>
```

### Step 10: Login/Register UI Components
```typescript
// frontend/src/pages/LoginPage.tsx
import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError('Invalid email or password');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <h2 className="text-3xl font-bold text-center">Sign in to Adamani AI</h2>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
          >
            Sign in
          </button>
        </form>

        <p className="text-center text-sm text-gray-600">
          Don't have an account?{' '}
          <a href="/register" className="text-blue-600 hover:text-blue-500">
            Sign up
          </a>
        </p>
      </div>
    </div>
  );
}
```

---

## Migration Path (Existing Data)

Since you already have deployed version:

1. **Add database** (Render Postgres)
2. **Run migrations** (create tables)
3. **Keep existing API working** (backwards compatible)
4. **Add `/auth/*` routes** (new)
5. **Gradually migrate endpoints** to require auth
6. **Create default organization** for existing data
7. **Announce to users**: "We've added accounts! Sign up to keep your data"

---

## Environment Variables

```bash
# Backend (.env)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
JWT_SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
JWT_ALGORITHM=HS256
JWT_EXPIRATION_SECONDS=604800  # 7 days

# Frontend (.env)
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

---

## Timeline

- **Day 1:** Add PostgreSQL to Render, create database schema
- **Day 2:** Implement backend auth (FastAPI-Users)
- **Day 3:** Protect existing routes, add org isolation
- **Day 4:** Frontend auth UI (login, register pages)
- **Day 5:** Auth context, protected routes
- **Day 6:** Update API calls to include token
- **Day 7:** Test, deploy, celebrate! 🎉

---

## Cost

- **PostgreSQL (Render):** $7/month (Starter) → $50/month (Standard) at scale
- **Development time:** 40-60 hours (1-2 weeks)
- **Libraries:** Free (open source)

**Total:** $7/month + your time

---

## Next: Multi-Tenancy & Data Isolation

Once auth is done, we need to isolate data per organization:

```python
# Vector store isolation
def get_collection_name(organization_id: str) -> str:
    return f"org_{organization_id}"

# Usage
collection = vectorstore.get_collection(
    get_collection_name(user.organization.id)
)
```

This ensures:
- User A can't see User B's documents
- Complete data isolation
- Can sell to multiple businesses
- B2B ready!

---

Ready to start implementing? Let's begin!
