import os
from pathlib import Path
from typing import TypedDict

import chromadb
from langgraph.graph import END, START, StateGraph
from sentence_transformers import SentenceTransformer

from .prompts import SYSTEM_PROMPT, build_user_prompt
from .schemas import SupportResponse


BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "zepto_policies"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

MOCK_LLM = os.getenv("MOCK_LLM", "1") != "0"


class SupportState(TypedDict, total=False):
    query: str
    intent: str
    context: str
    sources: list[str]
    answer: str
    confidence: float
    response: dict


embedding_model = SentenceTransformer(EMBEDDING_MODEL)

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = chroma_client.get_collection(
    COLLECTION_NAME
)


def classify_intent(state: SupportState) -> SupportState:
    query = state["query"].lower()

    policy_keywords = [
        "delivery",
        "return",
        "refund",
        "membership",
        "tracking",
        "cancel",
        "gift card",
        "support hours",
    ]

    if any(keyword in query for keyword in policy_keywords):
        intent = "policy_question"
    else:
        intent = "general_question"

    return {
        **state,
        "intent": intent,
    }


def retrieve_and_answer(state: SupportState) -> SupportState:
    query = state["query"]

    query_embedding = embedding_model.encode(
        [query],
        normalize_embeddings=True,
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3,
    )

    documents = results["documents"][0]
    ids = results["ids"][0]

    context = "\n\n".join(documents)

    if MOCK_LLM:
        snippet = documents[0][:200]

        answer = f"Based on the retrieved context: {snippet}"

        response = SupportResponse(
            answer=answer,
            sources=ids,
            confidence=1.0,
        )

    else:
        # Real LLM mode will be added after the deterministic
        # mock baseline is fully verified.
        answer = (
            "Real LLM mode is not configured yet. "
            "Please use MOCK_LLM=1."
        )

        response = SupportResponse(
            answer=answer,
            sources=ids,
            confidence=0.0,
        )

    return {
        **state,
        "context": context,
        "sources": ids,
        "answer": response.answer,
        "confidence": response.confidence,
        "response": response.model_dump(),
    }


def direct_answer(state: SupportState) -> SupportState:
    response = SupportResponse(
        answer="I can only answer questions about Zepto policies right now.",
        sources=[],
        confidence=1.0,
    )

    return {
        **state,
        "answer": response.answer,
        "sources": response.sources,
        "confidence": response.confidence,
        "response": response.model_dump(),
    }


def route_by_intent(state: SupportState) -> str:
    if state["intent"] == "policy_question":
        return "retrieve_and_answer"

    return "direct_answer"


builder = StateGraph(SupportState)

builder.add_node("classify_intent", classify_intent)
builder.add_node("retrieve_and_answer", retrieve_and_answer)
builder.add_node("direct_answer", direct_answer)

builder.add_edge(START, "classify_intent")

builder.add_conditional_edges(
    "classify_intent",
    route_by_intent,
    {
        "retrieve_and_answer": "retrieve_and_answer",
        "direct_answer": "direct_answer",
    },
)

builder.add_edge("retrieve_and_answer", END)
builder.add_edge("direct_answer", END)

graph = builder.compile()


def ask_question(query: str) -> dict:
    result = graph.invoke({"query": query})
    return result["response"]