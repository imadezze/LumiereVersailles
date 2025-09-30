import chromadb
from chromadb.utils import embedding_functions
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

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

user_query = input("What do you want to know about Versailles?\n\n")

results = collection.query(query_texts=[user_query], n_results=20)

print(results['documents'])

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-pro')

context = ""
for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
    source_file = meta.get('source', 'unknown')
    context += f"\n[Source: {source_file}]\n{doc}\n"

system_prompt = f"""
You are a helpful assistant for planning visits to the Palace of Versailles.
Answer only based on the provided information. Don't use your internal knowledge.
If you don't know the answer, just say: I don't know
--------------------
The data:
{context}
"""

response = model.generate_content(system_prompt + "\n\n" + user_query)

print("\n\n---------------------\n\n")
print(response.text)