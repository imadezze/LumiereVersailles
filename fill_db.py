import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from pathlib import Path
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker import HierarchicalChunker
from transformers import AutoTokenizer
import json

DATA_PATH = "data/rag_data"
CHROMA_PATH = "chroma_db"

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-7B")
embedding_function = SentenceTransformerEmbeddingFunction(model_name="sentence-transformers/all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(
    name="versailles_docs",
    embedding_function=embedding_function
)

converter = DocumentConverter()
chunker = HierarchicalChunker(tokenizer=tokenizer, merge_peers=True)

documents = []
metadata = []
ids = []
i = 0

for file_path in Path(DATA_PATH).rglob("*.md"):
    print(f"Processing {file_path}")
    doc = converter.convert(str(file_path)).document
    chunks = list(chunker.chunk(dl_doc=doc))

    for chunk in chunks:
        documents.append(chunk.text)
        ids.append(f"ID{i}")
        metadata.append({"source": str(file_path), "type": "markdown"})
        i += 1

for file_path in Path(DATA_PATH).rglob("*.jsonl"):
    print(f"Processing {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                text = json.dumps(entry, ensure_ascii=False)
                documents.append(text)
                ids.append(f"ID{i}")
                metadata.append({"source": str(file_path), "type": "jsonl"})
                i += 1

collection.upsert(documents=documents, metadatas=metadata, ids=ids)
print(f"Added {len(documents)} chunks to the database")