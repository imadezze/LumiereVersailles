# RAG System Architecture - Lumière Versailles

**Last Updated:** September 30, 2025

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Data Flow](#data-flow)
4. [Components Deep Dive](#components-deep-dive)
5. [Indexing Pipeline](#indexing-pipeline)
6. [Query Pipeline](#query-pipeline)
7. [Integration with Agent](#integration-with-agent)
8. [Configuration](#configuration)

---

## Overview

The RAG (Retrieval-Augmented Generation) system enables the Versailles agent to access a comprehensive knowledge base of information about the Palace of Versailles. Instead of relying solely on the LLM's training data, the agent can search and retrieve specific, up-to-date information from official Versailles documentation.

### What is RAG?

RAG combines two key technologies:
- **Retrieval**: Searching a vector database for relevant information
- **Generation**: Using an LLM to synthesize retrieved information into natural responses

### Why RAG?

1. **Accurate Information**: Access to official Versailles documentation
2. **Up-to-date Data**: Information can be updated without retraining the LLM
3. **Source Attribution**: Responses can cite specific URLs and sources
4. **Reduced Hallucinations**: LLM grounds responses in retrieved facts

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VERSAILLES AGENT                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  LLM (Mistral/OpenAI)                                │  │
│  │  - Receives user query                               │  │
│  │  - Decides to use RAG tool                          │  │
│  │  - Synthesizes retrieved info into response         │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓ ↑                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  RAG Tool (search_versailles_knowledge)              │  │
│  │  Location: agents/tools/rag_tools.py                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                    RAG SYSTEM BACKEND                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  VersaillesRAG (rag/src/rag_system.py)              │  │
│  │  - Main orchestrator                                 │  │
│  │  - Handles queries and indexing                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓ ↑                                │
│  ┌────────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Embedding      │  │ Vector Store │  │ Document      │  │
│  │ Service        │  │ (ChromaDB)   │  │ Processor     │  │
│  │                │  │              │  │               │  │
│  │ embeddings.py  │  │vector_store  │  │document_      │  │
│  │                │  │.py           │  │processor.py   │  │
│  └────────────────┘  └──────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                              │
│  - data/other/versailles_concentrated_filtered.jsonl        │
│  - 343 documents from chateauversailles.fr                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Indexing Phase (One-time / When updating)

```
Raw Data → Document Processing → Chunking → Embedding → Vector Storage
   ↓              ↓                  ↓           ↓            ↓
 JSONL    Extract & Clean      Split text   Generate    Save to
 files     from URLs           into chunks  vectors     ChromaDB
```

**Flow Details:**
1. Load JSONL files from `data/other/`
2. Extract text content (scraped from chateauversailles.fr)
3. Split into semantic chunks (2000-6000 chars)
4. Generate embeddings using Mistral API or local model
5. Store in ChromaDB with metadata (URL, title, etc.)

### 2. Query Phase (Real-time)

```
User Question → Embedding → Vector Search → Top-K Results → LLM → Response
      ↓             ↓             ↓              ↓           ↓        ↓
"tarif enfant"  Generate    Similarity    5 most       Synthesize  Natural
                 query       search       relevant      information answer
                 vector                   chunks
```

**Flow Details:**
1. User asks: "Quel est le tarif pour un enfant de 10 ans?"
2. Agent decides to use `search_versailles_knowledge` tool
3. Query text is embedded using same model as indexing
4. ChromaDB performs cosine similarity search
5. Returns top 5 most similar chunks with scores
6. LLM receives all 5 chunks as context
7. LLM generates natural response in user's language

---

## Components Deep Dive

### 1. Document Processor (`rag/src/document_processor.py`)

**Purpose:** Converts raw documents into searchable chunks

**Key Responsibilities:**
- Load JSONL files containing web-scraped Versailles content
- Extract text, URLs, and metadata
- Split text into semantic chunks using intelligent strategies
- Handle various document sizes (40 chars to 62,000+ chars)

**Chunking Strategy (Current):**
- **Small docs (<2000 chars)**: Keep whole
- **Medium/Large docs**: Split by sentences
- **Target size**: 2000 characters per chunk (~500 tokens)
- **Max size**: 6000 characters per chunk (~1500 tokens, safely under 8192 API limit)
- **Overlap**: 200 characters between chunks for context continuity

**Key Methods:**
- `load_jsonl_documents()`: Parse JSONL files
- `chunk_text()`: Intelligent sentence-based chunking with size enforcement
- `process_directory()`: Orchestrates processing of all files

**Output:**
- From 343 documents → ~5,799 searchable chunks
- Each chunk includes metadata: URL, filename, chunk position, original length

---

### 2. Embedding Service (`rag/src/embeddings.py`)

**Purpose:** Convert text into numerical vectors (embeddings)

**What are Embeddings?**
Embeddings are numerical representations of text that capture semantic meaning. Similar texts have similar vectors, enabling similarity search.

**Supported Models:**
1. **Mistral AI API** (mistral-embed)
   - Cloud-based, requires API key
   - Fast for small batches (3 texts at once)
   - Currently configured model

2. **Local Models** (Qwen/Qwen3-Embedding-0.6B)
   - Runs on your machine (CPU/GPU/MPS)
   - No API costs, but slower
   - Useful for development

**Configuration:**
- Set in `rag/.env`:
  - `USE_LOCAL_MODEL=False` → Use Mistral API
  - `EMBEDDING_MODEL=Linq-AI-Research/Linq-Embed-Mistral` → Model name
  - `MISTRAL_API_KEY=your_key` → API authentication

**Key Methods:**
- `embed_texts()`: Generate embeddings for multiple texts (batched)
- `embed_single()`: Generate embedding for one text (queries)
- `_embed_texts_mistral_api()`: Mistral API implementation with retry logic

**Performance:**
- Processes texts in batches (currently 3-5 at a time)
- Shows progress every 50 items
- Handles API rate limits and errors gracefully

---

### 3. Vector Store (`rag/src/vector_store.py`)

**Purpose:** Store and search embeddings efficiently

**Technology:** ChromaDB (open-source vector database)
- Persistent storage on disk (`rag/data/chroma_db/`)
- Fast cosine similarity search
- Automatic indexing with HNSW algorithm

**Key Features:**
- **Persistent storage**: Data survives restarts
- **Batched insertion**: Adds documents in chunks of 1000 to avoid memory errors
- **Metadata support**: Stores URLs, titles, chunk info alongside vectors
- **Similarity search**: Finds top-K most similar documents to a query

**Key Methods:**
- `add_documents()`: Store embeddings with metadata (batched for safety)
- `similarity_search()`: Find K most similar chunks to query embedding
- `get_stats()`: Return database statistics (document count, etc.)

**Storage Format:**
```
chroma_db/
├── chroma.sqlite3        # SQLite database with metadata
└── [index files]         # Vector index for fast search
```

---

### 4. RAG System Orchestrator (`rag/src/rag_system.py`)

**Purpose:** Main coordinator that ties everything together

**Key Responsibilities:**
- Initialize all components (embedding service, vector store, processor)
- Orchestrate indexing pipeline
- Handle queries with proper error handling
- Manage batch processing for reliability

**Key Methods:**

**`build_index(batch_size=500)`**: Indexing Pipeline
- Processes documents in batches (default: 500)
- For each batch:
  1. Extract document chunks
  2. Generate embeddings
  3. Save to vector store immediately
- **Why batches?** Prevents data loss if process crashes
- Progress saved after each batch

**`query(question, k=5)`**: Query Pipeline
- Embed the question using same model
- Search vector store for top K similar chunks
- Format results with metadata and scores
- Return structured response

**Error Handling:**
- Catches embedding API failures
- Handles vector store capacity limits
- Saves progress incrementally

---

## Indexing Pipeline

### When to Run Indexing?

**Run indexing when:**
- First time setting up RAG
- Data sources are updated (new JSONL files)
- Changing embedding models
- Improving chunking strategy

**How to Run:**
```bash
cd rag
python scripts/build_index.py
```

### Indexing Steps (Detailed)

**Step 1: Document Loading**
- Location: `document_processor.py` → `process_directory()`
- Scans `data/other/` for JSONL files
- Loads each line as a JSON document
- Extracts: `text`, `url` fields

**Step 2: Chunking**
- Location: `document_processor.py` → `chunk_text()`
- Splits text by sentence boundaries (`.!?`)
- Groups sentences into chunks ~2000 chars
- Enforces 6000 char hard limit for API safety
- Creates overlap between chunks (200 chars)
- Result: 343 docs → 5,799 chunks

**Step 3: Batch Processing**
- Location: `rag_system.py` → `build_index()`
- Processes 500 chunks at a time
- Why? Memory efficiency + save progress
- Total: 12 batches for 5,799 chunks

**Step 4: Embedding Generation**
- Location: `embeddings.py` → `embed_texts()`
- For each text, call Mistral API
- Processes 3-5 texts per API call (batch optimization)
- Returns 1024-dimensional vectors (model-specific)
- Shows progress every 50 items

**Step 5: Vector Storage**
- Location: `vector_store.py` → `add_documents()`
- Saves embeddings + metadata to ChromaDB
- Batches of 1000 for ChromaDB safety
- Persists to disk: `rag/data/chroma_db/`

**Performance:**
- Total time: ~2-3 hours for 5,799 chunks (Mistral API)
- Or ~10-15 minutes with local model
- Progress saved every 500 chunks

### Index Statistics

After successful indexing:
```
Total documents in database: 5,799
Collection name: versailles_documents
Storage size: ~50-100 MB (embeddings + metadata)
```

---

## Query Pipeline

### User Query → RAG → Response Flow

**Example Query:** "Quel est le tarif pour un enfant de 10 ans?"

### Step-by-Step Execution

**Step 1: Tool Invocation**
- Location: `agents/core/simple_agent.py`
- LLM decides to call `search_versailles_knowledge` tool
- Extracts query: `"tarif enfant 10 ans Versailles"`
- Passes to RAG tool handler

**Step 2: RAG Tool Execution**
- Location: `agents/tools/rag_tools.py` → `search_versailles_knowledge()`
- Validates RAG system is initialized
- Logs query: `📚 Searching knowledge base for: tarif enfant 10 ans Versailles`
- Calls RAG system query method

**Step 3: Query Embedding**
- Location: `rag_system.py` → `query()` → `embed_single()`
- Embeds query text using same model as indexing
- Generates 1024-dimensional query vector
- Uses `embeddings.py` → `_embed_texts_mistral_api()` or local

**Step 4: Vector Search**
- Location: `vector_store.py` → `similarity_search()`
- ChromaDB performs cosine similarity search
- Compares query vector to all 5,799 document vectors
- Returns top 5 most similar chunks
- Includes: text, metadata, similarity score (0-1)

**Step 5: Results Formatting**
- Location: `rag_tools.py` → result formatting
- For each of 5 results:
  - Extract full text (potentially 2000-6000 chars)
  - Get source URL from metadata
  - Calculate relevance score (e.g., 0.856 = 85.6% similar)
  - Assign rank (1-5)

**Logging Output:**
```
✅ Found 5 relevant results
================================================================================
RAG SEARCH RESULTS FOR: tarif enfant 10 ans Versailles
================================================================================

Result 1/5 (Score: 0.856)
Source: https://www.chateauversailles.fr/preparer-ma-visite/tarifs
Text (2341 chars):
[Full chunk text about tarifs for children...]
--------------------------------------------------------------------------------
[... 4 more results ...]
```

**Step 6: Return to LLM**
- Location: `rag_tools.py` → returns JSON
- Format:
```json
{
  "status": "success",
  "query": "tarif enfant 10 ans Versailles",
  "total_found": 5,
  "results": [
    {
      "text": "Full text of chunk 1...",
      "source": "https://...",
      "relevance_score": 0.856,
      "rank": 1
    }
    // ... 4 more
  ]
}
```

**Step 7: LLM Synthesis**
- Location: `agents/core/simple_agent.py` → LLM invocation
- LLM receives:
  - Original user question
  - All 5 chunks (full text)
  - Source URLs
  - Relevance scores
- LLM reads all 5 chunks
- Synthesizes information
- Generates natural response in user's language
- Can cite sources if needed

**Step 8: Response to User**
- Final answer displayed in chat interface
- Shows tool usage indicator (📚 Base de connaissances)
- User sees: "Les enfants de 10 ans bénéficient de la gratuité..."

### Similarity Scores Explained

**Score Range: 0.0 to 1.0**
- **0.9-1.0**: Excellent match (nearly identical meaning)
- **0.8-0.9**: Very relevant (strong semantic similarity)
- **0.7-0.8**: Relevant (good match, useful context)
- **0.6-0.7**: Somewhat relevant (may contain useful info)
- **<0.6**: Less relevant (usually filtered out)

**How Scores Work:**
- Cosine similarity between query and document vectors
- Measures "closeness" in high-dimensional space
- Similar meaning → similar vectors → high score
- Different meaning → distant vectors → low score

---

## Integration with Agent

### Agent Architecture

**Location:** `agents/core/simple_agent.py`

**Components:**
1. **LLM**: Mistral or OpenAI model
2. **Tools**: Weather, Travel, RAG (knowledge base)
3. **System Prompt**: Instructions from `agents/prompts/`
4. **Conversation History**: Maintains context

### RAG Tool Registration

**Location:** `agents/tools/rag_tools.py`

**Tool Definition:**
- Name: `search_versailles_knowledge`
- Description: "Search the Versailles knowledge base for information..."
- Parameters:
  - `query` (string): The search query
  - `max_results` (int): Number of results (default: 5)

**When Agent Uses RAG:**
The LLM autonomously decides to use RAG when:
- User asks about Versailles-specific information
- Questions about: history, tickets, hours, gardens, events, etc.
- Agent needs factual information not in training data

**Tool Instructions:**
- Location: `agents/prompts/rag_tool_prompt.md`
- Provides guidance to LLM on:
  - When to use the tool
  - How to formulate queries
  - How to synthesize results
  - Example use cases

### Initialization Flow

**Location:** `agents/core/simple_agent.py` → `__init__()`

1. **Agent starts**
2. **Initialize RAG system:**
   - Calls `initialize_rag_system()` from `rag_tools.py`
   - Sets paths:
     - Data: `/data/other/`
     - Database: `/rag/data/chroma_db/`
3. **Create RAG instance:**
   - Loads existing ChromaDB collection
   - Initializes embedding service
   - No indexing needed (uses pre-built index)
4. **Register tools:**
   - Add `search_versailles_knowledge` to agent's tools
   - LLM can now invoke RAG searches

**Success Message:**
```
🔧 Initializing RAG knowledge base...
✅ RAG system initialized with 5799 documents
✅ RAG knowledge base ready with 1 tools
```

---

## Configuration

### Environment Variables

**Location:** `rag/.env`

```bash
# Embedding Model Configuration
USE_LOCAL_MODEL=False                                # false = API, true = local
EMBEDDING_MODEL=Linq-AI-Research/Linq-Embed-Mistral # Model name

# API Keys
MISTRAL_API_KEY=your_key_here                        # For Mistral embeddings
HUGGINGFACE_API_TOKEN=your_token                     # For HF models (optional)
```

### Chunking Parameters

**Location:** `rag/src/document_processor.py` → `__init__()`

```python
chunk_size: 2000        # Target chunk size in characters (~500 tokens)
chunk_overlap: 200      # Overlap between chunks (maintains context)
max_chunk_chars: 6000   # Hard limit to prevent API errors (~1500 tokens)
```

**Tuning Recommendations:**
- **Smaller chunks** (1000-2000): Better precision, more API calls
- **Larger chunks** (4000-6000): More context, fewer chunks, faster
- **Overlap**: 10-20% of chunk size for continuity

### Vector Store Settings

**Location:** `rag/src/vector_store.py`

```python
persist_directory: "data/chroma_db"       # Storage location
collection_name: "versailles_documents"   # ChromaDB collection
hnsw:space: "cosine"                     # Similarity metric (cosine recommended)
```

### Query Parameters

**Location:** `agents/tools/rag_tools.py` → `search_versailles_knowledge()`

```python
max_results: 5          # Top-K results to return (default)
```

**Tuning Recommendations:**
- **k=3**: Fast, focused answers
- **k=5**: Balanced (current default)
- **k=10**: Comprehensive, but more tokens for LLM

---

## Performance Considerations

### Indexing Performance

**Bottleneck:** Embedding generation (API calls)

**Current:**
- 5,799 chunks × ~2 seconds = ~3 hours (Mistral API)
- Batch size: 3-5 texts per API call

**Optimization Options:**
1. **Use local model**: 10-15 minutes total
2. **Increase API batch size**: If Mistral allows larger batches
3. **Reduce chunks**: Better document chunking strategy
4. **Cache embeddings**: Save embeddings to avoid re-generation

### Query Performance

**Typical Query Time:** 2-5 seconds

**Breakdown:**
- Query embedding: ~1-2 seconds (API call)
- Vector search: <100ms (ChromaDB is very fast)
- Result formatting: <10ms
- LLM synthesis: 2-3 seconds (depends on model)

**Fast because:**
- ChromaDB uses HNSW algorithm (approximate nearest neighbor)
- Pre-built indexes
- Local disk storage

### Memory Usage

**Indexing:** ~2-4 GB RAM
- Batching prevents loading all documents at once
- ChromaDB handles memory efficiently

**Query:** <500 MB RAM
- Only loads relevant chunks
- Embedding service keeps model in memory

---

## Future Improvements

### Semantic Chunking (Planned)

**Current Issue:** Fixed-size chunks can split related information

**Proposed Solution:**
- Use sentence embeddings to detect topic shifts
- Group semantically related sentences together
- Location: `rag/src/document_processor_semantic.py` (created)

**Benefits:**
- Better context preservation
- More relevant retrievals
- Fewer, higher-quality chunks

### Hybrid Search

**Current:** Pure vector search (semantic similarity)

**Proposed:** Combine with keyword search (BM25)
- Vector search: "what it means"
- Keyword search: "what it says"
- Combined: Best of both worlds

### Re-ranking

**Add a re-ranking step after initial retrieval:**
1. Get top 20 results from vector search
2. Use cross-encoder model to re-rank
3. Return top 5 after re-ranking

**Benefits:** More accurate results, better than just vector similarity

### Metadata Filtering

**Add filters to queries:**
- Search only specific sections (gardens, tickets, history)
- Filter by date (for events)
- Filter by audience (families, students, etc.)

---

## Troubleshooting

### RAG Not Initializing

**Symptoms:** `⚠️ RAG knowledge base not available`

**Solutions:**
1. Check ChromaDB exists: `rag/data/chroma_db/chroma.sqlite3`
2. Rebuild index: `cd rag && python scripts/build_index.py`
3. Check logs for errors during initialization

### Poor Retrieval Quality

**Symptoms:** Irrelevant results, low scores

**Solutions:**
1. Check chunk size (too small/large?)
2. Verify embedding model matches between indexing and querying
3. Try increasing `max_results` (k=10)
4. Review chunking strategy in logs
5. Consider semantic chunking

### Slow Queries

**Symptoms:** RAG searches take >5 seconds

**Solutions:**
1. Check if using API embeddings (slower than local)
2. Switch to local model for query embeddings
3. Reduce `max_results` (k=3)
4. Check ChromaDB disk I/O performance

---

## References

### Code Locations

**RAG Core:**
- `rag/src/rag_system.py` - Main orchestrator
- `rag/src/embeddings.py` - Embedding generation
- `rag/src/vector_store.py` - ChromaDB interface
- `rag/src/document_processor.py` - Document chunking

**Agent Integration:**
- `agents/tools/rag_tools.py` - RAG tool for agent
- `agents/core/simple_agent.py` - Agent initialization
- `agents/prompts/rag_tool_prompt.md` - Tool instructions

**Scripts:**
- `rag/scripts/build_index.py` - Index building script
- `rag/.env` - Configuration

**Data:**
- `data/other/versailles_concentrated_filtered.jsonl` - Source data
- `rag/data/chroma_db/` - Vector database

### Technologies Used

- **ChromaDB**: Vector database (https://www.trychroma.com/)
- **Mistral AI**: Embedding API (https://docs.mistral.ai/)
- **Sentence Transformers**: Local embedding models
- **LangChain**: Agent framework and tool integration

---

## Glossary

**Embedding**: Numerical vector representation of text capturing semantic meaning

**Vector Database**: Database optimized for storing and searching high-dimensional vectors

**Semantic Similarity**: How similar two pieces of text are in meaning (not just words)

**Cosine Similarity**: Mathematical measure of similarity between vectors (0-1 scale)

**Chunking**: Process of splitting documents into smaller, manageable pieces

**RAG (Retrieval-Augmented Generation)**: AI technique combining information retrieval with text generation

**Token**: Basic unit of text for LLMs (~4 characters on average)

**HNSW**: Hierarchical Navigable Small World - fast algorithm for approximate nearest neighbor search

---

**Document Version:** 1.0
**Last Updated:** September 30, 2025
**Maintained by:** Lumière Versailles Team