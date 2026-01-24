"""
Code explanation API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
import logging

from app.schemas.explanation import (
    CodeExplanationRequest, 
    CodeExplanationResponse, 
    AIHealthCheck
)
from app.services.code_explainer import CodeExplainer
from app.core.exceptions import LLMException

logger = logging.getLogger(__name__)
router = APIRouter()

# Dependency to get code explainer instance
def get_code_explainer() -> CodeExplainer:
    return CodeExplainer()


@router.post("/", response_model=CodeExplanationResponse, summary="Explain code with AI")
async def explain_code(
    request: CodeExplanationRequest,
    explainer: CodeExplainer = Depends(get_code_explainer)
):
    """
    Generate AI-powered explanation of source code.
    
    **Features:**
    - Detailed step-by-step breakdown
    - Time & space complexity analysis  
    - Dry run with example execution
    - Beginner-friendly or detailed explanations
    - Potential issue warnings
    
    **Input validation:**
    - Code length: 5-10,000 characters
    - Filters OCR artifacts and garbage input
    - Handles empty or malformed code
    """
    try:
        logger.info(f"Code explanation request - level: {request.explanation_level}")
        
        # Generate explanation
        result = await explainer.explain_code(
            code=request.code,
            level=request.explanation_level
        )
        
        logger.info("Code explanation successful")
        
        return CodeExplanationResponse(
            success=True,
            result=result
        )
        
    except LLMException as e:
        logger.error(f"LLM service error: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail=f"AI service unavailable: {str(e)}"
        )
        
    except ValueError as e:
        logger.warning(f"Invalid input: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid code input: {str(e)}"
        )
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during code explanation"
        )


@router.get("/health", response_model=AIHealthCheck, summary="AI service health check")
async def ai_health_check(explainer: CodeExplainer = Depends(get_code_explainer)):
    """
    Check the health status of AI explanation service.
    
    **Checks:**
    - LLM provider availability
    - API key configuration
    - Service connectivity
    - Response timeouts
    """
    try:
        health_status = explainer.health_check()
        
        return AIHealthCheck(
            status=health_status.get("status", "unknown"),
            provider=health_status.get("ai_service", {}).get("provider", "unknown"),
            api_key_configured=health_status.get("ai_service", {}).get("api_key_configured", False),
            timeout=health_status.get("ai_service", {}).get("timeout", 30)
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return AIHealthCheck(
            status="unhealthy",
            provider="unknown", 
            api_key_configured=False,
            timeout=30
        )