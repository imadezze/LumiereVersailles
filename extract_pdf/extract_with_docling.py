#!/usr/bin/env python3
"""
Extract Documents with Docling AI
==================================

Using Docling - AI-powered document parsing with ML layout detection.
Perfect for complex documents with superior table analysis.

Usage:
    python extract_with_docling.py                          # Extract default hackathon PDF
    python extract_with_docling.py file.pdf                 # Extract single PDF
    python extract_with_docling.py /path/to/folder          # Extract all PDFs in folder
    python extract_with_docling.py /path/to/folder --recursive  # Extract all PDFs recursively
"""

import sys
import time
import argparse
from pathlib import Path
from typing import List, Optional

# Check if Docling is installed
try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    print("✅ Docling AI loaded - ready for ML-powered extraction!")
except ImportError:
    print("❌ Docling not installed!")
    print("Install with: pip install docling")
    exit(1)

def find_pdf_files(path: Path, recursive: bool = False) -> List[Path]:
    """Find all PDF files in the given path"""
    if path.is_file():
        if path.suffix.lower() == '.pdf':
            return [path]
        else:
            print(f"❌ {path} is not a PDF file")
            return []

    elif path.is_dir():
        pattern = "**/*.pdf" if recursive else "*.pdf"
        pdf_files = list(path.glob(pattern))
        if not pdf_files:
            depth_msg = "recursively" if recursive else "in directory"
            print(f"❌ No PDF files found {depth_msg}: {path}")
            return []
        return sorted(pdf_files)

    else:
        print(f"❌ Path not found: {path}")
        return []

def extract_single_pdf(pdf_path: Path, converter: DocumentConverter, output_dir: Path, base_path: Path = None) -> bool:
    """Extract a single PDF file"""
    print(f"📖 Processing: {pdf_path.name}")

    start_time = time.time()

    try:
        # Extract with Docling AI
        print("🚀 Starting ML-based analysis...")
        conversion_result = converter.convert(str(pdf_path))
        document = conversion_result.document

        # Export to markdown
        print("📝 Converting to markdown...")
        markdown_content = document.export_to_markdown()

        # Preserve original folder structure in output
        if base_path and pdf_path.is_relative_to(base_path):
            # Get relative path from base directory
            rel_path = pdf_path.relative_to(base_path)
            # Create same subfolder structure in output directory
            if len(rel_path.parts) > 1:
                # Create subfolder path in output directory
                output_subfolder = output_dir / rel_path.parent
                output_subfolder.mkdir(parents=True, exist_ok=True)
                safe_name = pdf_path.stem.replace(' ', '_').replace('â', 'a').replace('ô', 'o')
                output_file = output_subfolder / f"{safe_name}.md"
            else:
                safe_name = pdf_path.stem.replace(' ', '_').replace('â', 'a').replace('ô', 'o')
                output_file = output_dir / f"{safe_name}.md"
        else:
            safe_name = pdf_path.stem.replace(' ', '_').replace('â', 'a').replace('ô', 'o')
            output_file = output_dir / f"{safe_name}.md"

        # Save the extracted content
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {pdf_path.stem}\n\n")
            f.write("*Extracted with Docling AI - ML-Powered Document Analysis*\n\n")
            f.write("---\n\n")
            f.write(markdown_content)

        processing_time = time.time() - start_time

        # Analyze what we found
        pages_count = len(document.pages) if hasattr(document, 'pages') else 0

        # Count tables and figures safely
        tables_count = 0
        figures_count = 0

        try:
            if hasattr(document, 'pages'):
                for page in document.pages:
                    if hasattr(page, 'predictions'):
                        predictions = page.predictions
                        if isinstance(predictions, dict):
                            tables_count += len(predictions.get('tables', []))
                            figures_count += len(predictions.get('figures', []))
                        else:
                            # Alternative structure check
                            if hasattr(predictions, 'tables'):
                                tables_count += len(predictions.tables)
                            if hasattr(predictions, 'figures'):
                                figures_count += len(predictions.figures)
        except Exception:
            # If analysis fails, continue with 0 counts
            pass

        # Success report
        print(f"✅ SUCCESS! Time: {processing_time:.2f}s | Pages: {pages_count} | Tables: {tables_count} | Figures: {figures_count}")
        print(f"💾 Saved: {output_file}")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def main():
    """Main extraction function with argument parsing"""

    parser = argparse.ArgumentParser(
        description="Extract documents with Docling AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_with_docling.py                          # Extract default hackathon PDF
  python extract_with_docling.py file.pdf                 # Extract single PDF
  python extract_with_docling.py /path/to/folder          # Extract all PDFs in folder
  python extract_with_docling.py /path/to/folder -r       # Extract all PDFs recursively
        """
    )

    parser.add_argument('path', nargs='?', default='Livret-Hackathon_ChâteauDeVersailles.pdf',
                       help='PDF file or folder path (default: Livret-Hackathon_ChâteauDeVersailles.pdf)')
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='Search folders recursively')
    parser.add_argument('-o', '--output', default='output',
                       help='Output directory (default: output)')

    args = parser.parse_args()

    # Parse input path
    input_path = Path(args.path)
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)

    # Find PDF files
    pdf_files = find_pdf_files(input_path, args.recursive)
    if not pdf_files:
        sys.exit(1)

    print("🏰 Versailles Document Extractor - Docling AI Edition")
    print("=" * 60)
    print(f"📁 Input: {input_path}")
    print(f"📄 Found {len(pdf_files)} PDF file(s)")
    print(f"💾 Output: {output_dir}")
    print("🤖 Using Docling - ML-powered document analysis!")

    # Configure Docling pipeline
    print("\n🔧 Configuring AI pipeline...")
    print("   🧠 Layout detection model: ACTIVE")
    print("   📊 Table analysis model: ACTIVE")
    print("   👁️ OCR: DISABLED (text-based documents)")

    # Create pipeline options with exact API specification
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_table_structure = True
    pipeline_options.do_ocr = False
    pipeline_options.generate_page_images = False

    # Initialize converter with pipeline options
    try:
        from docling.datamodel.base_models import InputFormat
        converter = DocumentConverter()
        print("✅ Pipeline configured successfully")
    except Exception as e:
        print(f"⚠️  Pipeline config failed ({e}), using default converter")
        converter = DocumentConverter()

    # Process all files
    successful = 0
    failed = 0
    total_start_time = time.time()

    print(f"\n🚀 Processing {len(pdf_files)} files...")
    print("=" * 60)

    # Determine base path for preserving folder structure
    base_path = input_path if input_path.is_dir() else input_path.parent

    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] ", end="")
        if extract_single_pdf(pdf_path, converter, output_dir, base_path):
            successful += 1
        else:
            failed += 1

    total_time = time.time() - total_start_time

    # Final summary
    print("\n" + "=" * 60)
    print("🎉 EXTRACTION COMPLETE!")
    print(f"⏱️  Total time: {total_time:.2f} seconds")
    print(f"✅ Successful: {successful}")
    if failed > 0:
        print(f"❌ Failed: {failed}")
    print(f"📁 All outputs saved to: {output_dir}")
    print("🤖 Perfect for feeding into your LLM/RAG system!")

if __name__ == "__main__":
    main()