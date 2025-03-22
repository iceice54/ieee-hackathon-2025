import chromadb
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

client = chromadb.PersistentClient(path="../chroma")
collection = client.get_collection(name="knowledge_base")

embedding_model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=google_api_key)

query_text = "Recommend ways to manage emotions to reduce resistance to change and foster greater trust, resilience and optimism"
query_embedding = embedding_model.embed_query(query_text)

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5
)
print("Total documents in collection:", collection.count())  # Should return > 0

# print(results)
for i, doc in enumerate(results["documents"][0]):
    print(f"\nResult {i+1}:")
    print(f"Document: {doc}")
    print(f"Metadata: {results['metadatas'][0][i]}")
    print(f"Distance: {results['distances'][0][i]}")