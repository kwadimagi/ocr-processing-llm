"""Embedding model management."""
from typing import Optional
from langchain_huggingface import HuggingFaceEmbeddings
from ..config import Settings
from ..utils.logger import get_logger

logger = get_logger()


class EmbeddingManager:
    """Manages embedding model initialization and usage."""

    def __init__(self, settings: Settings):
        """
        Initialize embedding manager.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self._embeddings: Optional[HuggingFaceEmbeddings] = None

    def get_embeddings(self) -> HuggingFaceEmbeddings:
        """
        Get or create embeddings instance.

        Returns:
            Initialized HuggingFaceEmbeddings
        """
        if self._embeddings is None:
            logger.info(f"🔧 Initializing embeddings: {self.settings.embedding_model}")
            self._embeddings = HuggingFaceEmbeddings(
                model_name=self.settings.embedding_model,
                model_kwargs={"device": self.settings.embedding_device},
            )
            logger.success("✅ Embeddings initialized")

        return self._embeddings

    def embed_query(self, text: str) -> list[float]:
        """
        Embed a single query text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        embeddings = self.get_embeddings()
        return embeddings.embed_query(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embed multiple documents.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        embeddings = self.get_embeddings()
        logger.info(f"📝 Embedding {len(texts)} documents")
        return embeddings.embed_documents(texts)
