# Deployment Guide - Render

This guide walks you through deploying the Adamani AI RAG platform to Render.

## Overview

The platform consists of two services:
- **Backend API**: FastAPI application with RAG, OCR, and document processing
- **Frontend**: Next.js web application

## Prerequisites

1. [Render account](https://render.com) (free tier works for testing)
2. OpenAI API key (get one at [platform.openai.com](https://platform.openai.com))
3. Git repository with your code pushed to GitHub/GitLab

## Architecture on Render

```
┌─────────────────┐
│   Frontend      │
│   (Next.js)     │
│   Port 3000     │
└────────┬────────┘
         │
         │ API Calls
         ▼
┌─────────────────┐
│   Backend       │
│   (FastAPI)     │
│   Port 8000     │
│   + Persistent  │
│     Disk 10GB   │
└─────────────────┘
```

## Deployment Steps

### Step 1: Prepare Your Repository

Ensure these files are in your repository:
- `render.yaml` (infrastructure as code)
- `Dockerfile` (backend)
- `frontend/Dockerfile` (frontend)
- `pyproject.toml` (Python dependencies)

### Step 2: Deploy to Render

#### Option A: Using Blueprint (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Blueprint"
3. Connect your Git repository
4. Render will detect `render.yaml` automatically
5. Click "Apply" to create both services

#### Option B: Manual Service Creation

**Backend Service:**
1. Go to Render Dashboard → "New" → "Web Service"
2. Connect repository
3. Configure:
   - Name: `adamani-ai-rag-backend`
   - Runtime: `Docker`
   - Dockerfile Path: `./Dockerfile`
   - Instance Type: `Starter` (or higher for production)
4. Add Disk:
   - Name: `adamani-data`
   - Mount Path: `/opt/render/project/data`
   - Size: `10GB`

**Frontend Service:**
1. New → "Web Service"
2. Connect same repository
3. Configure:
   - Name: `adamani-ai-rag-frontend`
   - Runtime: `Docker`
   - Dockerfile Path: `./frontend/Dockerfile`

### Step 3: Configure Environment Variables

#### Backend Environment Variables

Go to Backend Service → "Environment" tab and add:

**Required:**
```bash
# LLM Provider
LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=sk-...your-key...  # ⚠️ Mark as secret
OPENAI_MODEL=gpt-4o-mini

# Application
APP_NAME=Adamani AI RAG
LOG_LEVEL=INFO
DEBUG=false

# Vector Store
VECTOR_STORE_TYPE=chroma
VECTORDB_PATH=/opt/render/project/data/vectorstore

# RAG Settings
RETRIEVAL_TOP_K=3
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Storage
UPLOAD_DIR=/opt/render/project/data/uploads
PROCESSED_DIR=/opt/render/project/data/processed
```

**Optional (if using Anthropic):**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...your-key...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

#### Frontend Environment Variables

Go to Frontend Service → "Environment" tab:

```bash
NEXT_PUBLIC_API_URL=https://adamani-ai-rag-backend.onrender.com
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
```

**⚠️ Important:** Replace `adamani-ai-rag-backend.onrender.com` with your actual backend URL from Render.

### Step 4: Deploy

1. Commit and push your changes to Git
2. Render will automatically build and deploy both services
3. Monitor the logs for any errors
4. Once deployed, you'll get URLs:
   - Backend: `https://adamani-ai-rag-backend.onrender.com`
   - Frontend: `https://adamani-ai-rag-frontend.onrender.com`

## Post-Deployment

### Test Your Deployment

1. Visit your frontend URL
2. Try uploading a document
3. Ask questions about the document
4. Check backend logs if issues occur

### Update Backend URL in Frontend

If you used Blueprint, you may need to update the frontend's `NEXT_PUBLIC_API_URL`:

1. Go to Frontend Service → "Environment"
2. Update `NEXT_PUBLIC_API_URL` to your backend's actual URL
3. Trigger a manual deploy

### Monitor Your Services

- Check logs: Service → "Logs" tab
- View metrics: Service → "Metrics" tab
- Set up alerts for errors and downtime

## Cost Considerations

### Render Costs (as of 2024)

**Free Tier:**
- Services spin down after inactivity
- 750 hours/month per account
- Good for testing

**Starter Tier ($7-25/month per service):**
- Always running
- Persistent disk included
- Recommended for production

**Disk Storage:**
- First 1GB free
- Additional storage: $0.25/GB/month

### OpenAI Costs

**GPT-4o-mini** (recommended for cost):
- Input: $0.150 per 1M tokens
- Output: $0.600 per 1M tokens
- ~$0.01 per 100 requests (avg)

**GPT-4o** (better quality):
- Input: $2.50 per 1M tokens
- Output: $10.00 per 1M tokens

## Troubleshooting

### Backend Won't Start

**Check logs for:**
- Missing `OPENAI_API_KEY`
- Invalid API key
- Dependency installation failures

**Solution:**
- Verify all environment variables are set
- Check API key is valid at [platform.openai.com](https://platform.openai.com)

### Frontend Can't Connect to Backend

**Check:**
- `NEXT_PUBLIC_API_URL` is set correctly
- Backend service is running
- CORS is configured (should be `*` in settings)

### Disk Space Issues

Monitor disk usage:
```bash
# In Render shell
du -sh /opt/render/project/data/*
```

Clean up old files or increase disk size.

### Slow Performance

**Common causes:**
- Free tier services spin down (wait 30s for cold start)
- Large models downloading
- Insufficient resources

**Solutions:**
- Upgrade to Starter tier ($7/month)
- Use faster OpenAI models
- Optimize chunk sizes

## Future: Switching to RunPod for Ollama

When ready to use your own Ollama instance:

1. Deploy Ollama on RunPod with GPU
2. Get the RunPod endpoint URL
3. Update backend environment variables:
   ```bash
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=https://your-runpod-url.com
   OLLAMA_MODEL=llama3
   ```
4. Redeploy backend service

## Updating Your Deployment

### Automatic Deploys

Render auto-deploys on git push to main branch.

### Manual Deploy

1. Go to Service → "Manual Deploy"
2. Select branch
3. Click "Deploy"

### Rollback

1. Service → "Events"
2. Find previous successful deploy
3. Click "Rollback"

## Security Checklist

- [ ] API keys stored as secrets (not visible in logs)
- [ ] DEBUG=false in production
- [ ] Rate limiting configured (TODO: add to backend)
- [ ] Regular security updates
- [ ] Monitor for unusual activity

## Support

For issues:
- Check logs first
- Review Render documentation: https://render.com/docs
- OpenAI status: https://status.openai.com

## Next Steps

1. Set up custom domain (Render supports this)
2. Add monitoring with Sentry or similar
3. Configure backups for persistent disk
4. Add CI/CD tests before deploy
5. Scale up instance types as needed
