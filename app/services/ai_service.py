"""
AI Service for LLM communication - provider agnostic
"""
import json
import asyncio
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

from app.core.config import settings
from app.core.exceptions import LLMException

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate_response(self, prompt: str, timeout: int = 30) -> str:
        """Generate response from LLM"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self):
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        except ImportError:
            raise LLMException("OpenAI library not installed")
        except Exception as e:
            raise LLMException(f"OpenAI initialization failed: {str(e)}")
    
    async def generate_response(self, prompt: str, timeout: int = 30) -> str:
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=settings.DEFAULT_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,  # Low temperature for consistency
                    max_tokens=2000
                ),
                timeout=timeout
            )
            return response.choices[0].message.content
        except asyncio.TimeoutError:
            raise LLMException(f"OpenAI request timed out after {timeout}s")
        except Exception as e:
            raise LLMException(f"OpenAI API error: {str(e)}")


class GroqProvider(LLMProvider):
    """Groq provider"""
    
    def __init__(self):
        try:
            import groq
            self.client = groq.AsyncGroq(api_key=settings.GROQ_API_KEY)
        except ImportError:
            raise LLMException("Groq library not installed")
        except Exception as e:
            raise LLMException(f"Groq initialization failed: {str(e)}")
    
    async def generate_response(self, prompt: str, timeout: int = 30) -> str:
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=2000
                ),
                timeout=timeout
            )
            return response.choices[0].message.content
        except asyncio.TimeoutError:
            raise LLMException(f"Groq request timed out after {timeout}s")
        except Exception as e:
            raise LLMException(f"Groq API error: {str(e)}")


class AIService:
    """Main AI service for code explanation"""
    
    def __init__(self):
        self.provider = self._get_provider()
        self.timeout = 30
    
    def _get_provider(self) -> LLMProvider:
        """Get configured LLM provider"""
        provider_name = settings.DEFAULT_LLM_PROVIDER.lower()
        
        if provider_name == "openai":
            return OpenAIProvider()
        elif provider_name == "groq":
            return GroqProvider()
        else:
            raise LLMException(f"Unsupported LLM provider: {provider_name}")
    
    async def generate_explanation(self, prompt: str) -> Dict[str, Any]:
        """
        Generate code explanation using LLM
        
        Args:
            prompt: Formatted prompt template
            
        Returns:
            Parsed JSON response from LLM
        """
        try:
            logger.info("Generating AI explanation")
            
            # Get response from LLM
            raw_response = await self.provider.generate_response(prompt, self.timeout)
            
            # Parse JSON response
            try:
                # Extract JSON from response (handle markdown code blocks)
                json_str = raw_response.strip()
                if json_str.startswith("```json"):
                    json_str = json_str[7:-3].strip()
                elif json_str.startswith("```"):
                    json_str = json_str[3:-3].strip()
                
                parsed_response = json.loads(json_str)
                
                # Validate required fields
                required_fields = ["overview", "step_by_step", "complexity", "dry_run"]
                for field in required_fields:
                    if field not in parsed_response:
                        raise ValueError(f"Missing required field: {field}")
                
                logger.info("AI explanation generated successfully")
                return parsed_response
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse LLM response: {str(e)}")
                # Return fallback response
                return {
                    "overview": "Code analysis completed but response format was invalid",
                    "step_by_step": ["Unable to parse detailed steps"],
                    "complexity": {"time": "Unknown", "space": "Unknown"},
                    "dry_run": {"input_example": "N/A", "steps": [], "output": "N/A"},
                    "warnings": ["Response parsing failed - please try again"]
                }
                
        except LLMException:
            raise  # Re-raise LLM exceptions
        except Exception as e:
            logger.error(f"Unexpected error in AI service: {str(e)}")
            raise LLMException(f"AI service error: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check AI service health"""
        try:
            provider_name = settings.DEFAULT_LLM_PROVIDER
            has_api_key = bool(
                settings.OPENAI_API_KEY if provider_name == "openai" 
                else settings.GROQ_API_KEY if provider_name == "groq"
                else False
            )
            
            return {
                "status": "healthy" if has_api_key else "degraded",
                "provider": provider_name,
                "api_key_configured": has_api_key,
                "timeout": self.timeout
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }