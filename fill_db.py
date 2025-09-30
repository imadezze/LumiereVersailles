import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
from langchain_text_splitters import CharacterTextSplitter
import json
import os
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = "data/rag_data"
CHROMA_PATH = "chroma_db"

gemini_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
    api_key=os.getenv("GEMINI_API_KEY"),
    model_name="models/embedding-001"
)

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(
    name="versailles_docs",
    embedding_function=gemini_ef
)

md_splitter = CharacterTextSplitter(separator="##", chunk_size=2000, chunk_overlap=200)

documents = []
metadata = []
ids = []
i = 0

for file_path in Path(DATA_PATH).rglob("*.md"):
    print(f"Processing {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    chunks = md_splitter.split_text(content)

    for chunk in chunks:
        if chunk.strip():
            documents.append(chunk.strip())
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

batch_size = 50
for i in range(0, len(documents), batch_size):
    batch_docs = documents[i:i+batch_size]
    batch_meta = metadata[i:i+batch_size]
    batch_ids = ids[i:i+batch_size]
    collection.upsert(documents=batch_docs, metadatas=batch_meta, ids=batch_ids)
    print(f"Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")

print(f"Added {len(documents)} chunks to the database")