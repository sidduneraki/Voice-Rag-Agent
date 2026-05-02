from app.llm.base import BaseLLM
from app.core.config import get_settings
from app.core.logger import logger

def get_llm() -> BaseLLM:
    provider = get_settings().LLM_PROVIDER.lower()
    logger.info(f"Loading LLM provider: {provider}")

    if provider == "groq":
        from app.llm.groq_llm import GroqLLM
        return GroqLLM()
    elif provider == "ollama":
        from app.llm.ollama_llm import OllamaLLM
        return OllamaLLM()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
