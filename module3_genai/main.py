from fastapi import FastAPI
from pydantic import BaseModel, Field

from .graph import ask_question
from .schemas import SupportResponse


app = FastAPI(
    title="Zepto Support Assistant",
    description="A LangGraph-based Zepto policy support assistant.",
    version="1.0.0",
)


class AskRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="Customer's question.",
    )


@app.get("/")
def root():
    return {
        "message": "Zepto Support Assistant is running.",
        "endpoint": "/ask",
    }


@app.post("/ask", response_model=SupportResponse)
def ask(request: AskRequest):
    return ask_question(request.query)