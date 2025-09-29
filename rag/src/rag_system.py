"""
Complete RAG system for Versailles documents
"""
from pathlib import Path
from typing import List, Dict, Any
from embeddings import QwenEmbeddingService
from vector_store import VersaillesVectorStore
from document_processor import DocumentProcessor

class VersaillesRAG:
    """Complete RAG system for Versailles documents"""

    def __init__(self, data_dir: str = "data", persist_dir: str = "data/chroma_db"):
        self.data_dir = Path(data_dir)
        self.embedding_service = QwenEmbeddingService()
        self.vector_store = VersaillesVectorStore(persist_dir)
        self.processor = DocumentProcessor()

    def build_index(self):
        """Build the vector index from documents"""
        print("🏰 Building Versailles RAG Index...")

        # Process documents
        print("📄 Processing documents...")
        documents = self.processor.process_directory(self.data_dir)

        if not documents:
            print("❌ No documents found!")
            return

        # Generate embeddings
        print("🧠 Generating embeddings with Qwen3-Embedding-8B...")
        texts = [doc["text"] for doc in documents]
        embeddings = self.embedding_service.embed_texts(texts)

        # Prepare data for vector store
        metadatas = [doc["metadata"] for doc in documents]
        ids = [doc["id"] for doc in documents]

        # Store in vector database
        print("💾 Storing in vector database...")
        self.vector_store.add_documents(texts, embeddings, metadatas, ids)

        # Show statistics
        stats = self.vector_store.get_stats()
        print(f"✅ Index built successfully!")
        print(f"📊 Total documents: {stats['total_documents']}")

    def query(self, question: str, k: int = 5) -> Dict[str, Any]:
        """Query the RAG system"""
        # Generate query embedding
        query_embedding = self.embedding_service.embed_single(question)

        # Search similar documents
        results = self.vector_store.similarity_search(query_embedding, k)

        # Format response
        response = {
            "question": question,
            "results": [],
            "total_found": len(results["documents"][0]) if results["documents"] else 0
        }

        if results["documents"]:
            for i, (doc, metadata, distance) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                response["results"].append({
                    "text": doc,
                    "metadata": metadata,
                    "similarity_score": 1 - distance,  # Convert distance to similarity
                    "rank": i + 1
                })

        return response

    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return self.vector_store.get_stats()