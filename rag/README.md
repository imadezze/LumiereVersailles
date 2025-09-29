# Versailles RAG System

Retrieval-Augmented Generation (RAG) system for Versailles documents using Qwen3-Embedding-8B.

## Setup

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Configure execution mode:
   - Copy `.env.example` to `.env`

   **For API mode (default, lightweight)**:
   - Get a token from: https://huggingface.co/settings/tokens
   - Add your token: `HF_TOKEN=your_token_here`
   - Keep `USE_LOCAL_MODEL=false`

   **For local mode (no API calls, requires ~15GB)**:
   - Set `USE_LOCAL_MODEL=true`
   - Install additional dependencies: `pip install sentence-transformers torch`

3. Ensure you have extracted documents in the `data/` folder (from the extract_pdf system)

## Usage

### Build Index

First, build the vector index from your documents:

```bash
cd scripts
python build_index.py
```

This will:
- Process all markdown files in the `data/` directory
- Generate embeddings using Qwen3-Embedding-8B
- Store vectors in ChromaDB

### Query System

Query the documents interactively:

```bash
cd scripts
python query.py
```

Example queries:
- "What are the opening hours of Versailles?"
- "How much do tickets cost?"
- "What exhibitions are available?"

## Architecture

```
rag/
├── src/
│   ├── embeddings.py      # Qwen3-Embedding-8B service
│   ├── vector_store.py    # ChromaDB vector storage
│   ├── document_processor.py  # Document chunking
│   └── rag_system.py      # Main RAG orchestrator
├── scripts/
│   ├── build_index.py     # Index builder
│   └── query.py           # Query interface
└── data/
    └── chroma_db/         # Vector database storage
```

## Features

- **High-quality embeddings**: Uses Qwen3-Embedding-8B (8B parameters)
- **Efficient storage**: ChromaDB for fast similarity search
- **Smart chunking**: Sentence-aware text splitting with overlap
- **Metadata preservation**: Keeps document structure and source information
- **Interactive queries**: Command-line interface for testing

## API Usage

```python
from src.rag_system import VersaillesRAG

# Initialize
rag = VersaillesRAG(data_dir="path/to/data")

# Build index
rag.build_index()

# Query
results = rag.query("What are the garden hours?", k=5)
for result in results["results"]:
    print(f"Score: {result['similarity_score']:.3f}")
    print(f"Text: {result['text'][:200]}...")
```