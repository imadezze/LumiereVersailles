"""
Document processor for Versailles extracted documents
"""
from pathlib import Path
from typing import List, Dict, Any
import re
import json

class DocumentProcessor:
    """Process and chunk Versailles documents for RAG"""

    def __init__(self, chunk_size: int = 2000, chunk_overlap: int = 200):
        """
        Initialize document processor
        chunk_size: characters per chunk (~500 tokens for 2000 chars, well under 8192 limit)
        chunk_overlap: characters of overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_chunk_chars = 6000  # Hard limit: ~1500 tokens, safely under 8192

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

    def load_jsonl_documents(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load documents from JSONL file"""
        documents = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        documents.append({
                            "content": data.get("text", ""),
                            "url": data.get("url", ""),
                            "filename": file_path.name,
                            "path": str(file_path)
                        })
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON line: {e}")
        return documents

    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return "Untitled"

    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap, enforcing max size"""
        # If text is short enough, return as is
        if len(text) <= self.chunk_size:
            return [text]

        # Split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            # Force split if single sentence exceeds max chunk size
            if sentence_length > self.max_chunk_chars:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_length = 0

                # Split long sentence into smaller pieces
                for i in range(0, len(sentence), self.max_chunk_chars):
                    chunks.append(sentence[i:i + self.max_chunk_chars])
                continue

            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Check if chunk exceeds hard limit
                chunk_text = ' '.join(current_chunk)
                if len(chunk_text) > self.max_chunk_chars:
                    # Force split oversized chunk
                    for i in range(0, len(chunk_text), self.max_chunk_chars):
                        chunks.append(chunk_text[i:i + self.max_chunk_chars])
                else:
                    chunks.append(chunk_text)

                # Start new chunk with overlap
                overlap_text = ' '.join(current_chunk[-2:]) if len(current_chunk) >= 2 else ''
                current_chunk = [overlap_text, sentence] if overlap_text else [sentence]
                current_length = len(overlap_text) + sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            # Check final chunk size
            if len(chunk_text) > self.max_chunk_chars:
                for i in range(0, len(chunk_text), self.max_chunk_chars):
                    chunks.append(chunk_text[i:i + self.max_chunk_chars])
            else:
                chunks.append(chunk_text)

        return [chunk.strip() for chunk in chunks if chunk.strip()]

    def process_directory(self, data_dir: Path) -> List[Dict[str, Any]]:
        """Process all markdown and JSONL files in directory"""
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
                            "total_chunks": len(chunks),
                            "source_type": "markdown"
                        },
                        "id": f"{doc['filename']}_chunk_{i}"
                    })

            except Exception as e:
                print(f"Error processing {md_file}: {e}")

        # Find all JSONL files
        jsonl_files = list(data_dir.rglob("*.jsonl"))
        print(f"Found {len(jsonl_files)} JSONL files")

        for jsonl_file in jsonl_files:
            try:
                docs = self.load_jsonl_documents(jsonl_file)
                print(f"  Loading {len(docs)} entries from {jsonl_file.name}")

                for doc_idx, doc in enumerate(docs):
                    if not doc["content"]:
                        continue

                    chunks = self.chunk_text(doc["content"])

                    for i, chunk in enumerate(chunks):
                        processed_docs.append({
                            "text": chunk,
                            "metadata": {
                                "filename": doc["filename"],
                                "path": doc["path"],
                                "url": doc["url"],
                                "chunk_id": i,
                                "total_chunks": len(chunks),
                                "doc_index": doc_idx,
                                "source_type": "jsonl"
                            },
                            "id": f"{doc['filename']}_doc_{doc_idx}_chunk_{i}"
                        })

            except Exception as e:
                print(f"Error processing {jsonl_file}: {e}")

        print(f"Created {len(processed_docs)} document chunks")
        return processed_docs