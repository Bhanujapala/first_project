from pydantic import BaseModel, Field


class SupportResponse(BaseModel):
    answer: str = Field(
        ...,
        description="The answer to the customer's question.",
    )

    sources: list[str] = Field(
        default_factory=list,
        description="Document or chunk IDs used to answer the question.",
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1.",
    )