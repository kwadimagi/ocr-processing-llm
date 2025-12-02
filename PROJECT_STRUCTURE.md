# Adamani AI RAG - Project Structure

A modular AI automation backend providing local LLM-powered RAG, memory-enabled conversational AI, and OCR-based document processing.

## Directory Structure

```
adamani_ai_rag/
├── src/adamani_ai_rag/
│   ├── core/                    # Core business logic modules
│   │   ├── llm.py              # LLM client management (Ollama)
│   │   ├── embeddings.py       # Embedding model management
│   │   ├── vectorstore.py      # Vector store operations (FAISS)
│   │   ├── memory.py           # Conversation memory management
│   │   └── ocr.py              # OCR processing (Tesseract)
│   │
│   ├── services/               # Service layer (business logic)
│   │   ├── rag_service.py      # RAG query processing
│   │   └── document_service.py # Document ingestion & processing
│   │
│   ├── api/                    # FastAPI application
│   │   ├── app.py             # Main FastAPI app initialization
│   │   ├── dependencies.py     # Dependency injection
│   │   ├── models/            # Pydantic models
│   │   │   ├── requests.py    # Request models
│   │   │   └── responses.py   # Response models
│   │   └── routes/            # API endpoints
│   │       ├── health.py      # Health check
│   │       ├── chat.py        # Chat/RAG endpoints
│   │       └── documents.py   # Document management
│   │
│   ├── config/                 # Configuration management
│   │   └── settings.py        # Application settings (env vars)
│   │
│   └── utils/                  # Utility modules
│       └── logger.py          # Logging configuration (Loguru)
│
├── data/                       # Data storage
│   ├── uploads/               # Uploaded files
│   ├── processed/             # Processed documents
│   └── vectorstore/           # Vector database files
│
├── pyproject.toml             # Project dependencies
├── Dockerfile                 # Docker configuration
└── .env                       # Environment variables (not in git)
```

## Module Responsibilities

### Core Layer
**Purpose**: Low-level integrations with external services and libraries

- **llm.py**: Manages Ollama LLM client, handles text generation
- **embeddings.py**: Manages HuggingFace embeddings for document vectorization
- **vectorstore.py**: Handles FAISS vector store operations (add, search, persist)
- **memory.py**: Manages conversation history per session
- **ocr.py**: Processes images with Tesseract OCR

### Service Layer
**Purpose**: Business logic that orchestrates core modules

- **rag_service.py**: Implements RAG pipeline (retrieve → augment → generate)
- **document_service.py**: Handles document ingestion, chunking, and indexing

### API Layer
**Purpose**: HTTP interface for external clients

- **app.py**: FastAPI application setup, middleware, route registration
- **dependencies.py**: Singleton instances for dependency injection
- **routes/**: REST API endpoints organized by feature
- **models/**: Request/response validation with Pydantic

### Config Layer
**Purpose**: Centralized configuration management

- **settings.py**: Environment-based settings using Pydantic BaseSettings

### Utils Layer
**Purpose**: Shared utilities

- **logger.py**: Beautiful logging with Loguru

## Key Features

### 1. RAG (Retrieval-Augmented Generation)
- Retrieve relevant documents from vector store
- Augment LLM prompt with retrieved context
- Generate contextual responses

### 2. Memory-Enabled Chat
- Per-session conversation history
- Context-aware responses
- History management (clear, view)

### 3. OCR Processing
- Extract text from images (PNG, JPG, TIFF, etc.)
- Automatic chunking and indexing
- Batch directory processing

### 4. Modular Architecture
- Clean separation of concerns
- Dependency injection for testability
- Easy to extend with new features

## API Endpoints

### Health
- `GET /health` - Service health check

### Chat
- `POST /chat/` - RAG-powered chat
- `DELETE /chat/memory/{session_id}` - Clear session memory
- `DELETE /chat/memory` - Clear all memories

### Documents
- `POST /documents/texts` - Add text documents
- `POST /documents/upload` - Upload & process files
- `POST /documents/process-directory` - Batch process directory
- `DELETE /documents/clear` - Clear knowledge base

## Configuration

Environment variables (`.env`):

```bash
# LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
LLM_TEMPERATURE=0.1

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# RAG
RETRIEVAL_TOP_K=3
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# OCR
OCR_ENGINE=tesseract
OCR_LANGUAGES=eng

# Storage
VECTORDB_PATH=./data/vectorstore
UPLOAD_DIR=./data/uploads

# API
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

## Development Workflow

1. **Add new core functionality**: Create module in `core/`
2. **Add business logic**: Create service in `services/`
3. **Expose via API**: Add route in `api/routes/`
4. **Configure**: Add settings to `config/settings.py`

## Design Principles

- **Separation of Concerns**: Each layer has distinct responsibilities
- **Dependency Injection**: Services receive dependencies, not create them
- **Configuration Management**: All settings in one place
- **Logging**: Consistent, beautiful logging throughout
- **Type Safety**: Pydantic models for validation
- **Modularity**: Easy to swap implementations (e.g., different vector stores)
