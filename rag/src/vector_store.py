"""
Vector store using ChromaDB for Versailles documents
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import os
from pathlib import Path

class VersaillesVectorStore:
    """Vector store for Versailles documents using ChromaDB"""

    def __init__(self, persist_directory: str = "data/chroma_db"):
        self.persist_directory = persist_directory
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="versailles_documents",
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, texts: List[str], embeddings: List[List[float]],
                     metadatas: List[Dict[str, Any]], ids: List[str]):
        """Add documents to the vector store"""
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        print(f"✅ Added {len(texts)} documents to vector store")

    def similarity_search(self, query_embedding: List[float], k: int = 5) -> Dict:
        """Search for similar documents"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        return results

    def get_stats(self) -> Dict:
        """Get collection statistics"""
        return {
            "total_documents": self.collection.count(),
            "collection_name": self.collection.name
        }