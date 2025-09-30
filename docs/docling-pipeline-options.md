# Docling PdfPipelineOptions Complete Guide

Comprehensive guide for configuring and using PdfPipelineOptions effectively in Docling document processing.

## Overview

`PdfPipelineOptions` is the main class for PDF pipeline configuration in Docling. Pipeline options allow customization of model execution during the conversion pipeline, including OCR engines, table recognition, AI enrichments, and performance settings.

## Basic Configuration

### Simple Setup

```python
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat

# Basic configuration
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False  # Disable OCR for text-based documents
pipeline_options.do_table_structure = True  # Enable table structure recognition

# Initialize converter with options
doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

### Alternative Constructor Approach

```python
# Using constructor parameters
pipeline_options = PdfPipelineOptions(
    do_ocr=False,
    do_table_structure=True,
    generate_page_images=False
)
```

## Core Configuration Options

### Table Processing

```python
from docling.datamodel.pipeline_options import TableFormerMode

# Enable table structure recognition
pipeline_options.do_table_structure = True

# Configure table processing quality
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE  # Better quality
# pipeline_options.table_structure_options.mode = TableFormerMode.FAST     # Faster processing

# Enable cell matching for better table structure
pipeline_options.table_structure_options.do_cell_matching = True
```

### OCR Configuration

```python
from docling.datamodel.pipeline_options import (
    EasyOcrOptions,
    TesseractOcrOptions,
    TesseractCliOcrOptions,
    RapidOcrOptions
)

# Enable OCR
pipeline_options.do_ocr = True

# Choose OCR engine (pick one)
pipeline_options.ocr_options = EasyOcrOptions(force_full_page_ocr=True)
# pipeline_options.ocr_options = TesseractOcrOptions(force_full_page_ocr=True)
# pipeline_options.ocr_options = TesseractCliOcrOptions(force_full_page_ocr=True)
# pipeline_options.ocr_options = RapidOcrOptions(force_full_page_ocr=True)
```

### Image Processing

```python
# Page image generation
pipeline_options.generate_page_images = True  # Extract page images
pipeline_options.images_scale = 2.0  # Control image resolution

# Picture processing
pipeline_options.generate_picture_images = True  # Extract individual pictures
pipeline_options.do_picture_description = True  # AI-powered image descriptions
pipeline_options.do_picture_classification = True  # Classify image types
```

## Performance Optimization

### Speed Optimization

```python
# Fast processing configuration
pipeline_options = PdfPipelineOptions(
    # Disable expensive operations
    do_ocr=False,
    generate_page_images=False,
    generate_picture_images=False,
    do_picture_description=False,
    do_picture_classification=False,

    # Use fast table processing
    do_table_structure=True
)
pipeline_options.table_structure_options.mode = TableFormerMode.FAST
```

### Memory Optimization

```python
# Memory-efficient configuration
pipeline_options = PdfPipelineOptions(
    # Limit pages processed
    max_num_pages=10,

    # Skip image generation to save memory
    generate_page_images=False,
    generate_picture_images=False,

    # Reduce image resolution
    images_scale=0.5
)
```

### Parallel Processing

```python
from docling.datamodel.pipeline_options import AcceleratorOptions, AcceleratorDevice

# Enable parallel processing
pipeline_options.enable_parallel_processing = True

# Configure hardware acceleration
pipeline_options.accelerator_options = AcceleratorOptions(
    num_threads=8,
    device=AcceleratorDevice.CUDA  # or AcceleratorDevice.CPU
)
```

## Advanced Configurations

### Page Range Processing

```python
# Process specific pages only
pipeline_options.page_range = [1, 5]  # Process pages 1-5
pipeline_options.max_num_pages = 3    # Or limit total pages
```

### AI Enrichments

```python
# Enable AI-powered enrichments
pipeline_options.do_code_enrichment = True      # Enhance code blocks
pipeline_options.do_formula_enrichment = True   # Improve formula recognition
pipeline_options.do_picture_description = True  # AI image descriptions
```

### Remote Services

```python
# Enable remote API services (required for some features)
pipeline_options.enable_remote_services = True
pipeline_options.allow_external_plugins = True
```

## Complete Example Configurations

### Versailles Document Processing (Optimized)

```python
def create_versailles_config():
    \"\"\"Optimized configuration for Versailles documentation\"\"\"
    pipeline_options = PdfPipelineOptions(
        # Core features
        do_table_structure=True,  # Important for schedules and pricing tables
        do_ocr=False,            # Most Versailles docs are text-based

        # Performance optimization
        generate_page_images=False,     # Skip images for speed
        generate_picture_images=False,  # Skip individual pictures

        # Quality settings
        do_picture_description=False,   # Disable for speed
        do_code_enrichment=False,      # Not needed for tourism docs
        do_formula_enrichment=False    # Not needed for tourism docs
    )

    # High-quality table processing
    pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
    pipeline_options.table_structure_options.do_cell_matching = True

    return pipeline_options
```

### Scanned Document Processing

```python
def create_scanned_document_config():
    \"\"\"Configuration for scanned PDFs requiring OCR\"\"\"
    pipeline_options = PdfPipelineOptions(
        # OCR required for scanned docs
        do_ocr=True,
        do_table_structure=True,

        # Image processing
        generate_page_images=True,
        images_scale=1.5,  # Higher resolution for better OCR

        # AI enhancements
        do_picture_description=True,
        do_picture_classification=True
    )

    # Use EasyOCR for better multilingual support
    pipeline_options.ocr_options = EasyOcrOptions(force_full_page_ocr=True)

    # High-quality table processing
    pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE

    return pipeline_options
```

### High-Performance Batch Processing

```python
def create_batch_processing_config():
    \"\"\"Configuration for processing many documents quickly\"\"\"
    pipeline_options = PdfPipelineOptions(
        # Minimal processing for speed
        do_ocr=False,
        do_table_structure=True,  # Keep table processing as it's often needed

        # Skip expensive operations
        generate_page_images=False,
        generate_picture_images=False,
        do_picture_description=False,
        do_picture_classification=False,
        do_code_enrichment=False,
        do_formula_enrichment=False,

        # Performance optimization
        enable_parallel_processing=True
    )

    # Fast table processing
    pipeline_options.table_structure_options.mode = TableFormerMode.FAST

    # Limit processing scope
    pipeline_options.max_num_pages = 20  # Skip very large documents

    return pipeline_options
```

## Troubleshooting Common Issues

### Backend Attribute Error

If you encounter `'PdfPipelineOptions' object has no attribute 'backend'`:

```python
# Workaround: Use basic DocumentConverter without format_options
converter = DocumentConverter()  # Don't pass pipeline_options

# Or use try-catch for fallback
try:
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )
except Exception as e:
    print(f"Pipeline config failed: {e}")
    converter = DocumentConverter()  # Use default configuration
```

### Memory Issues

For large documents or batch processing:

```python
# Memory-efficient configuration
pipeline_options = PdfPipelineOptions(
    generate_page_images=False,      # Saves significant memory
    generate_picture_images=False,   # Reduces memory usage
    max_num_pages=10,               # Process fewer pages
    images_scale=0.5                # Lower resolution images
)
```

### Performance Issues

For slow processing:

```python
# Speed-optimized configuration
pipeline_options = PdfPipelineOptions(
    do_ocr=False,                          # Skip OCR if not needed
    do_picture_description=False,          # Skip AI descriptions
    enable_parallel_processing=True        # Use multiple cores
)
pipeline_options.table_structure_options.mode = TableFormerMode.FAST
```

## Best Practices

1. **Start Simple**: Begin with basic configuration and add features as needed
2. **Profile Performance**: Test different configurations to find optimal settings
3. **Memory Management**: Disable image generation for batch processing
4. **Quality vs Speed**: Use ACCURATE mode for important documents, FAST for bulk processing
5. **Error Handling**: Always include fallback to basic DocumentConverter
6. **Version Compatibility**: Some options may not be available in all Docling versions

## Complete Usage Example

```python
#!/usr/bin/env python3
from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

def process_document(pdf_path: Path, config_type: str = "versailles"):
    \"\"\"Process document with specified configuration\"\"\"

    # Choose configuration based on document type
    if config_type == "versailles":
        pipeline_options = create_versailles_config()
    elif config_type == "scanned":
        pipeline_options = create_scanned_document_config()
    elif config_type == "batch":
        pipeline_options = create_batch_processing_config()
    else:
        pipeline_options = PdfPipelineOptions()

    # Initialize converter with error handling
    try:
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        print("✅ Advanced pipeline configuration loaded")
    except Exception as e:
        print(f"⚠️ Pipeline config failed ({e}), using default")
        converter = DocumentConverter()

    # Process document
    result = converter.convert(str(pdf_path))
    return result.document

# Usage
if __name__ == "__main__":
    pdf_file = Path("document.pdf")
    document = process_document(pdf_file, "versailles")
    markdown_content = document.export_to_markdown()

    with open("output.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)
```

## References

- [Official Docling Pipeline Options Documentation](https://docling-project.github.io/docling/reference/pipeline_options/)
- [Docling Usage Guide](https://docling-project.github.io/docling/usage/)
- [Docling Advanced Options](https://docling-project.github.io/docling/usage/advanced_options/)

---

*Generated for Versailles PDF extraction project - optimize your document processing with these configurations.*