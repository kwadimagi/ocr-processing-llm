import type {
  ChatRequest,
  ChatResponse,
  DocumentResponse,
  HealthResponse,
  AsyncChatInitResponse,
  ChatStatusResponse,
} from '@/types';

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || 'https://adamani-ai-rag-backend.onrender.com';

class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// Get auth token from localStorage
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
}

// Get auth headers
function getAuthHeaders(): HeadersInit {
  const token = getAuthToken();
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new APIError(
      error.detail || 'An error occurred',
      response.status,
      error
    );
  }
  return response.json();
}

export async function uploadDocument(
  file: File,
  useOCR: boolean = false
): Promise<DocumentResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(
    `${API_BASE}/documents/upload?use_ocr=${useOCR}`,
    {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData,
    }
  );

  return handleResponse<DocumentResponse>(response);
}

// Check the status of a chat request
export async function checkChatStatus(
  requestId: string
): Promise<ChatStatusResponse> {
  const response = await fetch(`${API_BASE}/chat/status/${requestId}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  return handleResponse<ChatStatusResponse>(response);
}

// Send chat message with streaming
export async function sendChatMessageStream(
  request: ChatRequest,
  onToken: (token: string) => void,
  onSources: (sources: any[]) => void,
  onComplete: () => void,
  onError: (error: string) => void
): Promise<void> {
  try {
    const response = await fetch(`${API_BASE}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new APIError('Failed to start streaming', response.status);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new APIError('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      // Decode the chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });

      // Process complete SSE messages (ending with \n\n)
      const messages = buffer.split('\n\n');
      buffer = messages.pop() || ''; // Keep incomplete message in buffer

      for (const message of messages) {
        if (!message.trim() || !message.startsWith('data: ')) continue;

        try {
          // Parse the JSON data after "data: "
          const jsonStr = message.substring(6); // Remove "data: " prefix
          const data = JSON.parse(jsonStr);

          switch (data.type) {
            case 'sources':
              onSources(data.sources || []);
              break;
            case 'token':
              onToken(data.token || '');
              break;
            case 'done':
              onComplete();
              return;
            case 'error':
              onError(data.error || 'Unknown error');
              return;
          }
        } catch (e) {
          console.error('Failed to parse SSE message:', message, e);
        }
      }
    }
  } catch (error: any) {
    onError(error.message || 'Streaming failed');
    throw error;
  }
}

// Send chat message with polling (legacy fallback)
export async function sendChatMessage(
  request: ChatRequest,
  onProgress?: (status: string) => void
): Promise<ChatResponse> {
  // Initiate the chat request
  const initResponse = await fetch(`${API_BASE}/chat/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(request),
  });

  const initData = await handleResponse<AsyncChatInitResponse>(initResponse);
  const requestId = initData.request_id;

  // Poll for status
  const pollInterval = 1000; // Poll every 1 second
  const maxAttempts = 120; // Max 2 minutes
  let attempts = 0;

  while (attempts < maxAttempts) {
    attempts++;

    if (onProgress) {
      onProgress(`Processing... (${attempts}s)`);
    }

    await new Promise(resolve => setTimeout(resolve, pollInterval));

    const statusResponse = await checkChatStatus(requestId);

    if (statusResponse.status === 'completed') {
      return {
        answer: statusResponse.answer!,
        sources: statusResponse.sources || [],
        session_id: statusResponse.session_id!,
      };
    } else if (statusResponse.status === 'error') {
      throw new APIError(statusResponse.message || 'Processing failed');
    }
    // Continue polling if status is 'processing'
  }

  throw new APIError('Request timeout: Processing took too long');
}

export async function addTexts(
  texts: string[],
  metadatas?: Record<string, any>[]
): Promise<DocumentResponse> {
  const response = await fetch(`${API_BASE}/documents/texts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify({ texts, metadatas }),
  });

  return handleResponse<DocumentResponse>(response);
}

export async function clearMemory(sessionId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/chat/memory/${sessionId}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });

  await handleResponse(response);
}

export async function clearKnowledgeBase(): Promise<void> {
  const response = await fetch(`${API_BASE}/documents/clear`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });

  await handleResponse(response);
}

export async function healthCheck(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/health`);
  return handleResponse<HealthResponse>(response);
}
