"""
Versailles PDF Parser - 2025 Edition
====================================

Using Docling - AI-powered PDF parsing with ML layout detection.
Perfect for complex documents with superior table analysis and structure recognition.

Docling advantages:
- ML-based layout detection model
- Advanced table analysis model
- Excellent structure preservation
- Built-in OCR capabilities
- Superior handling of complex documents
"""

import os
import time
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    print("❌ Docling not installed. Run: pip install docling")

from ..utils.config import PDFParsingConfig
from ..utils.helpers import validate_pdf, get_safe_filename, get_pdf_info


class VersaillesPDFParser:
    """
    AI-powered PDF parser using Docling for advanced document analysis
    Optimized for Versailles documentation with ML layout detection
    """

    def __init__(self, config: Optional[PDFParsingConfig] = None):
        """
        Initialize parser with configuration

        Args:
            config: Parsing configuration (uses Versailles defaults if None)
        """
        if not DOCLING_AVAILABLE:
            raise ImportError("Docling is required. Install with: pip install docling")

        self.config = config or PDFParsingConfig.versailles_optimized()

        # Initialize Docling converter with appropriate pipeline options
        pipeline_options = PdfPipelineOptions(
            do_ocr=self.config.use_ocr,
            do_table_structure=self.config.use_table_model,
            generate_page_images=False  # Speed optimization
        )

        self.converter = DocumentConverter(
            format_options={InputFormat.PDF: pipeline_options}
        )

        if self.config.verbose:
            print("🏰 Versailles PDF Parser initialized with Docling")
            print(f"🤖 Layout detection: {self.config.use_layout_model}")
            print(f"📊 Table analysis: {self.config.use_table_model}")
            print(f"👁️ OCR enabled: {self.config.use_ocr}")
            print(f"📁 Output directory: {self.config.output_dir}")

    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Parse PDF and return results

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with parsing results
        """
        # Validate input
        if not validate_pdf(pdf_path):
            return {
                "success": False,
                "error": "Invalid or inaccessible PDF file",
                "file_path": pdf_path
            }

        start_time = time.time()
        pdf_info = get_pdf_info(pdf_path)

        if self.config.verbose:
            print(f"📖 Processing: {pdf_info['filename']}")
            print(f"📏 Size: {pdf_info['size_formatted']}")

        try:
            # Parse with Docling - AI-powered document analysis
            document_result = self._extract_with_docling(pdf_path)

            # Convert to requested format
            if self.config.export_format == "markdown":
                content = document_result.document.export_to_markdown()
            elif self.config.export_format == "json":
                content = document_result.document.export_to_dict()
            else:
                content = document_result.document.export_to_markdown()  # Default

            # Post-process if requested
            if self.config.clean_output and isinstance(content, str):
                content = self._clean_markdown(content)

            # Generate output filename
            extension = ".md" if self.config.export_format == "markdown" else ".json"
            output_filename = get_safe_filename(pdf_info['filename'], extension)
            output_path = Path(self.config.output_dir) / output_filename

            # Save to file
            self._save_content(content, output_path)

            processing_time = time.time() - start_time

            result = {
                "success": True,
                "content": content,
                "output_file": str(output_path),
                "processing_time": round(processing_time, 3),
                "file_info": pdf_info,
                "document_info": {
                    "pages": len(document_result.document.pages) if hasattr(document_result.document, 'pages') else 0,
                    "tables": self._count_document_elements(document_result.document, 'table'),
                    "figures": self._count_document_elements(document_result.document, 'figure')
                },
                "config": self.config
            }

            if self.config.verbose:
                print(f"✅ Completed in {processing_time:.3f}s")
                print(f"💾 Saved to: {output_path}")
                print(f"📄 Pages: {result['document_info']['pages']}")
                print(f"📊 Tables found: {result['document_info']['tables']}")
                print(f"🖼️ Figures found: {result['document_info']['figures']}")
                if isinstance(content, str):
                    print(f"📝 Content length: {len(content)} characters")

            return result

        except Exception as e:
            error_msg = f"Error parsing PDF with Docling: {str(e)}"
            if self.config.verbose:
                print(f"❌ {error_msg}")

            return {
                "success": False,
                "error": error_msg,
                "file_path": pdf_path,
                "processing_time": time.time() - start_time
            }

    def _extract_with_docling(self, pdf_path: str):
        """
        Extract content using Docling ML-based parsing

        Args:
            pdf_path: Path to PDF file

        Returns:
            Docling conversion result
        """
        if self.config.verbose:
            print("🤖 Starting ML-based document analysis...")

        # Convert document using Docling
        conversion_result = self.converter.convert(pdf_path)

        if self.config.verbose:
            print("✅ Document analysis complete")

        return conversion_result

    def _count_document_elements(self, document, element_type: str) -> int:
        """
        Count specific elements in the document

        Args:
            document: Docling document object
            element_type: Type of element to count ('table', 'figure', etc.)

        Returns:
            Count of elements
        """
        try:
            count = 0
            if hasattr(document, 'pages'):
                for page in document.pages:
                    # Check different possible structures
                    if hasattr(page, 'predictions'):
                        predictions = page.predictions
                        if isinstance(predictions, dict) and element_type + 's' in predictions:
                            count += len(predictions[element_type + 's'])
                        elif hasattr(predictions, element_type + 's'):
                            count += len(getattr(predictions, element_type + 's'))

                    # Also check for items directly
                    if hasattr(page, 'items'):
                        for item in page.items:
                            if hasattr(item, 'type') and element_type in str(item.type).lower():
                                count += 1

            return count
        except Exception:
            return 0

    def _clean_markdown(self, text: str) -> str:
        """
        Clean and optimize markdown text

        Args:
            text: Raw markdown text

        Returns:
            Cleaned markdown text
        """
        if not text:
            return text

        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            # Remove excessive whitespace
            line = line.strip()

            # Skip empty lines (but keep intentional breaks)
            if not line:
                if cleaned_lines and cleaned_lines[-1] != "":
                    cleaned_lines.append("")
                continue

            cleaned_lines.append(line)

        # Join and clean up multiple empty lines
        result = '\n'.join(cleaned_lines)

        # Remove excessive line breaks (more than 2 consecutive)
        import re
        result = re.sub(r'\n{3,}', '\n\n', result)

        return result.strip()

    def _save_content(self, content, output_path: Path) -> None:
        """
        Save content to file (supports both string and dict)

        Args:
            content: Content to save (string or dict)
            output_path: Output file path
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # Add header if metadata is requested
                if self.config.include_metadata:
                    f.write("# Document Extracted by Versailles PDF Parser\n\n")
                    f.write(f"*Processed with Docling AI - ML-Powered Document Analysis*\n\n")
                    f.write("---\n\n")

                if isinstance(content, str):
                    f.write(content)
                else:
                    # Handle dict content (JSON)
                    import json
                    json.dump(content, f, indent=2, ensure_ascii=False)

        except Exception as e:
            raise Exception(f"Failed to save output: {e}")

    def parse_multiple(self, pdf_directory: str, pattern: str = "*.pdf") -> Dict[str, Any]:
        """
        Parse multiple PDFs in a directory

        Args:
            pdf_directory: Directory containing PDFs
            pattern: File pattern to match (default: "*.pdf")

        Returns:
            Results for all processed files
        """
        pdf_dir = Path(pdf_directory)
        if not pdf_dir.exists():
            return {"error": f"Directory not found: {pdf_directory}"}

        pdf_files = list(pdf_dir.glob(pattern))
        if not pdf_files:
            return {"error": f"No PDF files found in {pdf_directory}"}

        results = {
            "total_files": len(pdf_files),
            "successful": 0,
            "failed": 0,
            "results": []
        }

        if self.config.verbose:
            print(f"📁 Processing {len(pdf_files)} PDFs from {pdf_directory}")

        for pdf_file in pdf_files:
            if self.config.verbose:
                print(f"\n🔄 Processing: {pdf_file.name}")

            result = self.parse_pdf(str(pdf_file))
            results["results"].append(result)

            if result["success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1

        if self.config.verbose:
            print(f"\n✅ Batch complete: {results['successful']} successful, {results['failed']} failed")

        return results


# Convenience function for quick parsing
def parse_pdf_quick(pdf_path: str, output_dir: str = "output") -> str:
    """
    Quick PDF parsing function using Docling AI

    Args:
        pdf_path: Path to PDF file
        output_dir: Output directory

    Returns:
        Extracted content (markdown or JSON based on config)
    """
    config = PDFParsingConfig.versailles_optimized()
    config.output_dir = output_dir
    config.verbose = False
    config.export_format = "markdown"  # Default to markdown for quick parsing

    parser = VersaillesPDFParser(config)
    result = parser.parse_pdf(pdf_path)

    if result["success"]:
        return result["content"]
    else:
        raise Exception(f"PDF parsing with Docling failed: {result.get('error', 'Unknown error')}")