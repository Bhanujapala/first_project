from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma_db"

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = client.get_collection("zepto_policies")

query = "How much does delivery cost for orders below INR 149?"

query_embedding = model.encode(
    [query],
    normalize_embeddings=True,
).tolist()

results = collection.query(
    query_embeddings=query_embedding,
    n_results=3,
)

print("Query:")
print(query)

print("\nRetrieved documents:")

for i, document in enumerate(results["documents"][0], start=1):
    print(f"\n--- Result {i} ---")
    print(document)