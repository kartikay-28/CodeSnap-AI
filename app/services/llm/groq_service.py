"""
Groq LLM Service Implementation
"""
import httpx
from typing import Optional
from app.services.llm.base import BaseLLMService
from app.core.exceptions import LLMException

class GroqService(BaseLLMService):
    """Groq API implementation"""
    
    def __init__(self, model: str = "mixtral-8x7b-32768"):
        super().__init__(provider="groq", model=model)
        self.base_url = "https://api.groq.com/openai/v1"
    
    async def generate_completion(
        self, 
        prompt: str, 
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Generate completion using Groq API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._prepare_headers(),
                    json={
                        "model": model or self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise LLMException(f"Groq API error: {response.status_code} - {response.text}")
                
                data = response.json()
                return data["choices"][0]["message"]["content"]
                
        except httpx.TimeoutException:
            raise LLMException("Groq API request timeout")
        except Exception as e:
            raise LLMException(f"Groq completion failed: {e}")