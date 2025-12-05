"""RAG (Retrieval-Augmented Generation) service."""
from typing import List, Dict, AsyncGenerator
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document

from ..core.llm import LLMClient
from ..core.vectorstore import VectorStoreManager
from ..core.memory import MemoryManager
from ..config import Settings
from ..utils.logger import get_logger

logger = get_logger()


class RAGService:
    """Service for RAG-based question answering."""

    def __init__(
        self,
        settings: Settings,
        llm_client: LLMClient,
        vectorstore: VectorStoreManager,
        memory: MemoryManager,
    ):
        """
        Initialize RAG service.

        Args:
            settings: Application settings
            llm_client: LLM client instance
            vectorstore: Vector store manager
            memory: Memory manager
        """
        self.settings = settings
        self.llm_client = llm_client
        self.vectorstore = vectorstore
        self.memory = memory

        # RAG prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant. Use the following context to answer the user's question. "
                      "If you cannot answer based on the context, say so.\n\nContext: {context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])

    def _format_docs(self, docs: List[Document]) -> str:
        """Format documents into a context string."""
        return "\n\n".join([doc.page_content for doc in docs])

    def query(
        self,
        question: str,
        session_id: str = "default",
        k: int = None,
    ) -> Dict[str, any]:
        """
        Query the RAG system.

        Args:
            question: User question
            session_id: Session identifier
            k: Number of documents to retrieve

        Returns:
            Dictionary with answer and sources
        """
        logger.info(f"💬 RAG Query | Session: {session_id} | Q: {question[:50]}...")

        try:
            # Retrieve relevant documents
            k = k or self.settings.retrieval_top_k
            docs = self.vectorstore.similarity_search(question, k=k)
            logger.info(f"📚 Retrieved {len(docs)} documents")

            context = self._format_docs(docs)

            # Get chat history
            history = self.memory.get_history(session_id)

            # Format prompt
            messages = self.prompt.format_messages(
                context=context,
                chat_history=history.messages,
                question=question
            )

            # Generate response
            logger.info("🤖 Generating response...")
            llm = self.llm_client.get_client()
            answer = llm.invoke(messages)

            # Update memory
            self.memory.add_user_message(session_id, question)
            self.memory.add_ai_message(session_id, answer)

            logger.success(f"✅ Response generated ({len(answer)} chars)")

            return {
                "answer": answer,
                "sources": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                    }
                    for doc in docs
                ],
                "session_id": session_id,
            }

        except Exception as e:
            logger.error(f"❌ RAG query failed: {str(e)}")
            raise

    async def query_stream(
        self,
        question: str,
        session_id: str = "default",
        k: int = None,
    ) -> AsyncGenerator[Dict[str, any], None]:
        """
        Query the RAG system with streaming response.

        Args:
            question: User question
            session_id: Session identifier
            k: Number of documents to retrieve

        Yields:
            Dictionary chunks with token, sources, and metadata
        """
        logger.info(f"💬 RAG Stream Query | Session: {session_id} | Q: {question[:50]}...")

        try:
            # Retrieve relevant documents
            k = k or self.settings.retrieval_top_k
            docs = self.vectorstore.similarity_search(question, k=k)
            logger.info(f"📚 Retrieved {len(docs)} documents")

            # Send sources first
            sources = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                }
                for doc in docs
            ]
            yield {
                "type": "sources",
                "sources": sources,
                "session_id": session_id,
            }

            context = self._format_docs(docs)

            # Get chat history
            history = self.memory.get_history(session_id)

            # Format prompt
            messages = self.prompt.format_messages(
                context=context,
                chat_history=history.messages,
                question=question
            )

            # Generate streaming response
            logger.info("🤖 Generating streaming response...")
            llm = self.llm_client.get_client()

            full_response = ""
            async for chunk in llm.astream(messages):
                # Handle different response formats
                if hasattr(chunk, 'content'):
                    token = chunk.content
                else:
                    token = str(chunk)

                full_response += token
                yield {
                    "type": "token",
                    "token": token,
                }

            # Update memory with complete response
            self.memory.add_user_message(session_id, question)
            self.memory.add_ai_message(session_id, full_response)

            logger.success(f"✅ Streaming response completed ({len(full_response)} chars)")

            # Send completion signal
            yield {
                "type": "done",
                "session_id": session_id,
            }

        except Exception as e:
            logger.error(f"❌ RAG stream query failed: {str(e)}")
            yield {
                "type": "error",
                "error": str(e),
            }
            raise
