import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from mistralai import Mistral
from dotenv import load_dotenv
import os

load_dotenv()

CHROMA_PATH = "chroma_db"

embedding_function = SentenceTransformerEmbeddingFunction(model_name="sentence-transformers/all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(
    name="versailles_docs",
    embedding_function=embedding_function
)

user_query = input("What do you want to know about Versailles?\n\n")

results = collection.query(query_texts=[user_query], n_results=4)

print(results['documents'])

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

system_prompt = """
You are a helpful assistant for planning visits to the Palace of Versailles.
Answer only based on the provided information. Don't use your internal knowledge.
If you don't know the answer, just say: I don't know
--------------------
The data:
"""+str(results['documents'])+"""
"""

response = client.chat.complete(
    model="mistral-large-latest",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
)

print("\n\n---------------------\n\n")
print(response.choices[0].message.content)