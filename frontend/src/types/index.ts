export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatRequest {
  question: string;
  session_id: string;
  k?: number;
}

export interface SourceDocument {
  content: string;
  metadata: {
    source?: string;
    filename?: string;
    page?: number;
    [key: string]: any;
  };
}

export interface ChatResponse {
  answer: string;
  sources: SourceDocument[];
  session_id: string;
}

export interface DocumentResponse {
  status: string;
  documents_added: number;
  chunks_created: number;
  message: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  services: {
    llm: string;
    embeddings: string;
    vectorstore: string;
    memory: string;
    ocr: string;
  };
}
