# Local Development Setup with Ollama

This guide will help you run the Adamani AI RAG system locally on your machine with Ollama (100% free and private).

## Prerequisites

### Required Software
- **Python 3.10+** - Download from [python.org](https://www.python.org/downloads/)
- **Node.js 18+** - Download from [nodejs.org](https://nodejs.org/)
- **PostgreSQL 14+** - Download from [postgresql.org](https://www.postgresql.org/download/)
- **Ollama** - Download from [ollama.com](https://ollama.com/download)
- **Poetry** - Python package manager
- **Git** - Version control

### Optional (Recommended)
- **Tesseract OCR** - For scanned document processing

---

## Step 1: Install Ollama

Ollama allows you to run large language models locally on your machine.

### macOS
```bash
# Download and install from: https://ollama.com/download
# Or use Homebrew:
brew install ollama
```

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows
Download the installer from [ollama.com/download](https://ollama.com/download)

### Start Ollama Service
```bash
# Start Ollama (it will run in the background)
ollama serve
```

### Pull a Model
```bash
# Pull Llama 3 (recommended, ~4.7GB)
ollama pull llama3

# Or use Mistral (smaller, ~4.1GB)
ollama pull mistral

# Or use Phi-3 (very small, ~2.3GB)
ollama pull phi3
```

Verify installation:
```bash
ollama list
# Should show the models you pulled

# Test the model
ollama run llama3 "Hello, how are you?"
```

---

## Step 2: Clone and Setup Backend

### Clone Repository
```bash
git clone https://github.com/yourusername/adamani-ai-rag.git
cd adamani-ai-rag
```

### Install Poetry
```bash
# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Add to PATH (follow instructions after installation)
```

### Install Backend Dependencies
```bash
# Install all Python dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Setup PostgreSQL Database
```bash
# Create database
createdb adamani_rag

# Or using psql:
psql postgres
CREATE DATABASE adamani_rag;
\q
```

### Configure Environment Variables
```bash
# Create .env file in project root
cat > .env << 'EOF'
# Application
APP_NAME="Adamani AI RAG"
APP_VERSION="1.0.0"
DEBUG=true
LOG_LEVEL=INFO

# LLM Configuration
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Embedding Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu

# Vector Store
VECTOR_STORE_TYPE=chroma
VECTORDB_PATH=./data/vectorstore

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/adamani_rag

# Authentication
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRATION_SECONDS=604800

# CORS (for local development)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# API
API_HOST=0.0.0.0
API_PORT=8000

# RAG Settings
RETRIEVAL_TOP_K=3
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# OCR
OCR_ENGINE=tesseract
OCR_LANGUAGES=eng
EOF
```

### Run Database Migrations
```bash
# Initialize database tables
poetry run alembic upgrade head

# Verify tables were created
psql adamani_rag -c "\dt"
```

### Start Backend Server
```bash
# Start with auto-reload
poetry run uvicorn src.adamani_ai_rag.api.app:app --reload --host 0.0.0.0 --port 8000

# Or use this shorter command:
poetry run python -m uvicorn src.adamani_ai_rag.api.app:app --reload
```

Backend will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Step 3: Setup Frontend

### Navigate to Frontend Directory
```bash
cd frontend
```

### Install Frontend Dependencies
```bash
npm install
```

### Configure Frontend Environment
```bash
# Create .env.local file
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
```

### Start Frontend Development Server
```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

---

## Step 4: Install Tesseract OCR (Optional)

For processing scanned documents and images.

### macOS
```bash
brew install tesseract
```

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### Windows
Download installer from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

### Verify Installation
```bash
tesseract --version
```

---

## Step 5: Test the Application

### 1. Create an Account
- Open http://localhost:3000/signup
- Enter email and password
- Click "Sign Up"

### 2. Login
- Go to http://localhost:3000/login
- Enter credentials
- You'll be redirected to the main page

### 3. Upload Documents
- Click on "Upload Document"
- Select a PDF or image file
- Wait for processing (watch backend logs)

### 4. Ask Questions
- Type a question in the chat box
- Press Enter
- Watch the streaming response

### 5. View Invoices (if you upload invoices)
- Navigate to the invoices section
- View extracted invoice data
- Export to CSV/Excel

---

## Directory Structure

After setup, your project should look like:

```
adamani_ai_rag/
├── data/
│   ├── uploads/          # Uploaded files
│   ├── processed/        # Processed files
│   └── vectorstore/      # ChromaDB data
├── src/
│   └── adamani_ai_rag/   # Backend source code
├── frontend/
│   ├── src/              # Frontend source code
│   ├── node_modules/     # Frontend dependencies
│   └── .env.local        # Frontend config
├── .venv/                # Python virtual environment
├── .env                  # Backend config
└── pyproject.toml        # Python dependencies
```

---

## Troubleshooting

### Ollama Issues

**Ollama not responding:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it:
ollama serve
```

**Model not found:**
```bash
# List available models
ollama list

# Pull the model if missing
ollama pull llama3
```

### Database Issues

**Connection refused:**
```bash
# Check PostgreSQL is running
pg_isready

# Start PostgreSQL (macOS)
brew services start postgresql

# Start PostgreSQL (Linux)
sudo systemctl start postgresql
```

**Authentication failed:**
```bash
# Update DATABASE_URL in .env with correct credentials
# Default is usually: postgres:postgres@localhost:5432
```

### Backend Issues

**Module not found:**
```bash
# Make sure you're in the poetry shell
poetry shell

# Reinstall dependencies
poetry install
```

**Port already in use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
poetry run uvicorn src.adamani_ai_rag.api.app:app --reload --port 8001
```

### Frontend Issues

**Cannot connect to backend:**
- Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
- Verify backend is running on http://localhost:8000
- Check CORS configuration in backend `.env`

**Dependencies error:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## Performance Tips

### Speed Up Embeddings
```bash
# If you have a GPU, install CUDA-enabled version
poetry add sentence-transformers[gpu]

# Update .env
EMBEDDING_DEVICE=cuda
```

### Use Smaller Models
```bash
# For faster responses (less accurate)
ollama pull phi3

# Update .env
OLLAMA_MODEL=phi3
```

### Increase Memory for Ollama
```bash
# Set Ollama environment variable (Linux/macOS)
export OLLAMA_NUM_THREAD=8
export OLLAMA_NUM_GPU=1

# Restart Ollama
ollama serve
```

---

## Development Workflow

### Daily Development
```bash
# Terminal 1: Start Ollama (if not running)
ollama serve

# Terminal 2: Start Backend
cd adamani_ai_rag
poetry shell
poetry run uvicorn src.adamani_ai_rag.api.app:app --reload

# Terminal 3: Start Frontend
cd adamani_ai_rag/frontend
npm run dev

# Terminal 4: Watch logs
tail -f logs/app.log
```

### Testing Changes
```bash
# Backend tests
poetry run pytest

# Frontend tests
cd frontend
npm test

# Manual testing via API docs
open http://localhost:8000/docs
```

---

## Switching LLM Providers

Your app supports multiple LLM providers. To switch:

### Use OpenAI (requires API key)
```bash
# Update .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

### Use Anthropic Claude (requires API key)
```bash
# Update .env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

### Stick with Ollama (100% free)
```bash
# Update .env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

---

## Next Steps

1. **Read the main README.md** for full feature documentation
2. **Check API docs** at http://localhost:8000/docs
3. **Explore the code** in `src/adamani_ai_rag/`
4. **Add your own models** with Ollama
5. **Customize the frontend** in `frontend/src/`

---

## Getting Help

- **Issues**: https://github.com/yourusername/adamani-ai-rag/issues
- **Documentation**: See `docs/` folder
- **Discord**: (coming soon)

---

## System Requirements

### Minimum
- CPU: 4 cores
- RAM: 8GB (16GB recommended for Ollama)
- Disk: 20GB free space (for models + data)
- OS: macOS, Linux, or Windows 10+

### Recommended
- CPU: 8+ cores
- RAM: 16GB+ (32GB for better performance)
- GPU: NVIDIA GPU with 8GB+ VRAM (optional, speeds up embeddings)
- Disk: SSD with 50GB+ free space

---

**Ready to build?** Start with Step 1 and you'll be running locally in 15-20 minutes!

For production deployment, see the main README.md deployment section.
