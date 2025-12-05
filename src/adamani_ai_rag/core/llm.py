"""LLM client management."""
from typing import Optional, Union
from langchain_core.language_models.base import BaseLanguageModel
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
        self._client: Optional[BaseLanguageModel] = None

    def get_client(self) -> BaseLanguageModel:
        """
        Get or create LLM client instance based on configured provider.

        Returns:
            Initialized LLM client (Ollama, OpenAI, or Anthropic)
        """
        if self._client is None:
            provider = self.settings.llm_provider.lower()
            logger.info(f"🤖 Initializing LLM client with provider: {provider}")

            # if provider == "ollama":
            #     from langchain_ollama import OllamaLLM
            #     self._client = OllamaLLM(
            #         base_url=self.settings.ollama_base_url,
            #         model=self.settings.ollama_model,
            #         temperature=self.settings.llm_temperature,
            #         timeout=self.settings.llm_timeout,
            #     )
            #     logger.success(f"✅ Ollama client initialized: {self.settings.ollama_model}")
            if provider == "ollama":
                from langchain_ollama import ChatOllama  # ✅ Changed import
                self._client = ChatOllama(
                    base_url=self.settings.ollama_base_url,
                    model=self.settings.ollama_model,
                    temperature=self.settings.llm_temperature,
                    timeout=self.settings.llm_timeout,
                    streaming=True,  # ✅ Explicit streaming
                )
                logger.success(f"✅ Ollama Chat client initialized: {self.settings.ollama_model}")
            elif provider == "openai":
                from langchain_openai import ChatOpenAI
                if not self.settings.openai_api_key:
                    raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
                self._client = ChatOpenAI(
                    api_key=self.settings.openai_api_key,
                    model=self.settings.openai_model,
                    temperature=self.settings.llm_temperature,
                    timeout=self.settings.llm_timeout,
                )
                logger.success(f"✅ OpenAI client initialized: {self.settings.openai_model}")

            elif provider == "anthropic":
                from langchain_anthropic import ChatAnthropic
                if not self.settings.anthropic_api_key:
                    raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic provider")
                self._client = ChatAnthropic(
                    api_key=self.settings.anthropic_api_key,
                    model=self.settings.anthropic_model,
                    temperature=self.settings.llm_temperature,
                    timeout=self.settings.llm_timeout,
                )
                logger.success(f"✅ Anthropic client initialized: {self.settings.anthropic_model}")

            else:
                raise ValueError(f"Unsupported LLM provider: {provider}. Choose from: ollama, openai, anthropic")

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
