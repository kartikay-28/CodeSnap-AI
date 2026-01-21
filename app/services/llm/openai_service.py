"""
OpenAI LLM Service Implementation
"""
import httpx
from typing import Optional
from app.services.llm.base import BaseLLMService
from app.core.exceptions import LLMException

class OpenAIService(BaseLLMService):
    """OpenAI API implementation"""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        super().__init__(provider="openai", model=model)
        self.base_url = "https://api.openai.com/v1"
    
    async def generate_completion(
        self, 
        prompt: str, 
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Generate completion using OpenAI API"""
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
                    raise LLMException(f"OpenAI API error: {response.status_code} - {response.text}")
                
                data = response.json()
                return data["choices"][0]["message"]["content"]
                
        except httpx.TimeoutException:
            raise LLMException("OpenAI API request timeout")
        except Exception as e:
            raise LLMException(f"OpenAI completion failed: {e}")