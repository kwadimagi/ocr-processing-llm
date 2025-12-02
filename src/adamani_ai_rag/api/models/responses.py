"""API response models."""
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class SourceDocument(BaseModel):
    """Source document in response."""

    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")


class ChatResponse(BaseModel):
    """Chat/query response model."""

    answer: str = Field(..., description="AI-generated answer")
    sources: List[SourceDocument] = Field(..., description="Source documents used")
    session_id: str = Field(..., description="Session identifier")


class DocumentResponse(BaseModel):
    """Document processing response."""

    status: str = Field(..., description="Processing status")
    documents_added: int = Field(..., description="Number of documents added")
    chunks_created: int = Field(..., description="Number of chunks created")
    message: str = Field(..., description="Status message")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    services: Dict[str, str] = Field(..., description="Service statuses")
