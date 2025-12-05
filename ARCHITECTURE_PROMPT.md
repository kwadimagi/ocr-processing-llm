# Architecture Generation Prompts for Adamani AI RAG

This document contains prompts and code for generating various architecture diagrams for the Adamani AI RAG system.

---

## 🎨 AI Image Generator Prompt (For ChatGPT, Midjourney, DALL-E)

Use this prompt with AI image generators to create visual architecture diagrams:

```
Create a professional, detailed system architecture diagram for an enterprise AI RAG (Retrieval-Augmented Generation) application with the following specifications:

STYLE:
- Clean, modern technical diagram
- Use rectangular boxes for services/components
- Use cylindrical shapes for databases
- Use cloud shapes for external APIs
- Color coding: Blue for frontend, Green for backend services, Orange for databases, Purple for AI/ML components
- Include arrows showing data flow with labels
- Professional font, high contrast, white background

LAYERS (Top to Bottom):

1. CLIENT LAYER:
   - Next.js Frontend (React 19, TypeScript, Tailwind CSS)
   - Components: ChatInterface, FileUploader, AuthContext
   - Technologies: SSE Client, Fetch API

2. API GATEWAY LAYER:
   - FastAPI Backend (Port 8000)
   - Routes: /auth, /chat, /chat/stream, /documents, /health
   - Features: JWT Auth, CORS, Background Tasks

3. SERVICE LAYER:
   - RAG Service (Query & Stream methods)
   - Document Service (Upload & Processing)
   - LLM Client (Multi-provider: Ollama, OpenAI, Anthropic)
   - Memory Manager (Conversation history)
   - Vector Store Manager (Embeddings & Search)

4. AI/ML LAYER:
   - LLM Providers (shown as external clouds):
     * Ollama (Local)
     * OpenAI GPT-4
     * Anthropic Claude
   - Embedding Model: Sentence-Transformers (all-MiniLM-L6-v2)

5. DATA LAYER:
   - PostgreSQL Database (Users, Organizations, Documents metadata)
   - ChromaDB Vector Store (Document embeddings)
   - File Storage (Uploads, Processed files)

DATA FLOWS:
1. Document Upload: Client → API → Document Service → OCR/PDF Parser → Chunking → Embeddings → ChromaDB
2. Query Flow: Client → API → RAG Service → Vector Search → LLM → Stream Response → Client
3. Auth Flow: Client → API → PostgreSQL → JWT Token → Client

KEY FEATURES TO HIGHLIGHT:
- Real-time streaming (SSE)
- Multi-tenant architecture
- OCR processing (Tesseract)
- Vector similarity search
- JWT authentication
- Async processing

Add labels for: "Production-Grade RAG System", "Real-Time Streaming", "Multi-Tenant", "Enterprise Authentication"
```

---

## 📐 Mermaid Diagram Code

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        A[Next.js Frontend<br/>React 19 + TypeScript]
        A1[ChatInterface Component]
        A2[FileUploader Component]
        A3[Auth Context]
        A --> A1
        A --> A2
        A --> A3
    end

    subgraph "API Gateway"
        B[FastAPI Backend<br/>Port 8000]
        B1[Auth Routes<br/>/auth/register, /auth/login]
        B2[Chat Routes<br/>/chat, /chat/stream]
        B3[Document Routes<br/>/documents/upload]
        B4[Health Check<br/>/health]
        B --> B1
        B --> B2
        B --> B3
        B --> B4
    end

    subgraph "Service Layer"
        C[RAG Service]
        C1[query method]
        C2[query_stream method]
        C --> C1
        C --> C2

        D[Document Service]
        D1[Upload Handler]
        D2[PDF Parser]
        D3[OCR Engine]
        D --> D1
        D --> D2
        D --> D3

        E[LLM Client]
        E1[Ollama Integration]
        E2[OpenAI Integration]
        E3[Anthropic Integration]
        E --> E1
        E --> E2
        E --> E3

        F[Memory Manager]
        G[Vector Store Manager]
    end

    subgraph "AI/ML Components"
        H[Embedding Model<br/>sentence-transformers<br/>all-MiniLM-L6-v2]
        I1{{Ollama<br/>Local LLM}}
        I2{{OpenAI<br/>GPT-4}}
        I3{{Anthropic<br/>Claude}}
    end

    subgraph "Data Layer"
        J[(PostgreSQL<br/>Users, Orgs, Docs)]
        K[(ChromaDB<br/>Vector Store)]
        L[File Storage<br/>Uploads & Processed]
    end

    %% Client to API
    A -->|HTTPS/SSE| B

    %% API to Services
    B1 -.->|Auth| J
    B2 -->|Query| C
    B3 -->|Upload| D

    %% Service Interactions
    C -->|Retrieve| G
    C -->|Generate| E
    C -->|History| F
    D -->|Process| H
    D -->|Store| L
    G -->|Search| K

    %% AI/ML Connections
    E -->|LLM Call| I1
    E -->|LLM Call| I2
    E -->|LLM Call| I3
    H -->|Embeddings| K

    %% Data Persistence
    F -.->|Session Data| J
    D -.->|Metadata| J

    style A fill:#3498db,color:#fff
    style B fill:#2ecc71,color:#fff
    style C fill:#2ecc71,color:#fff
    style D fill:#2ecc71,color:#fff
    style E fill:#2ecc71,color:#fff
    style F fill:#2ecc71,color:#fff
    style G fill:#2ecc71,color:#fff
    style H fill:#9b59b6,color:#fff
    style I1 fill:#e74c3c,color:#fff
    style I2 fill:#e74c3c,color:#fff
    style I3 fill:#e74c3c,color:#fff
    style J fill:#f39c12,color:#fff
    style K fill:#f39c12,color:#fff
    style L fill:#f39c12,color:#fff
```

### Data Flow: Document Upload

```mermaid
sequenceDiagram
    actor User
    participant Frontend as Next.js Frontend
    participant API as FastAPI
    participant DocService as Document Service
    participant OCR as Tesseract OCR
    participant Chunker as Text Chunker
    participant Embedder as Embedding Model
    participant VectorDB as ChromaDB
    participant DB as PostgreSQL

    User->>Frontend: Upload PDF/Image
    Frontend->>API: POST /documents/upload
    API->>DocService: Process file

    alt PDF Document
        DocService->>DocService: Extract text (PyPDF)
    else Scanned/Image
        DocService->>OCR: Extract text (Tesseract)
        OCR-->>DocService: Extracted text
    end

    DocService->>Chunker: Split into chunks
    Chunker-->>DocService: Text chunks (1000 tokens)

    DocService->>Embedder: Generate embeddings
    Embedder-->>DocService: 384-dim vectors

    DocService->>VectorDB: Store vectors + metadata
    VectorDB-->>DocService: Success

    DocService->>DB: Store document metadata
    DB-->>DocService: Success

    DocService-->>API: Processing complete
    API-->>Frontend: 200 OK (chunks created)
    Frontend-->>User: Upload successful
```

### Data Flow: Query with Streaming

```mermaid
sequenceDiagram
    actor User
    participant Frontend as Next.js Frontend
    participant API as FastAPI
    participant RAG as RAG Service
    participant VectorDB as ChromaDB
    participant Memory as Memory Manager
    participant LLM as LLM Provider

    User->>Frontend: Ask question
    Frontend->>API: POST /chat/stream
    API->>RAG: query_stream(question)

    RAG->>VectorDB: Similarity search
    VectorDB-->>RAG: Top-5 relevant chunks

    RAG->>Frontend: SSE: {type: "sources"}
    Frontend-->>User: Display sources

    RAG->>Memory: Get chat history
    Memory-->>RAG: Previous messages

    RAG->>RAG: Build prompt (context + history + question)
    RAG->>LLM: astream(prompt)

    loop Token Streaming
        LLM-->>RAG: Token chunk
        RAG->>Frontend: SSE: {type: "token"}
        Frontend-->>User: Display token (real-time)
    end

    LLM-->>RAG: Stream complete
    RAG->>Memory: Save conversation
    RAG->>Frontend: SSE: {type: "done"}
    Frontend-->>User: Complete answer shown
```

### Authentication Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend as Next.js Frontend
    participant API as FastAPI
    participant Auth as Auth Manager
    participant DB as PostgreSQL

    User->>Frontend: Enter credentials
    Frontend->>API: POST /auth/login
    API->>Auth: Verify credentials
    Auth->>DB: Query user by email
    DB-->>Auth: User record
    Auth->>Auth: Verify password (Argon2)

    alt Valid Credentials
        Auth->>Auth: Generate JWT token
        Auth-->>API: Token + user data
        API-->>Frontend: 200 OK {access_token}
        Frontend->>Frontend: Store token (localStorage)
        Frontend-->>User: Redirect to dashboard
    else Invalid Credentials
        Auth-->>API: Authentication failed
        API-->>Frontend: 401 Unauthorized
        Frontend-->>User: Show error message
    end

    Note over Frontend,API: Subsequent Requests
    Frontend->>API: Request with Authorization header
    API->>Auth: Validate JWT token
    Auth-->>API: User context
    API->>API: Process request
    API-->>Frontend: Response
```

### Multi-Tenant Architecture

```mermaid
graph TB
    subgraph "Organization A"
        UA[Users A1, A2, A3]
        DA[Documents A]
        VA[Vector Data A]
    end

    subgraph "Organization B"
        UB[Users B1, B2]
        DB[Documents B]
        VB[Vector Data B]
    end

    subgraph "Application Layer"
        API[FastAPI with Auth]
        Filter[Organization Filter]
    end

    subgraph "Data Layer"
        PG[(PostgreSQL)]
        Chroma[(ChromaDB)]
    end

    UA -->|Auth Token| API
    UB -->|Auth Token| API
    API --> Filter

    Filter -->|org_id = A| PG
    Filter -->|org_id = B| PG
    Filter -->|metadata filter| Chroma

    PG --> DA
    PG --> DB
    Chroma --> VA
    Chroma --> VB

    style UA fill:#3498db,color:#fff
    style UB fill:#e74c3c,color:#fff
    style DA fill:#3498db,color:#fff
    style DB fill:#e74c3c,color:#fff
    style VA fill:#3498db,color:#fff
    style VB fill:#e74c3c,color:#fff
    style Filter fill:#f39c12,color:#fff
```

---

## 🔧 Component Breakdown for Manual Diagramming

Use this structured breakdown for tools like draw.io, Lucidchart, or Visio:

### Layer 1: Client Layer (Blue)
```
┌─────────────────────────────────────────┐
│      Next.js Frontend (Port 3000)       │
│  ┌──────────────────────────────────┐   │
│  │  React Components:               │   │
│  │  • ChatInterface.tsx             │   │
│  │  • FileUploader.tsx              │   │
│  │  • ProtectedRoute.tsx            │   │
│  │  • AuthContext.tsx               │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  Services:                       │   │
│  │  • api.ts (API client)           │   │
│  │  • sendChatMessageStream()       │   │
│  │  • uploadDocument()              │   │
│  └──────────────────────────────────┘   │
│                                          │
│  Tech: React 19, TypeScript, Tailwind   │
└─────────────────────────────────────────┘
           │
           │ HTTPS + SSE
           ▼
```

### Layer 2: API Gateway (Green)
```
┌─────────────────────────────────────────┐
│      FastAPI Backend (Port 8000)        │
│  ┌──────────────────────────────────┐   │
│  │  Routes:                         │   │
│  │  • /auth (register, login)       │   │
│  │  • /chat (query, stream, status) │   │
│  │  • /documents (upload, clear)    │   │
│  │  • /health                       │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  Middleware:                     │   │
│  │  • CORS Configuration            │   │
│  │  • JWT Authentication            │   │
│  │  • Background Tasks              │   │
│  └──────────────────────────────────┘   │
│                                          │
│  Tech: FastAPI 0.115, Uvicorn, Pydantic │
└─────────────────────────────────────────┘
           │
           │ Dependency Injection
           ▼
```

### Layer 3: Service Layer (Green)
```
┌─────────────────────────────────────────┐
│           RAG Service                    │
│  • query(question, session_id, k)       │
│  • query_stream(question, ...)          │
│  • _format_docs(docs)                   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        Document Service                  │
│  • process_document(file, use_ocr)      │
│  • extract_text_from_pdf()              │
│  • extract_text_with_ocr()              │
│  • chunk_text(text)                     │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│           LLM Client                     │
│  • get_client() -> BaseLanguageModel    │
│  • Providers:                           │
│    - Ollama (local)                     │
│    - OpenAI (GPT-4, GPT-4-mini)         │
│    - Anthropic (Claude 3.5)             │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        Memory Manager                    │
│  • get_history(session_id)              │
│  • add_user_message(session, msg)       │
│  • add_ai_message(session, msg)         │
│  • clear_history(session_id)            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│      Vector Store Manager                │
│  • add_documents(docs)                  │
│  • similarity_search(query, k)          │
│  • clear()                              │
└─────────────────────────────────────────┘
```

### Layer 4: AI/ML Components (Purple)
```
┌─────────────────────────────────────────┐
│      Embedding Model                     │
│  Model: all-MiniLM-L6-v2                │
│  Dimensions: 384                        │
│  Provider: HuggingFace                  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│      LLM Providers (External)            │
│  ┌──────────────────────────────────┐   │
│  │  Ollama (Local)                  │   │
│  │  Models: llama3, mistral         │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  OpenAI API                      │   │
│  │  Models: gpt-4, gpt-4o-mini      │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  Anthropic API                   │   │
│  │  Models: claude-3-5-sonnet       │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│      OCR Engine                          │
│  Engine: Tesseract                      │
│  Languages: eng                         │
│  Support: pdf2image, Pillow             │
└─────────────────────────────────────────┘
```

### Layer 5: Data Layer (Orange)
```
┌─────────────────────────────────────────┐
│      PostgreSQL Database                 │
│  ┌──────────────────────────────────┐   │
│  │  Tables:                         │   │
│  │  • users (id, email, password)   │   │
│  │  • organizations (id, name)      │   │
│  │  • organization_members          │   │
│  │  • documents (id, org_id, file)  │   │
│  └──────────────────────────────────┘   │
│  ORM: SQLAlchemy (async)                │
│  Driver: asyncpg                        │
│  Migrations: Alembic                    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│      ChromaDB Vector Store               │
│  • Storage: Persistent                  │
│  • Collections: documents               │
│  • Vectors: 384-dimensional             │
│  • Metadata: filename, page, org_id     │
│  • Index: HNSW                          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│      File Storage                        │
│  • ./data/uploads/                      │
│  • ./data/processed/                    │
│  • ./data/vectorstore/                  │
└─────────────────────────────────────────┘
```

---

## 🎯 Technology Stack Diagram

```
Frontend Stack:
├── Next.js 15.1.3
├── React 19.0.0
├── TypeScript 5
├── Tailwind CSS 3.4.1
└── Lucide React 0.469.0

Backend Stack:
├── FastAPI 0.115.0
├── Python 3.10+
├── Uvicorn (ASGI server)
└── Poetry (dependency management)

AI/ML Stack:
├── LangChain 0.3.0
│   ├── langchain-core
│   ├── langchain-community
│   ├── langchain-ollama
│   ├── langchain-openai
│   └── langchain-anthropic
├── Sentence-Transformers 3.3.0
└── ChromaDB 0.5.0

Database Stack:
├── PostgreSQL 14+
├── SQLAlchemy 2.0+ (async)
├── Alembic 1.13.0
└── asyncpg 0.29.0

Authentication:
├── FastAPI-Users 12.0.0
├── Python-JOSE (JWT)
├── Passlib + Argon2
└── Email-validator

Document Processing:
├── PyPDF 5.1.0
├── Pytesseract 0.3.0
├── pdf2image 1.17.0
└── Pillow 11.0.0

Utilities:
├── Loguru 0.7.0
├── Pydantic 2.9.0
├── python-dotenv 1.0.0
└── aiofiles 24.1.0
```

---

## 📊 Deployment Architecture

```
┌────────────────────────────────────────────────────┐
│              Render Cloud Platform                 │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │  Frontend Service                            │ │
│  │  • Next.js Application                       │ │
│  │  • URL: adamani-ai-rag-frontend.onrender.com│ │
│  │  • Auto-deploy from Git                      │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │  Backend Service                             │ │
│  │  • FastAPI Application                       │ │
│  │  • URL: adamani-ai-rag-backend.onrender.com │ │
│  │  • Auto-deploy from Git                      │ │
│  │  • Environment Variables Configured          │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │  PostgreSQL Database                         │ │
│  │  • Managed PostgreSQL Instance               │ │
│  │  • Automatic Backups                         │ │
│  │  • SSL Connections                           │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
└────────────────────────────────────────────────────┘

External Services:
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   OpenAI     │  │  Anthropic   │  │   GitHub     │
│   API        │  │   API        │  │  Repository  │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 🔄 Request Flow Examples

### Example 1: User Registration
```
1. User fills form → Frontend
2. Frontend → POST /auth/register → Backend
3. Backend → Validate data (Pydantic)
4. Backend → Hash password (Argon2)
5. Backend → Create user in PostgreSQL
6. Backend → Auto-create organization
7. Backend → Add user to organization
8. Backend → Return user object
9. Frontend → Auto-login
10. Frontend → Redirect to dashboard
```

### Example 2: Document Upload with OCR
```
1. User selects PDF → Frontend
2. Frontend → POST /documents/upload?use_ocr=true → Backend
3. Backend → Validate file type
4. Backend → Save to ./data/uploads/
5. Backend → Check if scanned (OCR needed)
6. Backend → pdf2image → Convert pages
7. Backend → Tesseract → Extract text per page
8. Backend → Combine extracted text
9. Backend → RecursiveCharacterTextSplitter → Chunk (1000 tokens, 200 overlap)
10. Backend → Sentence-Transformers → Generate embeddings (384-dim)
11. Backend → ChromaDB → Store vectors + metadata
12. Backend → PostgreSQL → Store document metadata
13. Backend → Return success + chunk count
14. Frontend → Show success notification
```

### Example 3: Streaming Query
```
1. User types question → Frontend
2. Frontend → POST /chat/stream → Backend
3. Backend → RAG Service → query_stream()
4. RAG → ChromaDB → similarity_search(question embedding)
5. ChromaDB → Return top-5 relevant chunks
6. RAG → SSE: {type: "sources"} → Frontend
7. Frontend → Display sources in UI
8. RAG → Memory Manager → get chat history
9. RAG → Build prompt (system + context + history + question)
10. RAG → LLM.astream(prompt) → Start streaming
11. LLM → Token 1 → RAG → SSE: {type: "token", token: "The"}
12. Frontend → Display "The" + cursor
13. LLM → Token 2 → RAG → SSE: {type: "token", token: " answer"}
14. Frontend → Display "The answer" + cursor
15. ... (continue for all tokens)
16. LLM → Complete → RAG → Memory → Save conversation
17. RAG → SSE: {type: "done"} → Frontend
18. Frontend → Finalize message, remove cursor
```

---

## 🎨 Color Scheme for Diagrams

```
Client Layer:     #3498db (Blue)
API Gateway:      #2ecc71 (Green)
Services:         #2ecc71 (Green)
AI/ML:            #9b59b6 (Purple)
External APIs:    #e74c3c (Red)
Databases:        #f39c12 (Orange)
File Storage:     #f39c12 (Orange)
Authentication:   #e67e22 (Dark Orange)
Arrows (Data):    #34495e (Dark Gray)
Arrows (Control): #95a5a6 (Light Gray)
```

---

## 📝 Usage Instructions

### For AI Image Generators:
1. Copy the "AI Image Generator Prompt" section
2. Paste into ChatGPT, Claude, or Midjourney
3. Request: "Generate this as a professional architecture diagram"

### For Mermaid Diagrams:
1. Copy any Mermaid code block
2. Paste into:
   - GitHub Markdown (renders automatically)
   - Mermaid Live Editor (https://mermaid.live)
   - VS Code (with Mermaid extension)
   - Notion, Obsidian, or other Mermaid-compatible tools

### For Manual Diagramming:
1. Use the "Component Breakdown" section
2. Import into draw.io, Lucidchart, or Visio
3. Follow the layer structure and color scheme
4. Add arrows according to data flow examples

---

## 🚀 Diagram Export Formats

### Recommended Formats:
- **Presentations**: PNG (high-res, 300 DPI)
- **Documentation**: SVG (scalable, small file size)
- **Reports**: PDF (professional, print-ready)
- **Web**: WebP (optimized, fast loading)

### Mermaid Export:
```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Generate PNG
mmdc -i diagram.mmd -o diagram.png -b transparent

# Generate SVG
mmdc -i diagram.mmd -o diagram.svg

# Generate PDF
mmdc -i diagram.mmd -o diagram.pdf
```

---

**Last Updated**: December 2024
**Version**: 1.0
**Author**: Adamani AI RAG Project Team
