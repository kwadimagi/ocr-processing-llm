"""LLM client management."""
from typing import Optional
from langchain_ollama import OllamaLLM
from ..config import Settings
from ..utils.logger import get_logger

logger = get_logger()


class LLMClient:
    """Manages LLM client connections and interactions."""

    def __init__(self, settings: Settings):
        """
        Initialize LLM client.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self._client: Optional[OllamaLLM] = None

    def get_client(self) -> OllamaLLM:
        """
        Get or create LLM client instance.

        Returns:
            Initialized OllamaLLM client
        """
        if self._client is None:
            logger.info(f"🤖 Initializing LLM client: {self.settings.ollama_model}")
            self._client = OllamaLLM(
                base_url=self.settings.ollama_base_url,
                model=self.settings.ollama_model,
                temperature=self.settings.llm_temperature,
                timeout=self.settings.llm_timeout,
            )
            logger.success("✅ LLM client initialized")

        return self._client

    def generate(self, prompt: str) -> str:
        """
        Generate text from prompt.

        Args:
            prompt: Input prompt

        Returns:
            Generated text
        """
        client = self.get_client()
        logger.debug(f"Generating response for prompt: {prompt[:100]}...")
        response = client.invoke(prompt)
        logger.debug(f"Response generated: {len(response)} characters")
        return response
