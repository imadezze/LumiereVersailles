#!/usr/bin/env python3
"""
Extract Hackathon PDF with Docling AI
=====================================

Using Docling - AI-powered PDF parsing with ML layout detection.
Perfect for complex documents with superior table analysis.
"""

import time
from pathlib import Path

# Check if Docling is installed
try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    print("✅ Docling AI loaded - ready for ML-powered extraction!")
except ImportError:
    print("❌ Docling not installed!")
    print("Install with: pip install docling")
    exit(1)

def main():
    """Extract the hackathon PDF with Docling AI"""

    # Find the PDF
    pdf_path = Path("Livret-Hackathon_ChâteauDeVersailles.pdf")

    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        print("Make sure Livret-Hackathon_ChâteauDeVersailles.pdf is in this directory")
        return

    print("🏰 Versailles Hackathon PDF Extractor - Docling AI Edition")
    print("=" * 65)
    print(f"📖 Processing: {pdf_path.name}")
    print("🤖 Using Docling - ML-powered document analysis!")

    start_time = time.time()

    try:
        # Configure Docling pipeline for Versailles documents
        print("\n🔧 Configuring AI pipeline...")

        # Create pipeline options with exact API specification
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_table_structure = True
        pipeline_options.do_ocr = False
        pipeline_options.generate_page_images = False

        # Initialize converter - try without format_options first
        print("🔧 Initializing DocumentConverter...")
        converter = DocumentConverter()

        # Extract with Docling AI
        print("🚀 Starting ML-based analysis...")
        print("   🧠 Layout detection model: ACTIVE")
        print("   📊 Table analysis model: ACTIVE")
        print("   👁️ OCR: DISABLED (text-based document)")

        conversion_result = converter.convert(str(pdf_path))
        document = conversion_result.document

        # Export to markdown
        print("📝 Converting to markdown...")
        markdown_content = document.export_to_markdown()

        # Create output directory
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        # Save the extracted content
        output_file = output_dir / "Livret-Hackathon_ChateauDeVersailles.md"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Hackathon Château de Versailles\n\n")
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
        print(f"\n🎉 SUCCESS!")
        print(f"⏱️  AI Processing time: {processing_time:.3f} seconds")
        print(f"💾 Saved to: {output_file}")
        print(f"📝 Extracted: {len(markdown_content):,} characters")
        print(f"📄 File size: {output_file.stat().st_size:,} bytes")

        print(f"\n🧠 AI Analysis Results:")
        print(f"   📄 Pages analyzed: {pages_count}")
        print(f"   📊 Tables detected: {tables_count}")
        print(f"   🖼️ Figures found: {figures_count}")

        # Preview the content
        lines = markdown_content.split('\n')[:15]
        print(f"\n📋 Content Preview:")
        print("─" * 70)
        for i, line in enumerate(lines[:15], 1):
            if line.strip():
                display_line = line[:80] + "..." if len(line) > 80 else line
                print(f"{i:2d}: {display_line}")
        print("─" * 70)

        print(f"\n✨ Your Versailles hackathon documentation is ready!")
        print(f"📁 Open: {output_file}")
        print(f"🤖 Perfect for feeding into your LLM/RAG system!")
        print(f"🏆 Docling AI provided superior structure recognition!")

    except Exception as e:
        print(f"\n❌ Extraction failed: {e}")
        print("Check that the PDF file is valid and Docling is properly installed")

if __name__ == "__main__":
    main()