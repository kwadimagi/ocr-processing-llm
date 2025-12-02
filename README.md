# Adamani AI RAG - Responsible AI Governance Platform

A modular AI automation backend that provides local LLM-powered RAG (Retrieval-Augmented Generation), memory-enabled conversational AI, and OCR-based document processing for businesses and institutions with a strong focus on responsible AI and governance.

## Overview

This platform enables organizations to process invoices, PDFs, and documents using AI while maintaining strict data privacy, transparency, and ethical AI principles. All processing happens locally without sending data to external APIs.

## Tech Stack

### Backend
- **Framework**: FastAPI 0.115.x
- **Language**: Python 3.11
- **Dependency Management**: Poetry 2.2.x
- **Logging**: Loguru 0.7.x (beautiful colored logs with emojis)
- **Configuration**: Pydantic Settings 2.6.x
- **ASGI Server**: Uvicorn 0.32.x

### AI/ML Components
- **LLM Engine**: Ollama (local LLM server)
  - Model: Llama 3 (8B parameters)
  - Base URL: http://localhost:11434
  - Temperature: 0.1 (for consistency)
- **Orchestration Framework**: LangChain 0.2.x
  - `langchain-core`: Core abstractions
  - `langchain-community`: Community integrations
  - `langchain-ollama`: Ollama integration
  - `langchain-chroma`: ChromaDB integration
  - `langchain-huggingface`: HuggingFace embeddings
- **Embeddings**: Sentence Transformers 3.3.x
  - Model: `all-MiniLM-L6-v2` (384-dimensional)
  - Fast, lightweight, and accurate
- **Vector Store**: ChromaDB 0.5.x (default) / FAISS 1.9.x
  - ChromaDB: Persistent, production-ready
  - FAISS: In-memory, faster for development

### Document Processing
- **PDF Processing**: PyPDF 5.1.x, pdf2image 1.17.x
- **OCR Engine**: Tesseract OCR (via pytesseract 0.3.x)
  - Languages: English (configurable)
  - Auto-detection of scanned PDFs
- **Image Processing**: Pillow 11.0.x
- **Supported Formats**: PDF, PNG, JPG, JPEG, TIFF, BMP

### Frontend
- **Framework**: Next.js 15.1.3 (React 19)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS 3.4.x
- **UI Components**:
  - Lucide React 0.469.x (icons)
  - Custom components with CVA (Class Variance Authority)
- **Build Output**: Standalone mode for Docker optimization

### Data & Storage
- **Vector Database**: ChromaDB (persistent on disk)
- **File Storage**: Local filesystem (`./data/`)
  - Uploads: `./data/uploads/`
  - Processed: `./data/processed/`
  - Vector Store: `./data/vectorstore/`
- **Session Management**: In-memory (scalable to Redis/DB)

### DevOps & Infrastructure
- **Containerization**: Docker + Docker Compose
- **Base Images**:
  - Backend: `python:3.11-slim`
  - Frontend: `node:20-alpine`
  - LLM: `ollama/ollama:latest`
- **Orchestration**: Docker Compose 3.8
- **Health Checks**: Built-in for all services
- **Port Mapping**:
  - Frontend: 3000
  - Backend: 8080
  - Ollama: 11434

### RAG Configuration
- **Chunk Size**: 1000 tokens
- **Chunk Overlap**: 200 tokens
- **Retrieval Top-K**: 5 most relevant chunks
- **Context Window**: 4096 tokens (Llama 3)

## Responsible AI Principles

### 1. Data Privacy & Security
- **Local Processing**: All data processing happens on-premises
- **No External APIs**: No data sent to third-party services
- **Data Isolation**: Session-based separation of user data
- **Secure Storage**: Files stored locally with proper permissions
- **GDPR Compliant**: Full control over data lifecycle

### 2. Transparency & Explainability
- **Source Attribution**: Every AI response includes source documents
- **Audit Logging**: Comprehensive logging with Loguru
- **Model Information**: Clear indication of AI model used (Llama 3)
- **Confidence Indication**: Retrieval scores available for verification
- **Human Oversight**: System designed for human-in-the-loop workflows

### 3. Fairness & Bias Mitigation
- **Open Source Models**: Using openly auditable Llama 3
- **Multilingual Support**: Configurable OCR languages
- **No Training on User Data**: Model remains static, no fine-tuning
- **Diverse Testing**: Designed for various document types and formats

### 4. Accountability & Governance
- **Version Control**: All components versioned and tracked
- **Change Management**: Git-based workflow for all changes
- **Error Handling**: Comprehensive error logging and reporting
- **Performance Monitoring**: Built-in health checks and metrics
- **Incident Response**: Clear logging for debugging and auditing

### 5. Robustness & Safety
- **Input Validation**: File type and size validation
- **Error Recovery**: Graceful degradation on failures
- **Rate Limiting**: Configurable (can be added)
- **Resource Management**: Docker-based resource constraints
- **Fallback Mechanisms**: OCR fallback for scanned PDFs

## Governance Framework

### Data Governance

#### Data Classification
- **Public**: API documentation, health endpoints
- **Internal**: System logs, configuration
- **Confidential**: Uploaded documents, embeddings
- **Restricted**: User sessions, conversation history

#### Data Lifecycle
1. **Collection**: File upload with validation
2. **Processing**: OCR and text extraction
3. **Storage**: Encrypted at rest (Docker volumes)
4. **Usage**: RAG retrieval for Q&A
5. **Retention**: Configurable (manual cleanup)
6. **Deletion**: Clear endpoints for data removal

#### Data Access Control
- **Authentication**: To be implemented (OAuth2/JWT recommended)
- **Authorization**: Role-based access control (RBAC) ready
- **Session Management**: UUID-based session isolation
- **Audit Trail**: All access logged via Loguru

### Model Governance

#### Model Selection Criteria
- **Open Source**: Llama 3 is openly available and auditable
- **Performance**: 8B parameters, suitable for document Q&A
- **Safety**: Meta's safety guidelines followed
- **Licensing**: Commercial use permitted

#### Model Monitoring
- **Response Quality**: Source attribution for verification
- **Latency**: Health checks and timeout monitoring
- **Resource Usage**: Docker stats and logging
- **Error Rates**: Comprehensive error logging

#### Model Updates
- **Version Control**: Model versions tracked in config
- **Testing**: Sandbox environment for testing new models
- **Rollback**: Easy rollback via Docker images
- **Documentation**: Change logs for all updates

### Operational Governance

#### Service Level Agreements (SLAs)
- **Availability**: 99.9% uptime target
- **Response Time**: <5s for document upload
- **Processing Time**: <30s for standard PDFs
- **Query Response**: <10s for RAG queries

#### Incident Management
1. **Detection**: Health checks every 10-30s
2. **Logging**: All errors logged with context
3. **Alerting**: Docker logs accessible via `docker compose logs`
4. **Resolution**: Documented troubleshooting in guides
5. **Post-Mortem**: Git commit messages track fixes

#### Change Management
- **Version Control**: Git for all code changes
- **Code Review**: PR-based workflow (recommended)
- **Testing**: Health endpoints for smoke testing
- **Deployment**: Docker Compose for consistent deploys
- **Rollback**: Git revert + rebuild Docker images

### Compliance & Ethics

#### Regulatory Compliance
- **GDPR**: Data minimization, right to deletion
- **CCPA**: Data access and portability
- **SOC 2**: Audit logging, access controls
- **ISO 27001**: Information security management

#### Ethical AI Principles
- **Beneficence**: System designed to help, not harm
- **Non-maleficence**: Safety checks and validations
- **Autonomy**: User control over data and queries
- **Justice**: Fair access, no discrimination
- **Explicability**: Transparent AI decision-making

#### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Data breach | Low | High | Local processing, no external APIs |
| Model hallucination | Medium | Medium | Source attribution, human review |
| OCR errors | Medium | Low | Confidence scores, manual verification |
| Service downtime | Low | Medium | Health checks, Docker restart policies |
| Bias in responses | Low | Medium | Open-source model, diverse testing |
| Resource exhaustion | Medium | Medium | Docker limits, monitoring |

## Architecture

```
                                                             
   Frontend          ¶   Backend API       ¶     Ollama      
  (Next.js)              (FastAPI)            (Llama 3)      
  Port 3000              Port 8080            Port 11434     
                                                             
                               
                               ¼
                                         
                           ChromaDB      
                         (Vector Store)  
                           Embeddings    
                                         
```

### Modular Architecture

```
adamani_ai_rag/
   src/adamani_ai_rag/
      core/              # Core AI components
         llm.py         # LLM client management
         embeddings.py  # Embedding model
         vectorstore.py # Vector DB manager
         memory.py      # Conversation memory
         ocr.py         # OCR processing
         pdf_processor.py # PDF handling
      services/          # Business logic
         rag_service.py # RAG orchestration
         document_service.py # Document processing
      api/               # REST API
         app.py         # FastAPI application
         routes/        # API endpoints
         models/        # Pydantic models
         dependencies.py # DI singletons
      config/            # Configuration
         settings.py    # Environment settings
      utils/             # Utilities
          logger.py      # Loguru setup
   frontend/              # Next.js frontend
       src/
          app/           # Next.js pages
          components/    # React components
          lib/           # API client
          types/         # TypeScript types
       public/            # Static assets
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- 8GB+ RAM
- 10GB+ disk space

### 1. Clone Repository
```bash
git clone https://github.com/silsgah/ocr_llg_rag_responsible_AI_Governance.git
cd ocr_llg_rag_responsible_AI_Governance
```

### 2. Start All Services
```bash
docker-compose up -d
```

### 3. Pull LLM Model
```bash
docker exec -it adamani_ai_rag-ollama-1 ollama pull llama3
```

### 4. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs

## Usage

### Upload Documents
1. Navigate to http://localhost:3000
2. Drag & drop PDF or image files
3. Toggle OCR for scanned documents
4. Wait for processing completion

### Ask Questions
1. Type your question in the chat interface
2. Get AI-powered answers with source attribution
3. View source documents for verification
4. Clear history with the trash button

### API Usage
```bash
# Upload document
curl -X POST http://localhost:8080/documents/upload \
  -F "file=@invoice.pdf" \
  -F "use_ocr=true"

# Ask question
curl -X POST http://localhost:8080/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the total amount?",
    "session_id": "user_123"
  }'

# Clear conversation history
curl -X DELETE http://localhost:8080/chat/memory/user_123
```

## Configuration

### Backend Environment Variables
```bash
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
LLM_TEMPERATURE=0.1

# Vector Store
VECTOR_STORE_TYPE=chroma  # or faiss
VECTORDB_PATH=./data/vectorstore

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVAL_TOP_K=5

# OCR Configuration
OCR_LANGUAGES=eng

# API Configuration
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

### Frontend Environment Variables
```bash
NEXT_PUBLIC_API_URL=http://localhost:8080
```

## Development

### Backend Development
```bash
# Install dependencies
poetry install

# Start Ollama
ollama serve

# Pull model
ollama pull llama3

# Start backend
uvicorn src.adamani_ai_rag.api.app:app --reload --host 0.0.0.0 --port 8080
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## Testing

### Health Checks
```bash
# Backend
curl http://localhost:8080/health

# Ollama
curl http://localhost:11434/api/tags

# Frontend
curl http://localhost:3000
```

### Example Test Documents
Upload sample invoices with:
- Customer information
- Line items
- Totals and taxes
- Dates and invoice numbers

Ask questions like:
- "What is the total amount?"
- "Who is the customer?"
- "What items were purchased?"
- "What is the invoice date?"

## Security Best Practices

### Production Deployment
- [ ] Enable HTTPS (TLS/SSL certificates)
- [ ] Add authentication (OAuth2/JWT)
- [ ] Implement rate limiting
- [ ] Set up monitoring and alerting
- [ ] Configure backup and recovery
- [ ] Enable firewall rules
- [ ] Use secrets management
- [ ] Implement audit logging
- [ ] Set resource limits
- [ ] Regular security updates

### Data Protection
- [ ] Encrypt data at rest
- [ ] Encrypt data in transit
- [ ] Implement data retention policies
- [ ] Set up access controls
- [ ] Regular security audits
- [ ] Incident response plan
- [ ] Data breach notification procedures

## Monitoring & Observability

### Logs
```bash
# View all logs
docker-compose logs -f

# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend

# Ollama logs
docker-compose logs -f ollama
```

### Metrics
- Health endpoint: `/health`
- Docker stats: `docker stats`
- Ollama models: `docker exec ollama ollama list`

## Troubleshooting

See [FULL_STACK_GUIDE.md](FULL_STACK_GUIDE.md) for detailed troubleshooting steps.

## Documentation

- [Project Structure](PROJECT_STRUCTURE.md) - Detailed architecture
- [Dependencies](DEPENDENCIES.md) - Package versions and rationale
- [Full Stack Guide](FULL_STACK_GUIDE.md) - Complete deployment guide
- [Quick Start](QUICKSTART.md) - Fast setup instructions
- [MVP Ready](MVP_READY.md) - API reference and integration guide

## Contributing

### Code Standards
- Python: PEP 8, type hints required
- TypeScript: Strict mode enabled
- Git: Conventional commits
- Testing: Health checks required
- Documentation: README updates with changes

### Pull Request Process
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

MIT License - see LICENSE file for details

## Responsible AI Statement

This project is committed to responsible AI development and deployment:

- **Transparency**: Open source, auditable code and models
- **Privacy**: Local processing, no data leaves your infrastructure
- **Fairness**: Open-source models, diverse testing
- **Accountability**: Comprehensive logging and audit trails
- **Safety**: Multiple validation layers and human oversight
- **Ethics**: Designed with ethical AI principles at the core

## Support

- **Issues**: GitHub Issues
- **Documentation**: See docs/ folder
- **Community**: Discussions tab

## Acknowledgments

- Meta AI for Llama 3
- Ollama for local LLM serving
- LangChain for RAG framework
- ChromaDB for vector storage
- Tesseract for OCR capabilities
- FastAPI and Next.js teams

---

**Built with responsibility, powered by AI, secured by design.**
