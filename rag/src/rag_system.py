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

    def build_index(self, batch_size: int = 100):
        """Build the vector index from documents, processing in batches"""
        print("🏰 Building Versailles RAG Index...")

        # Process documents
        print("📄 Processing documents...")
        documents = self.processor.process_directory(self.data_dir)

        if not documents:
            print("❌ No documents found!")
            return

        total_docs = len(documents)
        print(f"📊 Total documents to process: {total_docs}")
        print(f"💾 Processing in batches of {batch_size} (embeddings + storage)")

        # Process documents in batches to save progress incrementally
        for i in range(0, total_docs, batch_size):
            batch_end = min(i + batch_size, total_docs)
            batch_num = (i // batch_size) + 1
            total_batches = (total_docs + batch_size - 1) // batch_size

            print(f"\n📦 Batch {batch_num}/{total_batches} (documents {i+1} to {batch_end})")

            # Get batch data
            batch_docs = documents[i:batch_end]
            texts = [doc["text"] for doc in batch_docs]
            metadatas = [doc["metadata"] for doc in batch_docs]
            ids = [doc["id"] for doc in batch_docs]

            try:
                # Generate embeddings for this batch
                print(f"   🧠 Generating {len(texts)} embeddings...")
                embeddings = self.embedding_service.embed_texts(texts)

                # Store immediately in vector database
                print(f"   💾 Saving to database...")
                self.vector_store.add_documents(texts, embeddings, metadatas, ids)
                print(f"   ✅ Batch {batch_num}/{total_batches} saved successfully!")

            except Exception as e:
                print(f"   ❌ Error processing batch {batch_num}: {e}")
                print(f"   ⚠️ Stopping at batch {batch_num}. {i} documents saved so far.")
                raise

        # Show final statistics
        stats = self.vector_store.get_stats()
        print(f"\n✅ Index built successfully!")
        print(f"📊 Total documents in database: {stats['total_documents']}")

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