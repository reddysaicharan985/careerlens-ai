import json
import os
import re
import time
from typing import Callable

import requests
from services.telemetry import record_provider_attempt

from config import (
    get_cerebras_api_key,
    get_cloudflare_account_id,
    get_cloudflare_api_token,
    get_google_api_key,
    get_groq_api_key,
    get_openrouter_api_key,
)


REQUEST_TIMEOUT = 60
MAX_PROVIDER_ATTEMPTS = 2
RETRY_BACKOFF_SECONDS = 0.25


# ---------------------------------------------------------
# Provider 1: Cerebras
# ---------------------------------------------------------

def _call_cerebras(system_prompt, user_prompt, max_tokens):
    response = requests.post(
        "https://api.cerebras.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {get_cerebras_api_key()}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-oss-120b",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "temperature": 0.2,
            "max_tokens": max_tokens,
        },
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"].strip()


# ---------------------------------------------------------
# Provider 2: Groq
# ---------------------------------------------------------

def _call_groq(system_prompt, user_prompt, max_tokens):
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {get_groq_api_key()}",
            "Content-Type": "application/json",
        },
        json={
            "model": "openai/gpt-oss-120b",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "temperature": 0.2,
            "max_tokens": max_tokens,
        },
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"].strip()


# ---------------------------------------------------------
# Provider 3: Google Gemini
# ---------------------------------------------------------

def _call_gemini(system_prompt, user_prompt, max_tokens):
    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-3.5-flash:generateContent"
    )

    response = requests.post(
        url,
        headers={
            "x-goog-api-key": get_google_api_key(),
            "Content-Type": "application/json",
        },
        json={
            "systemInstruction": {
                "parts": [
                    {
                        "text": system_prompt,
                    }
                ]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": user_prompt,
                        }
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": max_tokens,
            },
        },
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    return (
        data["candidates"][0]["content"]["parts"][0]["text"]
        .strip()
    )


# ---------------------------------------------------------
# Provider 4: Cloudflare Workers AI
# ---------------------------------------------------------

def _call_cloudflare(system_prompt, user_prompt, max_tokens):
    account_id = get_cloudflare_account_id()

    url = (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{account_id}/ai/v1/chat/completions"
    )

    response = requests.post(
        url,
        headers={
            "Authorization": (
                f"Bearer {get_cloudflare_api_token()}"
            ),
            "Content-Type": "application/json",
        },
        json={
            "model": "@cf/openai/gpt-oss-20b",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "temperature": 0.2,
            "max_tokens": max_tokens,
        },
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"].strip()


# ---------------------------------------------------------
# Provider 5: OpenRouter
# ---------------------------------------------------------

def _call_openrouter(system_prompt, user_prompt, max_tokens):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": (
                f"Bearer {get_openrouter_api_key()}"
            ),
            "Content-Type": "application/json",
            "HTTP-Referer": (
                "https://careerlens-by-saicharan.streamlit.app"
            ),
            "X-OpenRouter-Title": "CareerLens AI",
        },
        json={
            "model": "openrouter/free",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "temperature": 0.2,
            "max_tokens": max_tokens,
        },
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"].strip()


# ---------------------------------------------------------
# Provider order
# ---------------------------------------------------------

PROVIDERS = [
    ("Cerebras", _call_cerebras),
    ("Groq", _call_groq),
    ("Gemini", _call_gemini),
    ("Cloudflare", _call_cloudflare),
    ("OpenRouter", _call_openrouter),
]

PROVIDER_ENVIRONMENT_VARIABLES = {
    "Cerebras": ("CEREBRAS_API_KEY",),
    "Groq": ("GROQ_API_KEY",),
    "Gemini": ("GOOGLE_API_KEY",),
    "Cloudflare": ("CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID"),
    "OpenRouter": ("OPENROUTER_API_KEY",),
}


def _provider_is_configured(provider_name):
    """Check required settings without reading or exposing their values."""
    required_variables = PROVIDER_ENVIRONMENT_VARIABLES.get(provider_name, ())
    return all(os.getenv(name, "").strip() for name in required_variables)


def _record_attempt(provider_name, started, success, status=None, error_type=None):
    """Record metadata without allowing telemetry errors to affect routing."""
    try:
        record_provider_attempt(
            provider_name,
            (time.perf_counter() - started) * 1000,
            success,
            status,
            error_type,
        )
    except Exception:
        pass


def _error_metadata(error):
    """Return privacy-safe error classification and an optional HTTP status."""
    status = None
    if isinstance(error, requests.exceptions.HTTPError):
        response = getattr(error, "response", None)
        status = getattr(response, "status_code", None)
        if status in {401, 403}:
            error_type = "authentication_error"
        elif status == 429:
            error_type = "quota"
        elif status is not None and status >= 500:
            error_type = "server_error"
        else:
            error_type = "http_error"
    elif isinstance(error, requests.exceptions.Timeout):
        error_type = "timeout"
    elif isinstance(error, requests.exceptions.ConnectionError):
        error_type = "connection_error"
    elif isinstance(error, (ValueError, json.JSONDecodeError, KeyError)):
        error_type = "invalid_response"
    else:
        error_type = type(error).__name__
    return status, error_type


def _is_retryable(error_type):
    return error_type in {
        "quota",
        "server_error",
        "timeout",
        "connection_error",
        "invalid_response",
    }


def _generate_with_fallback(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    validator: Callable,
):
    """
    Try every AI provider in order.

    If a provider hits quota, rate limits, authentication
    errors, timeout, malformed output, or temporary failure,
    CareerLens automatically tries the next provider.
    """

    failures = []
    configured_provider_count = 0

    for provider_name, provider_function in PROVIDERS:
        if not _provider_is_configured(provider_name):
            started = time.perf_counter()
            _record_attempt(
                provider_name, started, False, error_type="configuration_error"
            )
            failures.append(f"{provider_name}: configuration_error")
            continue

        configured_provider_count += 1
        for attempt_number in range(1, MAX_PROVIDER_ATTEMPTS + 1):
            started = time.perf_counter()
            try:
                response_text = provider_function(
                    system_prompt,
                    user_prompt,
                    max_tokens,
                )

                if not response_text:
                    raise ValueError("Provider returned empty output.")

                result = validator(response_text)
                _record_attempt(provider_name, started, True)
                return result

            except Exception as error:
                status, error_type = _error_metadata(error)
                _record_attempt(
                    provider_name, started, False, status, error_type
                )
                failures.append(f"{provider_name}: {error_type}")

                should_retry = (
                    attempt_number < MAX_PROVIDER_ATTEMPTS
                    and _is_retryable(error_type)
                )
                if not should_retry:
                    break
                time.sleep(RETRY_BACKOFF_SECONDS)

    if configured_provider_count == 0:
        raise RuntimeError(
            "No CareerLens AI provider is configured. Configure at least one "
            "provider credential and try again."
        )

    raise RuntimeError(
        "All CareerLens AI providers are currently unavailable. "
        + " | ".join(failures)
    )


# ---------------------------------------------------------
# Plain text generation
# ---------------------------------------------------------

def generate_text(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 2000,
):
    """
    Generate normal text using the first available provider.
    """

    def validate_text(text):
        cleaned = text.strip()

        if not cleaned:
            raise ValueError("Empty AI response.")

        return cleaned

    return _generate_with_fallback(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=max_tokens,
        validator=validate_text,
    )


# ---------------------------------------------------------
# JSON extraction
# ---------------------------------------------------------

def _extract_json(text: str):
    """
    Extract a JSON object from an AI response.

    Handles:
    - plain JSON
    - ```json code blocks
    - small amounts of text around the JSON
    """

    cleaned = text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError(
                "AI provider did not return valid JSON."
            )

        candidate = cleaned[start:end + 1]

        return json.loads(candidate)


# ---------------------------------------------------------
# Structured generation
# ---------------------------------------------------------

def generate_structured(
    system_prompt: str,
    user_prompt: str,
    schema: dict,
    max_tokens: int = 3000,
):
    """
    Generate JSON matching a supplied Pydantic JSON schema.

    The calling CareerLens service still performs final
    Pydantic validation.
    """

    schema_text = json.dumps(
        schema,
        indent=2,
        ensure_ascii=False,
    )

    structured_system_prompt = f"""
{system_prompt}

IMPORTANT OUTPUT FORMAT:

Return ONLY one valid JSON object.

Do not include Markdown.
Do not include ```json.
Do not include explanations before or after the JSON.

The JSON must follow this schema:

{schema_text}
""".strip()

    return _generate_with_fallback(
        system_prompt=structured_system_prompt,
        user_prompt=user_prompt,
        max_tokens=max_tokens,
        validator=_extract_json,
    )
