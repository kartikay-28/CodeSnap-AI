"""
LLM Service Factory - Clean dependency injection
"""
from app.services.interfaces import LLMServiceInterface
from app.services.llm.openai_service import OpenAIService
from app.services.llm.groq_service import GroqService
from app.services.llm.ollama_service import OllamaService
from app.core.exceptions import ConfigurationException
from app.core.config import settings

class LLMServiceFactory:
    """Factory for creating LLM service instances"""
    
    _services = {
        "openai": OpenAIService,
        "groq": GroqService,
        "ollama": OllamaService
    }
    
    @classmethod
    def create_service(
        self, 
        provider: str = None, 
        model: str = None
    ) -> LLMServiceInterface:
        """Create LLM service instance based on provider"""
        provider = provider or settings.DEFAULT_LLM_PROVIDER
        
        if provider not in self._services:
            available = ", ".join(self._services.keys())
            raise ConfigurationException(
                f"Unknown LLM provider: {provider}. Available: {available}"
            )
        
        service_class = self._services[provider]
        return service_class(model=model)
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available LLM providers"""
        return list(cls._services.keys())