"""Thin wrapper around the Google Gemini API that forces structured
(schema-validated) output using Gemini's structured output feature (a
Pydantic model passed directly as `response_schema`), so downstream code
never parses free-text model output."""

from __future__ import annotations

import os
import time
from typing import Type, TypeVar

from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-lite-latest")

_RETRYABLE_STATUS_CODES = {429, 500, 503}
_MAX_ATTEMPTS = 3
_RETRY_BACKOFF_SECONDS = 2
_REQUEST_TIMEOUT_MS = 45_000


def get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to a .env file (see .env.example) "
            "or export it in your shell before running the app."
        )
    return genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=_REQUEST_TIMEOUT_MS))


def call_structured(
    system: str,
    user_prompt: str,
    schema: Type[T],
    model: str = DEFAULT_MODEL,
    max_tokens: int = 4096,
) -> T:
    """Call the model and parse its response into `schema`, retrying on
    transient server errors (rate limits, temporary unavailability) or a
    missing parsed result."""
    client = get_client()

    last_error: Exception | None = None
    for attempt in range(_MAX_ATTEMPTS):
        try:
            response = client.models.generate_content(
                model=model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    response_mime_type="application/json",
                    response_schema=schema,
                    max_output_tokens=max_tokens,
                ),
            )
        except genai_errors.APIError as exc:
            last_error = exc
            if getattr(exc, "code", None) in _RETRYABLE_STATUS_CODES and attempt < _MAX_ATTEMPTS - 1:
                time.sleep(_RETRY_BACKOFF_SECONDS * (attempt + 1))
                continue
            raise
        except Exception as exc:  # noqa: BLE001, e.g. request timeouts, connection errors
            last_error = exc
            if attempt < _MAX_ATTEMPTS - 1:
                time.sleep(_RETRY_BACKOFF_SECONDS * (attempt + 1))
                continue
            raise RuntimeError(f"Gemini request failed: {exc}") from exc
        else:
            if response.parsed is not None:
                return response.parsed
            last_error = RuntimeError(
                f"Model did not return a parsed structured result (raw text: {response.text!r})"
            )
            if attempt < _MAX_ATTEMPTS - 1:
                time.sleep(_RETRY_BACKOFF_SECONDS)

    raise RuntimeError(f"Failed to get structured output from model: {last_error}")
