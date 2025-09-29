"""
Document processor for Versailles extracted documents
"""
from pathlib import Path
from typing import List, Dict, Any
import re

class DocumentProcessor:
    """Process and chunk Versailles documents for RAG"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_document(self, file_path: Path) -> Dict[str, Any]:
        """Load a markdown document"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            "content": content,
            "filename": file_path.name,
            "path": str(file_path),
            "title": self._extract_title(content)
        }

    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return "Untitled"

    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap"""
        # Split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append(' '.join(current_chunk))

                # Start new chunk with overlap
                overlap_text = ' '.join(current_chunk[-2:]) if len(current_chunk) >= 2 else ''
                current_chunk = [overlap_text, sentence] if overlap_text else [sentence]
                current_length = len(overlap_text) + sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        # Add final chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return [chunk.strip() for chunk in chunks if chunk.strip()]

    def process_directory(self, data_dir: Path) -> List[Dict[str, Any]]:
        """Process all markdown files in directory"""
        processed_docs = []

        # Find all markdown files
        md_files = list(data_dir.rglob("*.md"))
        print(f"Found {len(md_files)} markdown files")

        for md_file in md_files:
            try:
                doc = self.load_document(md_file)
                chunks = self.chunk_text(doc["content"])

                for i, chunk in enumerate(chunks):
                    processed_docs.append({
                        "text": chunk,
                        "metadata": {
                            "filename": doc["filename"],
                            "path": doc["path"],
                            "title": doc["title"],
                            "chunk_id": i,
                            "total_chunks": len(chunks)
                        },
                        "id": f"{doc['filename']}_chunk_{i}"
                    })

            except Exception as e:
                print(f"Error processing {md_file}: {e}")

        print(f"Created {len(processed_docs)} document chunks")
        return processed_docs