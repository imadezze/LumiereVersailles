#!/usr/bin/env python3
"""
Query the Versailles RAG system
"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from rag_system import VersaillesRAG

def main():
    """Interactive query interface"""
    print("🏰 Versailles RAG Query System")
    print("=" * 50)

    # Initialize RAG system
    data_dir = Path(__file__).parent.parent.parent / "data"
    rag = VersaillesRAG(data_dir=str(data_dir))

    # Check if index exists
    stats = rag.get_stats()
    if stats["total_documents"] == 0:
        print("❌ No documents in index!")
        print("Run build_index.py first to build the index")
        return

    print(f"📊 Index loaded: {stats['total_documents']} documents")
    print("💡 Ask questions about Versailles (type 'quit' to exit)")
    print("-" * 50)

    while True:
        try:
            question = input("\n🤔 Your question: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break

            if not question:
                continue

            # Query the RAG system
            print("🔍 Searching...")
            results = rag.query(question, k=3)

            print(f"\n📋 Found {results['total_found']} relevant documents:")
            print("=" * 60)

            for result in results["results"]:
                print(f"\n📄 {result['metadata']['title']}")
                print(f"📁 {result['metadata']['filename']}")
                print(f"⭐ Similarity: {result['similarity_score']:.3f}")
                print(f"📝 Content preview:")
                print("-" * 40)
                print(result["text"][:300] + "..." if len(result["text"]) > 300 else result["text"])
                print("-" * 40)

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()