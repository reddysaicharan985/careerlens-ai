from langchain_google_genai import ChatGoogleGenerativeAI

from config import get_google_api_key


MODEL_NAME = "gemini-3.5-flash"


def create_gemini_model():
    """Create the Gemini model used by CareerLens."""

    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        api_key=get_google_api_key(),
        temperature=1.0,
        max_retries=1,
        timeout=30,
    )


def extract_response_text(response):
    """Convert Gemini response content into normal text."""

    content = response.content

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts = []

        for block in content:
            if isinstance(block, str):
                text_parts.append(block)

            elif isinstance(block, dict):
                text_parts.append(block.get("text", ""))

        return "".join(text_parts).strip()

    return str(content).strip()


def test_gemini_connection():
    """Send one small request to verify the API connection."""

    model = create_gemini_model()

    response = model.invoke(
        "Reply with exactly: CareerLens AI connection successful"
    )

    return extract_response_text(response)