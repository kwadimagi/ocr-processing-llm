"""Chat and RAG endpoints."""
from fastapi import APIRouter, HTTPException, Depends

from ...services.rag_service import RAGService
from ...core.memory import MemoryManager
from ..models import ChatRequest, ChatResponse
from ..dependencies import get_rag_service, get_memory_manager
from ...utils.logger import get_logger

logger = get_logger()
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    Chat with AI using RAG (Retrieval-Augmented Generation).

    This endpoint retrieves relevant documents and generates contextual responses.
    """
    try:
        result = rag_service.query(
            question=request.question,
            session_id=request.session_id,
            k=request.k,
        )
        return ChatResponse(**result)

    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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
