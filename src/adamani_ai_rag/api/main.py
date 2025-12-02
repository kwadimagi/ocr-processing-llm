from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List
import sys
import logging

from loguru import logger

from langchain_ollama import OllamaLLM
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser

import os

# -----------------------------------------------------------------------------
# LOGURU CONFIGURATION
# -----------------------------------------------------------------------------
# Remove default logger
logger.remove()

# Add custom logger with beautiful formatting
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
)

# Intercept standard logging to use loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

# Configure uvicorn and fastapi to use loguru
logging.basicConfig(handlers=[InterceptHandler()], level=0)
for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"]:
    logging.getLogger(logger_name).handlers = [InterceptHandler()]

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3")  # Ollama local model name
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

logger.info(f"🚀 Starting Adamani AI RAG Server")
logger.info(f"📝 LLM Model: {MODEL_NAME}")
logger.info(f"🔤 Embedding Model: {EMBED_MODEL}")

# -----------------------------------------------------------------------------
# FASTAPI APP
# -----------------------------------------------------------------------------
app = FastAPI(
    title="Adamani AI RAG Server",
    description="Local LLM + RAG + Memory backend",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    logger.success("✅ Application startup complete!")

@app.on_event("shutdown")
async def shutdown_event():
    logger.warning("🛑 Application shutting down...")

# -----------------------------------------------------------------------------
# GLOBAL COMPONENTS
# -----------------------------------------------------------------------------

# Embeddings
logger.info("🔧 Initializing embeddings...")
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
logger.success("✅ Embeddings initialized")

# Temporary in-memory FAISS store
logger.info("🗄️  Initializing FAISS vector store...")
vector_store = FAISS.from_texts(
    texts=["This is an empty knowledge base. Add documents via /add-docs."],
    embedding=embeddings,
)
logger.success("✅ FAISS vector store initialized")

# LLM Client
logger.info("🤖 Connecting to Ollama LLM...")
llm = OllamaLLM(
    model=MODEL_NAME,
    temperature=0.1
)
logger.success("✅ LLM client ready")

# Chat history storage
chat_histories = {}

def get_chat_history(session_id: str):
    if session_id not in chat_histories:
        chat_histories[session_id] = ChatMessageHistory()
    return chat_histories[session_id]

# RAG prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use the following context to answer the question.\n\nContext: {context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])

# RAG chain
def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

# -----------------------------------------------------------------------------
# REQUEST MODELS
# -----------------------------------------------------------------------------
class ChatRequest(BaseModel):
    question: str
    session_id: str = "default"


class AddDocsRequest(BaseModel):
    documents: List[str]


# -----------------------------------------------------------------------------
# ROUTES
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    logger.info("📡 Health check requested")
    return {"status": "ok", "message": "Adamani AI RAG backend running."}


@app.post("/chat")
def chat(req: ChatRequest):
    """
    Main chat endpoint with RAG + Memory.
    """
    logger.info(f"💬 New chat request | Session: {req.session_id} | Question: {req.question[:50]}...")

    try:
        # Retrieve relevant documents
        logger.debug(f"🔍 Retrieving relevant documents...")
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(req.question)
        logger.info(f"📚 Retrieved {len(docs)} documents")
        context = format_docs(docs)

        # Get chat history
        history = get_chat_history(req.session_id)
        logger.debug(f"📜 Chat history length: {len(history.messages)} messages")

        # Format the prompt
        messages = prompt.format_messages(
            context=context,
            chat_history=history.messages,
            question=req.question
        )

        # Get response from LLM
        logger.info("🤖 Generating LLM response...")
        response = llm.invoke(messages)
        logger.success(f"✅ Response generated | Length: {len(response)} chars")

        # Update chat history
        history.add_user_message(req.question)
        history.add_ai_message(response)

        return {
            "answer": response,
            "sources": [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs]
        }
    except Exception as e:
        logger.error(f"❌ Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-docs")
def add_docs(req: AddDocsRequest):
    """
    Add new documents to the FAISS vector store.
    """
    logger.info(f"📄 Adding {len(req.documents)} documents to vector store...")

    try:
        global vector_store
        vector_store.add_texts(req.documents)
        logger.success(f"✅ Successfully added {len(req.documents)} documents")
        return {"added": len(req.documents), "status": "success"}
    except Exception as e:
        logger.error(f"❌ Error adding documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/clear")
def clear_memory(session_id: str = "default"):
    """
    Reset/clear chat history (memory wipe).
    """
    logger.info(f"🗑️  Clearing memory for session: {session_id}")

    if session_id in chat_histories:
        chat_histories[session_id].clear()
        logger.success(f"✅ Memory cleared for session: {session_id}")
    else:
        logger.warning(f"⚠️  No history found for session: {session_id}")

    return {"status": "memory cleared", "session_id": session_id}
