# Quick Start Guide - Run Locally in 5 Minutes

## Prerequisites Check
- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] PostgreSQL running
- [ ] Ollama installed

## Installation (First Time Only)

```bash
# 1. Install Ollama
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh
# Windows: Download from https://ollama.com/download

# 2. Start Ollama and pull model
ollama serve  # Run in background
ollama pull llama3  # ~4.7GB download

# 3. Setup database
createdb adamani_rag

# 4. Install backend dependencies
poetry install

# 5. Setup environment
cp .env.example .env
# Edit .env with your database credentials

# 6. Run database migrations
poetry run alembic upgrade head

# 7. Install frontend dependencies
cd frontend
npm install
```

## Daily Development

### Option 1: Using the Start Script (Easiest)
```bash
# Terminal 1: Start backend
./start-local.sh

# Terminal 2: Start frontend
cd frontend && npm run dev
```

### Option 2: Manual Start
```bash
# Terminal 1: Ollama (if not running)
ollama serve

# Terminal 2: Backend
poetry run uvicorn src.adamani_ai_rag.api.app:app --reload

# Terminal 3: Frontend
cd frontend && npm run dev
```

## Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Quick Test

```bash
# 1. Create account at http://localhost:3000/signup
# 2. Login at http://localhost:3000/login
# 3. Upload a PDF document
# 4. Ask a question about the document
```

## Common Issues

### Ollama not responding
```bash
ollama serve
ollama list  # Check models
ollama pull llama3  # If model missing
```

### Database connection error
```bash
# Check PostgreSQL is running
pg_isready

# Start if not running
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql
```

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
poetry run uvicorn src.adamani_ai_rag.api.app:app --reload --port 8001
```

## Configuration

### Switch LLM Provider

Edit `.env`:

```bash
# Use Ollama (free, local)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3

# Use OpenAI (requires API key)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Use Anthropic Claude (requires API key)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

### Use Different Ollama Model

```bash
# List available models
ollama list

# Pull other models
ollama pull mistral  # Smaller, faster
ollama pull phi3     # Very small
ollama pull codellama  # Code-focused

# Update .env
OLLAMA_MODEL=mistral
```

## Next Steps

- Read [LOCAL_SETUP.md](LOCAL_SETUP.md) for detailed setup
- Read [README.md](README.md) for full documentation
- Check [API docs](http://localhost:8000/docs) for API reference

## Need Help?

- See [LOCAL_SETUP.md](LOCAL_SETUP.md) for troubleshooting
- Check GitHub Issues
- Read the full README.md
