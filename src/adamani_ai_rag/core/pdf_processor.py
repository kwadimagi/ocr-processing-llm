"""PDF processing and text extraction."""
import os
from typing import List, Optional
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, PDFMinerLoader
from ..config import Settings
from ..utils.logger import get_logger

logger = get_logger()


class PDFProcessor:
    """Handles PDF document processing and text extraction."""

    def __init__(self, settings: Settings):
        """
        Initialize PDF processor.

        Args:
            settings: Application settings
        """
        self.settings = settings

    def extract_text_from_pdf(
        self,
        pdf_path: str,
        use_ocr: bool = False
    ) -> List[Document]:
        """
        Extract text from PDF file.

        Args:
            pdf_path: Path to PDF file
            use_ocr: Whether to use OCR for scanned PDFs

        Returns:
            List of Document objects (one per page)
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        logger.info(f"📄 Extracting text from PDF: {Path(pdf_path).name}")

        try:
            # Use PyPDF for standard PDFs
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()

            # Check if we got empty pages (might be scanned)
            if use_ocr or self._is_scanned_pdf(documents):
                logger.info("📷 PDF appears to be scanned, using OCR...")
                documents = self._process_with_ocr(pdf_path)

            # Add metadata
            for i, doc in enumerate(documents):
                doc.metadata.update({
                    "source": pdf_path,
                    "filename": Path(pdf_path).name,
                    "page": i + 1,
                    "total_pages": len(documents),
                    "type": "pdf",
                })

            logger.success(f"✅ Extracted {len(documents)} pages from PDF")
            return documents

        except Exception as e:
            logger.error(f"❌ Failed to extract text from PDF: {str(e)}")
            raise

    def _is_scanned_pdf(self, documents: List[Document]) -> bool:
        """
        Check if PDF is scanned (contains little to no text).

        Args:
            documents: List of documents from PDF

        Returns:
            True if appears to be scanned
        """
        if not documents:
            return True

        # Check first few pages
        sample_pages = documents[:min(3, len(documents))]
        avg_length = sum(len(doc.page_content) for doc in sample_pages) / len(sample_pages)

        # If average page has less than 100 characters, likely scanned
        return avg_length < 100

    def _process_with_ocr(self, pdf_path: str) -> List[Document]:
        """
        Process scanned PDF with OCR.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of documents with OCR text
        """
        try:
            # Convert PDF to images and OCR each page
            import pdf2image
            from PIL import Image
            import pytesseract

            logger.info("Converting PDF pages to images for OCR...")
            images = pdf2image.convert_from_path(pdf_path)

            documents = []
            for i, image in enumerate(images):
                logger.debug(f"Processing page {i + 1}/{len(images)} with OCR")

                # Extract text with Tesseract
                text = pytesseract.image_to_string(image, lang=self.settings.ocr_languages)

                # Create document
                doc = Document(
                    page_content=text.strip(),
                    metadata={
                        "source": pdf_path,
                        "filename": Path(pdf_path).name,
                        "page": i + 1,
                        "total_pages": len(images),
                        "type": "pdf_ocr",
                    }
                )
                documents.append(doc)

            logger.success(f"✅ OCR processed {len(documents)} pages")
            return documents

        except ImportError:
            logger.error("❌ pdf2image not installed. Install with: pip install pdf2image")
            logger.warning("Falling back to empty documents")
            return []
        except Exception as e:
            logger.error(f"❌ OCR processing failed: {str(e)}")
            raise

    def process_pdf_to_documents(
        self,
        pdf_path: str,
        use_ocr: bool = False,
        metadata: Optional[dict] = None,
    ) -> List[Document]:
        """
        Process PDF file to LangChain Documents.

        Args:
            pdf_path: Path to PDF file
            use_ocr: Force OCR processing
            metadata: Additional metadata to add

        Returns:
            List of processed documents
        """
        documents = self.extract_text_from_pdf(pdf_path, use_ocr=use_ocr)

        # Add custom metadata
        if metadata:
            for doc in documents:
                doc.metadata.update(metadata)

        return documents

    def process_directory(self, directory: str, use_ocr: bool = False) -> List[Document]:
        """
        Process all PDF files in a directory.

        Args:
            directory: Path to directory
            use_ocr: Whether to use OCR for scanned PDFs

        Returns:
            List of all documents from all PDFs
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            logger.error(f"❌ Directory not found: {directory}")
            return []

        logger.info(f"📂 Processing PDFs in directory: {directory}")

        all_documents = []
        pdf_files = list(dir_path.glob("*.pdf")) + list(dir_path.glob("*.PDF"))

        for pdf_file in pdf_files:
            try:
                docs = self.process_pdf_to_documents(str(pdf_file), use_ocr=use_ocr)
                all_documents.extend(docs)
            except Exception as e:
                logger.error(f"Failed to process {pdf_file.name}: {e}")

        logger.success(f"✅ Processed {len(pdf_files)} PDFs, extracted {len(all_documents)} pages")
        return all_documents
