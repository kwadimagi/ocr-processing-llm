# Quick Start Guide

## Prerequisites

- Docker (recommended) OR
- Python 3.10+, Poetry, and Ollama running locally
- Tesseract OCR (for local development)

## Option 1: Docker (Recommended)

### 1. Build the Docker image
```bash
docker build -t adamani_ai_rag:latest .
```

### 2. Run the container
```bash
docker run -p 8080:8000 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  adamani_ai_rag:latest
```

### 3. Access the API
- API: http://localhost:8080
- Docs: http://localhost:8080/docs
- Health: http://localhost:8080/health

## Option 2: Local Development

### 1. Install dependencies
```bash
poetry install
```

### 2. Set up environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run the server
```bash
uvicorn src.adamani_ai_rag.api.app:app --reload --host 0.0.0.0 --port 8000
```

## Example Usage

### 1. Add documents to knowledge base
```bash
curl -X POST "http://localhost:8080/documents/texts" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Paris is the capital of France.",
      "The Eiffel Tower is in Paris."
    ]
  }'
```

### 2. Chat with RAG
```bash
curl -X POST "http://localhost:8080/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the capital of France?",
    "session_id": "user_123"
  }'
```

### 3. Upload image for OCR
```bash
curl -X POST "http://localhost:8080/documents/upload" \
  -F "file=@document.png"
```

### 4. Clear conversation memory
```bash
curl -X DELETE "http://localhost:8080/chat/memory/user_123"
```

## API Endpoints Overview

### Health
- `GET /health` - Service status

### Chat
- `POST /chat/` - Ask questions with RAG
- `DELETE /chat/memory/{session_id}` - Clear specific session
- `DELETE /chat/memory` - Clear all sessions

### Documents
- `POST /documents/texts` - Add text documents
- `POST /documents/upload` - Upload files (images)
- `POST /documents/process-directory` - Batch process
- `DELETE /documents/clear` - Clear knowledge base

## Configuration

Key environment variables:

```bash
# LLM
OLLAMA_MODEL=llama3              # LLM model to use
LLM_TEMPERATURE=0.1              # Response creativity (0-1)

# RAG
RETRIEVAL_TOP_K=3                # Number of docs to retrieve
CHUNK_SIZE=1000                  # Document chunk size
CHUNK_OVERLAP=200                # Overlap between chunks

# OCR
OCR_LANGUAGES=eng                # Tesseract language (eng, fra, etc.)

# Logging
LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR
```

## Project Structure

```
src/adamani_ai_rag/
├── core/          # Core functionality (LLM, embeddings, OCR, etc.)
├── services/      # Business logic (RAG, documents)
├── api/           # FastAPI application
│   ├── routes/    # API endpoints
│   └── models/    # Request/response models
├── config/        # Configuration management
└── utils/         # Utilities (logging, etc.)
```

## Next Steps

1. **Customize**: Edit `config/settings.py` for your needs
2. **Extend**: Add new routes in `api/routes/`
3. **Deploy**: Use Docker for production deployment
4. **Monitor**: Check logs with Loguru's beautiful output

## Troubleshooting

### Ollama connection issues
Make sure Ollama is running and accessible:
```bash
curl http://localhost:11434/api/tags
```

### OCR not working
Ensure Tesseract is installed:
```bash
tesseract --version
```

### Import errors
Reinstall dependencies:
```bash
poetry install
```

## Documentation

- Full structure: See `PROJECT_STRUCTURE.md`
- API docs: http://localhost:8080/docs (when running)
- Example env: `.env.example`
