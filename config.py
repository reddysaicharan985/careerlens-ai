import os

from dotenv import load_dotenv


load_dotenv()


def get_google_api_key():
    """Load and validate the Gemini API key."""

    api_key = os.getenv("GOOGLE_API_KEY", "").strip()

    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY was not found. "
            "Add it to the local .env file."
        )

    if api_key == "your_gemini_api_key_here":
        raise RuntimeError(
            "Replace the placeholder API key in .env."
        )

    return api_key