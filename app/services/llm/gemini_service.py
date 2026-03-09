"""
Google Gemini LLM Service Implementation
"""
import asyncio
from typing import Optional
from google import genai
from app.services.llm.base import BaseLLMService
from app.core.exceptions import LLMException
from app.core.config import settings


class GeminiService(BaseLLMService):
    """Google Gemini API implementation"""
    
    def __init__(self, model: str = "gemini-2.0-flash-exp"):
        super().__init__(provider="gemini", model=model)
        try:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        except Exception as e:
            raise LLMException(f"Gemini initialization failed: {str(e)}")
    
    async def generate_completion(
        self, 
        prompt: str, 
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Generate completion using Gemini API"""
        try:
            # Run in thread pool since Gemini SDK is synchronous
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=model or self.model,
                    contents=prompt,
                    config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens
                    }
                )
            )
            
            return response.text
            
        except asyncio.TimeoutError:
            raise LLMException("Gemini API request timed out")
        except Exception as e:
            raise LLMException(f"Gemini API error: {str(e)}")