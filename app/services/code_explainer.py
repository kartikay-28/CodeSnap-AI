"""
Code explanation orchestrator - business logic layer
"""
import time
import logging
from typing import Optional

from app.services.ai_service import AIService
from app.schemas.explanation import CodeExplanationResult, ExplanationLevel
from app.core.prompts import DETAILED_EXPLANATION_PROMPT, BEGINNER_EXPLANATION_PROMPT
from app.core.exceptions import LLMException

logger = logging.getLogger(__name__)


class CodeExplainer:
    """Orchestrates code explanation process"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    async def explain_code(self, code: str, level: ExplanationLevel) -> CodeExplanationResult:
        """
        Generate comprehensive code explanation
        
        Args:
            code: Source code to explain
            level: Explanation detail level
            
        Returns:
            Complete explanation result
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting code explanation - level: {level}")
            
            # Select appropriate prompt template
            if level == ExplanationLevel.BEGINNER:
                prompt_template = BEGINNER_EXPLANATION_PROMPT
            else:
                prompt_template = DETAILED_EXPLANATION_PROMPT
            
            # Format prompt with code
            formatted_prompt = prompt_template.format(code=code)
            
            # Generate explanation using AI service
            ai_response = await self.ai_service.generate_explanation(formatted_prompt)
            
            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)
            
            # Create result object
            result = CodeExplanationResult(
                overview=ai_response.get("overview", "Code explanation generated"),
                step_by_step=ai_response.get("step_by_step", []),
                complexity={
                    "time": ai_response.get("complexity", {}).get("time", "Unknown"),
                    "space": ai_response.get("complexity", {}).get("space", "Unknown")
                },
                dry_run={
                    "input_example": ai_response.get("dry_run", {}).get("input_example", "N/A"),
                    "steps": ai_response.get("dry_run", {}).get("steps", []),
                    "output": ai_response.get("dry_run", {}).get("output", "N/A")
                },
                warnings=ai_response.get("warnings", []),
                processing_time_ms=processing_time
            )
            
            logger.info(f"Code explanation completed in {processing_time}ms")
            return result
            
        except LLMException:
            raise  # Re-raise LLM exceptions
        except Exception as e:
            logger.error(f"Code explanation failed: {str(e)}")
            raise LLMException(f"Explanation generation failed: {str(e)}")
    
    def health_check(self):
        """Check explainer service health"""
        try:
            ai_health = self.ai_service.health_check()
            return {
                "status": ai_health.get("status", "unknown"),
                "ai_service": ai_health,
                "prompts_loaded": True
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "ai_service": None,
                "prompts_loaded": False
            }