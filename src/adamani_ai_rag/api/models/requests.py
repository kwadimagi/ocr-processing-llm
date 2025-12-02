"""API request models."""
from typing import List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat/query request model."""

    question: str = Field(..., description="User question")
    session_id: str = Field(default="default", description="Session identifier")
    k: Optional[int] = Field(default=None, description="Number of documents to retrieve")


class AddTextsRequest(BaseModel):
    """Request to add texts to knowledge base."""

    texts: List[str] = Field(..., description="List of texts to add")
    metadatas: Optional[List[dict]] = Field(default=None, description="Optional metadata for each text")


class UploadFileRequest(BaseModel):
    """File upload configuration."""

    process_ocr: bool = Field(default=True, description="Whether to process with OCR")
