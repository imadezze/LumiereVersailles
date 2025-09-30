"""
Configuration for PDF parsing using Docling
ML-powered parsing with excellent layout detection and table analysis
"""
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

@dataclass
class PDFParsingConfig:
    """Configuration for Docling - AI-powered document processing"""

    # Output settings
    output_dir: str = "output"
    include_metadata: bool = True

    # Page selection
    max_pages: Optional[int] = None
    page_range: Optional[tuple] = None  # (start_page, end_page)

    # ML Processing options
    use_layout_model: bool = True       # Use ML layout detection
    use_table_model: bool = True        # Use ML table analysis
    use_ocr: bool = False              # Enable OCR for scanned docs

    # Content processing
    clean_output: bool = True          # Remove extra whitespace, clean formatting
    include_page_numbers: bool = True   # Add page references
    preserve_tables: bool = True        # Keep table structure
    export_format: str = "markdown"    # "markdown", "json", "docx"

    # Performance
    verbose: bool = False

    def __post_init__(self):
        """Validate configuration"""
        if self.max_pages and self.max_pages <= 0:
            raise ValueError("max_pages must be positive")

        if self.page_range:
            start, end = self.page_range
            if start >= end or start < 0:
                raise ValueError("Invalid page range: start must be < end and >= 0")

        # Ensure output directory exists
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    @classmethod
    def versailles_optimized(cls) -> 'PDFParsingConfig':
        """Optimized for Versailles documentation (brochures, guides, tickets)"""
        return cls(
            use_layout_model=True,
            use_table_model=True,
            use_ocr=False,  # Most Versailles docs are text-based
            clean_output=True,
            include_page_numbers=True,
            preserve_tables=True,
            include_metadata=True,
            export_format="markdown",
            verbose=False
        )

    @classmethod
    def fast_preview(cls) -> 'PDFParsingConfig':
        """Quick preview of first few pages"""
        return cls(
            max_pages=5,
            use_layout_model=True,
            use_table_model=False,  # Skip table analysis for speed
            use_ocr=False,
            clean_output=True,
            include_metadata=False,
            export_format="markdown",
            verbose=False
        )

    @classmethod
    def scanned_document(cls) -> 'PDFParsingConfig':
        """For scanned PDFs requiring OCR"""
        return cls(
            use_layout_model=True,
            use_table_model=True,
            use_ocr=True,  # Enable OCR for scanned docs
            clean_output=True,
            preserve_tables=True,
            export_format="markdown",
            verbose=True
        )