"""Chat and RAG endpoints."""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
import asyncio
import json
from typing import Dict, Any

from ...services.rag_service import RAGService
from ...core.memory import MemoryManager
from ..models import ChatRequest, ChatResponse
from ..dependencies import get_rag_service, get_memory_manager
from ...utils.logger import get_logger

logger = get_logger()
router = APIRouter(prefix="/chat", tags=["chat"])

# Store for async query results (temporary - use Redis/DB in production)
_query_results: Dict[str, Any] = {}


def process_query_background(question: str, session_id: str, k: int, rag_service: RAGService, request_id: str):
    """Background task to process RAG query."""
    try:
        result = rag_service.query(
            question=question,
            session_id=session_id,
            k=k,
        )
        # Store result for retrieval
        _query_results[request_id] = {
            "status": "completed",
            "result": result
        }
        logger.success(f"✅ Query processed: {question[:50]}...")
    except Exception as e:
        logger.error(f"❌ Background query error: {str(e)}")
        _query_results[request_id] = {
            "status": "error",
            "error": str(e)
        }


@router.post("/")
async def chat(
    background_tasks: BackgroundTasks,
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    Chat with AI using RAG (Retrieval-Augmented Generation).

    This endpoint retrieves relevant documents and generates contextual responses.
    """
    try:
        # Generate unique request ID
        import uuid
        request_id = str(uuid.uuid4())
        
        # Queue background task
        background_tasks.add_task(
            process_query_background,
            request.question,
            request.session_id,
            request.k,
            rag_service,
            request_id
        )
        
        # Return immediately with request ID
        return JSONResponse(
            status_code=202,  # Accepted
            content={
                "status": "processing",
                "request_id": request_id,
                "message": "Query is being processed. Use /chat/status/{request_id} to check progress."
            }
        )

    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Failed to queue query"
            }
        )


@router.get("/status/{request_id}")
async def get_query_status(request_id: str):
    """Check status of a background query."""
    if request_id not in _query_results:
        return JSONResponse(
            status_code=200,
            content={
                "status": "processing",
                "message": "Query is still being processed..."
            }
        )
    
    result_data = _query_results[request_id]
    
    if result_data["status"] == "completed":
        result = result_data["result"]
        # Clean up after retrieval
        del _query_results[request_id]
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "completed",
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "session_id": result.get("session_id", "")
            }
        )
    else:
        # Error occurred
        error = result_data.get("error", "Unknown error")
        del _query_results[request_id]
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": error
            }
        )


@router.delete("/memory/{session_id}")
async def clear_memory(
    session_id: str,
    memory_manager: MemoryManager = Depends(get_memory_manager),
):
    """Clear chat history for a specific session."""
    try:
        memory_manager.clear_history(session_id)
        return {"status": "success", "message": f"Cleared memory for session: {session_id}"}

    except Exception as e:
        logger.error(f"Clear memory error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/memory")
async def clear_all_memory(
    memory_manager: MemoryManager = Depends(get_memory_manager),
):
    """Clear all chat histories."""
    try:
        count = memory_manager.get_session_count()
        memory_manager.clear_all()
        return {
            "status": "success",
            "message": f"Cleared {count} session histories",
        }

    except Exception as e:
        logger.error(f"Clear all memory error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    Chat with AI using RAG with streaming response.

    This endpoint streams the response token by token for a better user experience.
    Uses Server-Sent Events (SSE) format.
    """
    async def event_generator():
        try:
            async for chunk in rag_service.query_stream(
                question=request.question,
                session_id=request.session_id,
                k=request.k,
            ):
                # Format as SSE (Server-Sent Events)
                # Each message is: data: {json}\n\n
                yield f"data: {json.dumps(chunk)}\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            error_data = {
                "type": "error",
                "error": str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )