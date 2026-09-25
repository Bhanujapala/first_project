from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "zepto_policies"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def load_documents():
    documents = []
    ids = []
    metadatas = []

    for path in sorted(DOCS_DIR.glob("doc_*.txt")):
        text = path.read_text(encoding="utf-8").strip()

        if not text:
            continue

        documents.append(text)
        ids.append(path.stem)
        metadatas.append(
            {
                "document_id": path.stem,
                "source": path.name,
            }
        )

    return documents, ids, metadatas


def main():
    documents, ids, metadatas = load_documents()

    print(f"Loaded documents: {len(documents)}")

    if len(documents) != 8:
        raise ValueError(
            f"Expected 8 documents, but found {len(documents)}."
        )

    print(f"Loading embedding model: {EMBEDDING_MODEL}")

    model = SentenceTransformer(EMBEDDING_MODEL)

    embeddings = model.encode(
        documents,
        normalize_embeddings=True,
    ).tolist()

    print(f"Generated embeddings: {len(embeddings)}")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(f"Chroma collection: {COLLECTION_NAME}")
    print(f"Stored documents: {collection.count()}")
    print("Ingestion completed successfully.")


if __name__ == "__main__":
    main()
