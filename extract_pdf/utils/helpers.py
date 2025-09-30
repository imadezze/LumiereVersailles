"""
Simple helper functions for PDF processing
"""
import os
from pathlib import Path
from typing import Dict, Any

def validate_pdf(file_path: str) -> bool:
    """
    Validate if file is a PDF and accessible

    Args:
        file_path: Path to PDF file

    Returns:
        True if valid PDF, False otherwise
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return False

        if not path.suffix.lower() == '.pdf':
            return False

        # Check if file is readable
        if not os.access(path, os.R_OK):
            return False

        # Basic file size check (not empty, not too large)
        size = path.stat().st_size
        if size == 0:
            return False
        if size > 500 * 1024 * 1024:  # 500MB limit
            print(f"⚠️  Warning: Large PDF file ({size // (1024*1024)}MB)")

        return True

    except Exception as e:
        print(f"❌ Error validating PDF: {e}")
        return False

def get_safe_filename(original_name: str, extension: str = ".md") -> str:
    """
    Generate a safe filename for output

    Args:
        original_name: Original PDF filename
        extension: Output file extension

    Returns:
        Safe filename for output
    """
    # Remove extension and clean name
    base_name = Path(original_name).stem

    # Replace problematic characters
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    safe_name = "".join(c if c in safe_chars else "_" for c in base_name)

    # Limit length and ensure not empty
    safe_name = safe_name[:100] or "document"

    return f"{safe_name}{extension}"

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}TB"

def get_pdf_info(file_path: str) -> Dict[str, Any]:
    """Get basic PDF file information"""
    try:
        path = Path(file_path)
        size = path.stat().st_size

        return {
            "filename": path.name,
            "size": size,
            "size_formatted": format_file_size(size),
            "exists": True,
            "readable": os.access(path, os.R_OK)
        }
    except Exception as e:
        return {
            "filename": file_path,
            "error": str(e),
            "exists": False,
            "readable": False
        }