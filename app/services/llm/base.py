"""
Base LLM service with provider abstraction
"""
import json
from typing import Dict, Any, Optional
from app.services.interfaces import LLMServiceInterface
from app.core.exceptions import LLMException, ConfigurationException
from app.core.config import settings

class BaseLLMService(LLMServiceInterface):
    """Base class for LLM services with common functionality"""
    
    def __init__(self, provider: str = None, model: str = None):
        self.provider = provider or settings.DEFAULT_LLM_PROVIDER
        self.model = model or settings.DEFAULT_MODEL
        self._validate_configuration()
    
    def _validate_configuration(self):
        """Validate provider configuration"""
        if self.provider == "openai" and not settings.OPENAI_API_KEY:
            raise ConfigurationException("OpenAI API key not configured")
        elif self.provider == "groq" and not settings.GROQ_API_KEY:
            raise ConfigurationException("Groq API key not configured")
        elif self.provider == "ollama" and not settings.OLLAMA_BASE_URL:
            raise ConfigurationException("Ollama base URL not configured")
    
    async def generate_structured_response(
        self, 
        prompt: str, 
        schema: Dict[str, Any],
        model: str = None
    ) -> Dict[str, Any]:
        """Generate structured JSON response with schema validation"""
        try:
            # Add JSON schema instruction to prompt
            structured_prompt = f"""
{prompt}

Please respond with valid JSON that matches this schema:
{json.dumps(schema, indent=2)}

Response:
"""
            
            response = await self.generate_completion(
                structured_prompt, 
                model=model,
                temperature=0.3  # Lower temperature for structured output
            )
            
            # Parse and validate JSON
            try:
                parsed_response = json.loads(response.strip())
                return parsed_response
            except json.JSONDecodeError as e:
                raise LLMException(f"Invalid JSON response from LLM: {e}")
                
        except Exception as e:
            raise LLMException(f"Structured response generation failed: {e}")
    
    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare headers for API requests"""
        headers = {"Content-Type": "application/json"}
        
        if self.provider == "openai":
            headers["Authorization"] = f"Bearer {settings.OPENAI_API_KEY}"
        elif self.provider == "groq":
            headers["Authorization"] = f"Bearer {settings.GROQ_API_KEY}"
            
        return headers