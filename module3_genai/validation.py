from typing import Any

from pydantic import ValidationError

from .schemas import SupportResponse


def validate_response(
    raw_output: Any,
    sources: list[str] | None = None,
) -> SupportResponse:
    """
    Validate model output against the required Pydantic schema.
    """

    if isinstance(raw_output, SupportResponse):
        return raw_output

    if isinstance(raw_output, dict):
        return SupportResponse.model_validate(raw_output)

    raise ValueError(
        "Model output must be a dictionary or SupportResponse."
    )


def validate_with_retry(
    raw_output: Any,
    sources: list[str] | None = None,
    retry_outputs: list[Any] | None = None,
) -> SupportResponse:
    """
    Validate the initial output and up to two corrective retry outputs.
    """

    attempts = [raw_output]

    if retry_outputs:
        attempts.extend(retry_outputs[:2])

    last_error = None

    for attempt in attempts:
        try:
            return validate_response(attempt, sources)
        except (ValidationError, ValueError) as exc:
            last_error = exc

    raise ValueError(
        f"Response validation failed after {len(attempts)} attempt(s): "
        f"{last_error}"
    )