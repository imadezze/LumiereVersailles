"""
RAG (Retrieval-Augmented Generation) tools for the Versailles Agent
"""
import sys
from pathlib import Path
from typing import Dict, Any, List
from langchain_core.tools import tool

# Add RAG src directory to path
project_root = Path(__file__).parent.parent.parent
rag_src_path = project_root / "rag" / "src"
sys.path.append(str(rag_src_path))

try:
    from rag_system import VersaillesRAG
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ RAG system not available: {e}")
    RAG_AVAILABLE = False

# Global RAG instance
_rag_instance = None


def initialize_rag_system(data_dir: str = None, persist_dir: str = None):
    """
    Initialize the RAG system with the vector database

    Args:
        data_dir: Directory containing the data files (optional)
        persist_dir: Directory for the vector database (optional)
    """
    global _rag_instance

    if not RAG_AVAILABLE:
        print("❌ Cannot initialize RAG: RAG system not available")
        return False

    try:
        if data_dir is None:
            data_dir = str(project_root / "data")
        if persist_dir is None:
            persist_dir = str(project_root / "rag" / "data" / "chroma_db")

        print(f"🔧 Initializing RAG system...")
        print(f"   Data dir: {data_dir}")
        print(f"   Persist dir: {persist_dir}")

        _rag_instance = VersaillesRAG(data_dir=data_dir, persist_dir=persist_dir)

        # Check if database exists
        stats = _rag_instance.get_stats()
        print(f"✅ RAG system initialized with {stats['total_documents']} documents")

        return True

    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {e}")
        return False


@tool
def search_versailles_knowledge(query: str, max_results: int = 5) -> str:
    """
    Search the Versailles knowledge base for information about the palace, gardens, history, visit tips, etc.

    Use this tool to find detailed information about:
    - Palace history and architecture
    - Gardens, fountains, and outdoor spaces
    - Visit information (tickets, hours, access, transportation)
    - Historical figures and events
    - Practical tips for visitors
    - Exhibitions and events
    - Restaurants and facilities
    - Accessibility information

    Args:
        query: The question or topic to search for
        max_results: Maximum number of results to return (default: 5)

    Returns:
        JSON string with search results containing relevant information
    """
    import json

    try:
        if not RAG_AVAILABLE or _rag_instance is None:
            return json.dumps({
                "status": "error",
                "error": "Knowledge base not available. RAG system not initialized."
            }, ensure_ascii=False)

        print(f"📚 Searching knowledge base for: {query}")

        # Query the RAG system
        results = _rag_instance.query(query, k=max_results)

        print(f"✅ Found {results['total_found']} relevant results")
        print(f"\n{'='*80}")
        print(f"RAG SEARCH RESULTS FOR: {query}")
        print(f"{'='*80}\n")

        # Format results for the LLM
        formatted_results = {
            "status": "success",
            "query": query,
            "total_found": results["total_found"],
            "results": []
        }

        for i, result in enumerate(results["results"], 1):
            source = result["metadata"].get("url", result["metadata"].get("filename", "unknown"))
            score = round(result["similarity_score"], 3)
            full_text = result["text"]

            print(f"Result {i}/{max_results} (Score: {score})")
            print(f"Source: {source}")
            print(f"Text ({len(full_text)} chars):\n{full_text}")
            print(f"{'-'*80}\n")

            formatted_results["results"].append({
                "text": result["text"],
                "source": source,
                "relevance_score": score,
                "rank": result["rank"]
            })

        print(f"{'='*80}\n")
        return json.dumps(formatted_results, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Error searching knowledge base: {str(e)}"
        }, ensure_ascii=False)


def get_all_rag_tools() -> List:
    """
    Get all available RAG tools

    Returns:
        List of RAG tools
    """
    if not RAG_AVAILABLE:
        return []

    return [search_versailles_knowledge]