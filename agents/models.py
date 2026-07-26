import os

from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

load_dotenv()

CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "anthropic/claude-sonnet-4")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:4b")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

OPENROUTER_MODEL = os.environ.get(
    "OPENROUTER_MODEL",
    "google/gemma-4-26b-a4b-it:free"
)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.environ.get(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1"
)

GEMINI_MODEL = os.environ.get(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

GROQ_MODEL = os.environ.get(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

MODEL_PROVIDER = os.environ.get("MODEL_PROVIDER", "ollama")


def get_claude_model():
    return ChatAnthropic(model=CLAUDE_MODEL)


def get_ollama_model():
    return ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
    )


def get_openrouter_model():
    return ChatOpenAI(
        model=OPENROUTER_MODEL,
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
        temperature=0,
    )

def get_gemini_model():
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
    )
    
def get_groq_model():
    return ChatGroq(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        temperature=0,
    )
    
def build_model():
    provider = MODEL_PROVIDER.lower()
    print(f"Using provider: {provider}")
    if provider == "anthropic":
        return get_claude_model()

    if provider == "openrouter":
        return get_openrouter_model()

    if provider == "gemini":
        return get_gemini_model()
    
    if provider == "groq":
        return get_groq_model()
    
    return get_ollama_model()