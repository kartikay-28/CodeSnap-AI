"""
Ollama LLM Service Implementation
"""
import httpx
from typing import Optional
from app.services.llm.base import BaseLLMService
from app.core.exceptions import LLMException
from app.core.config import settings

class OllamaService(BaseLLMService):
    """Ollama local API implementation"""
    
    def __init__(self, model: str = "codellama"):
        super().__init__(provider="ollama", model=model)
        self.base_url = settings.OLLAMA_BASE_URL
    
    async def generate_completion(
        self, 
        prompt: str, 
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Generate completion using Ollama API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model or self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens
                        }
                    },
                    timeout=60.0  # Ollama can be slower
                )
                
                if response.status_code != 200:
                    raise LLMException(f"Ollama API error: {response.status_code} - {response.text}")
                
                data = response.json()
                return data["response"]
                
        except httpx.TimeoutException:
            raise LLMException("Ollama API request timeout")
        except Exception as e:
            raise LLMException(f"Ollama completion failed: {e}")