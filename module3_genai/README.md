# Zepto Support Assistant — Module 3

## 1. Project Overview

This project implements a small RAG-based GenAI support assistant for Zepto.

The application answers customer questions using a local corpus of Zepto policy documents. The documents are embedded locally and stored in ChromaDB. LangGraph is used to classify incoming questions and route them either to a retrieval-based answer flow or to a direct answer flow.

The application is exposed through a FastAPI `/ask` endpoint.

The required graded mode is the deterministic offline mock mode using `MOCK_LLM=1` or leaving `MOCK_LLM` unset. This mode does not require an API key or an external LLM service.

### Technologies Used

- Python
- Sentence Transformers
- `all-MiniLM-L6-v2`
- ChromaDB
- LangGraph
- Pydantic
- FastAPI
- Uvicorn
- Docker
- Optional Groq LLM integration

---

## 2. Project Structure

```text
module3_genai/
├── docs/
│   ├── doc_01.txt
│   ├── doc_02.txt
│   ├── doc_03.txt
│   ├── doc_04.txt
│   ├── doc_05.txt
│   ├── doc_06.txt
│   ├── doc_07.txt
│   └── doc_08.txt
├── chroma_db/
├── requirements.txt
├── ingest.py
├── test_retrieval.py
├── prompts.py
├── schemas.py
├── graph.py
├── validation.py
├── main.py
├── Dockerfile
└── README.md

MOCK_LLM=0