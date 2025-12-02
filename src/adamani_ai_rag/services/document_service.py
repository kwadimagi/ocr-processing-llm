"""Document processing and ingestion service."""
import os
from typing import List
from pathlib import Path
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from ..core.vectorstore import VectorStoreManager
from ..core.ocr import OCRProcessor
from ..core.pdf_processor import PDFProcessor
from ..config import Settings
from ..utils.logger import get_logger

logger = get_logger()


class DocumentService:
    """Service for document processing and ingestion."""

    def __init__(
        self,
        settings: Settings,
        vectorstore: VectorStoreManager,
        ocr_processor: OCRProcessor,
        pdf_processor: PDFProcessor,
    ):
        """
        Initialize document service.

        Args:
            settings: Application settings
            vectorstore: Vector store manager
            ocr_processor: OCR processor
            pdf_processor: PDF processor
        """
        self.settings = settings
        self.vectorstore = vectorstore
        self.ocr_processor = ocr_processor
        self.pdf_processor = pdf_processor

        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )

    def add_texts(self, texts: List[str], metadatas: List[dict] = None) -> int:
        """
        Add texts directly to vector store.

        Args:
            texts: List of texts to add
            metadatas: Optional metadata for each text

        Returns:
            Number of texts added
        """
        logger.info(f"📝 Adding {len(texts)} texts to knowledge base")

        try:
            self.vectorstore.add_texts(texts, metadatas=metadatas)
            logger.success(f"✅ Successfully added {len(texts)} texts")
            return len(texts)

        except Exception as e:
            logger.error(f"❌ Failed to add texts: {str(e)}")
            raise

    def process_documents(self, documents: List[Document]) -> int:
        """
        Process and add documents to vector store.

        Args:
            documents: List of documents to process

        Returns:
            Number of chunks added
        """
        logger.info(f"📄 Processing {len(documents)} documents")

        try:
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"✂️ Split into {len(chunks)} chunks")

            # Add to vector store
            self.vectorstore.add_documents(chunks)
            logger.success(f"✅ Processed {len(documents)} documents ({len(chunks)} chunks)")

            return len(chunks)

        except Exception as e:
            logger.error(f"❌ Failed to process documents: {str(e)}")
            raise

    def process_file(self, file_path: str, use_ocr: bool = False) -> int:
        """
        Process a file (PDF or image) intelligently.

        Args:
            file_path: Path to file
            use_ocr: Force OCR for scanned PDFs

        Returns:
            Number of chunks added
        """
        file_ext = Path(file_path).suffix.lower()
        logger.info(f"📄 Processing {file_ext} file: {Path(file_path).name}")

        try:
            if file_ext == ".pdf":
                # Process PDF
                documents = self.pdf_processor.process_pdf_to_documents(
                    file_path,
                    use_ocr=use_ocr
                )
            elif file_ext in {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}:
                # Process image with OCR
                document = self.ocr_processor.process_image_to_document(file_path)
                documents = [document]
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")

            # Process and add to vector store
            chunks_added = self.process_documents(documents)

            logger.success(f"✅ Processed {Path(file_path).name}: {len(documents)} pages, {chunks_added} chunks")
            return chunks_added

        except Exception as e:
            logger.error(f"❌ Failed to process {file_path}: {str(e)}")
            raise

    def process_directory(self, directory_path: str) -> int:
        """
        Process all supported files in a directory.

        Args:
            directory_path: Path to directory

        Returns:
            Total number of chunks added
        """
        logger.info(f"📂 Processing directory: {directory_path}")

        try:
            # Process all images with OCR
            documents = self.ocr_processor.process_directory(directory_path)

            if not documents:
                logger.warning("No documents found to process")
                return 0

            # Add to vector store
            chunks_added = self.process_documents(documents)

            logger.success(f"✅ Processed directory: {len(documents)} docs, {chunks_added} chunks")
            return chunks_added

        except Exception as e:
            logger.error(f"❌ Failed to process directory {directory_path}: {str(e)}")
            raise

    def clear_vectorstore(self) -> None:
        """Clear all data from vector store."""
        self.vectorstore.clear()
