#!/usr/bin/env python3
"""
Build RAG index for Versailles documents
"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from rag_system import VersaillesRAG

def main():
    """Build the RAG index"""
    print("🏰 Versailles RAG Index Builder")
    print("=" * 50)

    # Check if data directory exists
    data_dir = Path(__file__).parent.parent.parent / "data"
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        print("Make sure you have extracted documents in the data folder")
        return

    # Initialize RAG system
    rag = VersaillesRAG(data_dir=str(data_dir))

    try:
        # Build index
        rag.build_index()

        # Show final stats
        stats = rag.get_stats()
        print(f"\n📈 Final Statistics:")
        print(f"   Total documents: {stats['total_documents']}")
        print(f"   Collection: {stats['collection_name']}")

        print(f"\n✨ Index ready for queries!")
        print(f"Use query.py to search the documents")

    except Exception as e:
        print(f"❌ Error building index: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()