from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic

PROVIDER_MAP = {
    "gemini": {
        "class": ChatGoogleGenerativeAI,
        "default_model": "gemini-2.5-flash",
    },
    "openai": {
        "class": ChatOpenAI,
        "default_model": "gpt-4o-mini",
    },
    "anthropic": {
        "class": ChatAnthropic,
        "default_model": "claude-3-haiku-20240307",
    },
}