"""Health check endpoint."""
from fastapi import APIRouter, Depends

from ..models import HealthResponse
from ..dependencies import get_settings
from ...config import Settings

router = APIRouter(tags=["health"])


@router.get("/", response_model=HealthResponse)
@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings)):
    """
    Health check endpoint.

    Returns the status of the service and its components.
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        services={
            "llm": "ready",
            "embeddings": "ready",
            "vectorstore": "ready",
            "memory": "ready",
            "ocr": "ready",
        },
    )
