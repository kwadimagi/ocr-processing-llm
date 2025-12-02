# Dependencies

All dependencies with pinned versions for reproducible builds.

## Core Framework

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | `>=0.115.0,<0.116.0` | Web framework for building APIs |
| `uvicorn[standard]` | `>=0.32.0,<0.33.0` | ASGI server with websocket support |
| `pydantic` | `>=2.9.0,<3.0.0` | Data validation using Python type hints |
| `pydantic-settings` | `>=2.6.0,<3.0.0` | Settings management from environment variables |

## LangChain Ecosystem

| Package | Version | Purpose |
|---------|---------|---------|
| `langchain` | `>=0.3.0,<0.4.0` | Core LangChain framework |
| `langchain-core` | `>=0.3.0,<0.4.0` | Core abstractions and interfaces |
| `langchain-community` | `>=0.3.0,<0.4.0` | Community integrations |
| `langchain-huggingface` | `>=0.1.0,<0.2.0` | HuggingFace embeddings integration |
| `langchain-ollama` | `>=0.2.0,<0.3.0` | Ollama LLM integration |
| `langchain-chroma` | `>=0.1.0,<0.2.0` | ChromaDB integration |

## AI/ML & Vector Stores

| Package | Version | Purpose |
|---------|---------|---------|
| `ollama` | `>=0.4.0,<0.5.0` | Python client for Ollama |
| `chromadb` | `>=0.5.0,<0.6.0` | **Default** vector database (persistent) |
| `faiss-cpu` | `>=1.9.0,<2.0.0` | Alternative vector database (in-memory) |
| `sentence-transformers` | `>=3.3.0,<4.0.0` | State-of-the-art text embeddings |
| `numpy` | `>=2.0.0,<3.0.0` | Numerical computing |

## OCR & Document Processing

| Package | Version | Purpose |
|---------|---------|---------|
| `pytesseract` | `>=0.3.0,<0.4.0` | Python wrapper for Tesseract OCR |
| `pillow` | `>=11.0.0,<12.0.0` | Python Imaging Library (PIL) |

## Utilities

| Package | Version | Purpose |
|---------|---------|---------|
| `loguru` | `>=0.7.0,<0.8.0` | Beautiful and powerful logging |
| `python-dotenv` | `>=1.0.0,<2.0.0` | Load environment variables from .env |
| `python-multipart` | `>=0.0.20,<0.1.0` | File upload support |
| `aiofiles` | `>=24.1.0,<25.0.0` | Async file operations |

## System Requirements

- Python: `>=3.10`
- Tesseract OCR: Required for document processing (system package)

## Vector Store Comparison

### ChromaDB (Default)
**Pros:**
- ✅ Persistent storage (automatic)
- ✅ Built-in metadata filtering
- ✅ Production-ready
- ✅ Better for large datasets
- ✅ Multi-user safe

**Cons:**
- ❌ Slightly slower initialization
- ❌ Requires disk space

**Best for:** Production deployments, persistent data

### FAISS
**Pros:**
- ✅ Lightning fast (in-memory)
- ✅ Lower memory footprint
- ✅ Quick prototyping

**Cons:**
- ❌ Requires manual persistence
- ❌ No built-in metadata filtering
- ❌ Lost on restart (unless saved)

**Best for:** Development, testing, temporary workloads

## Switching Vector Stores

To switch between ChromaDB and FAISS, set the environment variable:

```bash
# Use ChromaDB (default)
VECTOR_STORE_TYPE=chroma

# Use FAISS
VECTOR_STORE_TYPE=faiss
```

## Installation

### Poetry (Recommended)
```bash
poetry install
```

### Pip
```bash
pip install -e .
```

### Docker
Dependencies are automatically installed during Docker build.

## Version Strategy

We use **caret requirements** (`>=X.Y.0,<X+1.0.0`) for:
- **Stability**: Patch updates are allowed (bug fixes)
- **Safety**: Minor version bumps require testing
- **Reproducibility**: Lock file ensures exact versions

## Updating Dependencies

```bash
# Update all dependencies to latest compatible versions
poetry update

# Update specific package
poetry update langchain

# Check for outdated packages
poetry show --outdated
```

## Security

Run security audits regularly:

```bash
# Using pip-audit
pip install pip-audit
pip-audit

# Using safety
pip install safety
safety check
```
