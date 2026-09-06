import json
import re
from typing import Callable

import requests

from config import (
    get_cerebras_api_key,
    get_cloudflare_account_id,
    get_cloudflare_api_token,
    get_google_api_key,
    get_groq_api_key,
    get_openrouter_api_key,
)


REQUEST_TIMEOUT = 60


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

    for provider_name, provider_function in PROVIDERS:
        try:
            response_text = provider_function(
                system_prompt,
                user_prompt,
                max_tokens,
            )

            if not response_text:
                raise ValueError("Provider returned empty output.")

            return validator(response_text)

        except Exception as error:
            failures.append(
                f"{provider_name}: "
                f"{type(error).__name__}"
            )

            continue

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