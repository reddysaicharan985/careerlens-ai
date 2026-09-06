import os

from dotenv import load_dotenv


load_dotenv()


def get_api_key(name: str) -> str:
    """
    Load an API key or configuration value.

    Works locally with .env and on Streamlit Cloud
    with root-level Streamlit Secrets.
    """

    value = os.getenv(name, "").strip()

    if not value:
        raise RuntimeError(
            f"{name} was not found in the environment."
        )

    return value


def get_cerebras_api_key():
    return get_api_key("CEREBRAS_API_KEY")


def get_groq_api_key():
    return get_api_key("GROQ_API_KEY")


def get_google_api_key():
    return get_api_key("GOOGLE_API_KEY")


def get_cloudflare_api_token():
    return get_api_key("CLOUDFLARE_API_TOKEN")


def get_cloudflare_account_id():
    return get_api_key("CLOUDFLARE_ACCOUNT_ID")


def get_openrouter_api_key():
    return get_api_key("OPENROUTER_API_KEY")