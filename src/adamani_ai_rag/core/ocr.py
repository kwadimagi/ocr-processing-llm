"""OCR processing for document extraction."""
import os
from typing import Optional, List
from pathlib import Path
from PIL import Image
import pytesseract
from langchain_core.documents import Document
from ..config import Settings
from ..utils.logger import get_logger

logger = get_logger()


class OCRProcessor:
    """Handles OCR processing for various document formats."""

    def __init__(self, settings: Settings):
        """
        Initialize OCR processor.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.supported_formats = {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}

    def is_supported(self, file_path: str) -> bool:
        """
        Check if file format is supported.

        Args:
            file_path: Path to file

        Returns:
            True if supported
        """
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_formats

    def extract_text_from_image(self, image_path: str, lang: Optional[str] = None) -> str:
        """
        Extract text from an image using Tesseract OCR.

        Args:
            image_path: Path to image file
            lang: Language code (default from settings)

        Returns:
            Extracted text
        """
        if not self.is_supported(image_path):
            raise ValueError(f"Unsupported file format: {Path(image_path).suffix}")

        lang = lang or self.settings.ocr_languages
        logger.info(f"🔍 Extracting text from: {Path(image_path).name}")

        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=lang)
            logger.success(f"✅ Extracted {len(text)} characters from {Path(image_path).name}")
            return text.strip()

        except Exception as e:
            logger.error(f"❌ OCR extraction failed for {image_path}: {str(e)}")
            raise

    def process_image_to_document(
        self,
        image_path: str,
        metadata: Optional[dict] = None,
    ) -> Document:
        """
        Process image to LangChain Document.

        Args:
            image_path: Path to image file
            metadata: Additional metadata

        Returns:
            Document with extracted text
        """
        text = self.extract_text_from_image(image_path)

        doc_metadata = {
            "source": image_path,
            "filename": Path(image_path).name,
            "type": "ocr",
            "format": Path(image_path).suffix,
        }

        if metadata:
            doc_metadata.update(metadata)

        return Document(page_content=text, metadata=doc_metadata)

    def process_directory(self, directory: str) -> List[Document]:
        """
        Process all supported images in a directory.

        Args:
            directory: Path to directory

        Returns:
            List of documents
        """
        documents = []
        dir_path = Path(directory)

        if not dir_path.exists():
            logger.error(f"❌ Directory not found: {directory}")
            return documents

        logger.info(f"📂 Processing directory: {directory}")

        for file_path in dir_path.glob("*"):
            if file_path.is_file() and self.is_supported(str(file_path)):
                try:
                    doc = self.process_image_to_document(str(file_path))
                    documents.append(doc)
                except Exception as e:
                    logger.error(f"Failed to process {file_path.name}: {e}")

        logger.success(f"✅ Processed {len(documents)} documents from {directory}")
        return documents
