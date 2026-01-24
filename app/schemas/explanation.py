"""
Pydantic schemas for code explanation API
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


class ExplanationLevel(str, Enum):
    """Explanation complexity levels"""
    BEGINNER = "beginner"
    DETAILED = "detailed"


class CodeExplanationRequest(BaseModel):
    """Request model for code explanation"""
    code: str = Field(..., min_length=1, max_length=10000, description="Source code to explain")
    explanation_level: ExplanationLevel = Field(default=ExplanationLevel.DETAILED, description="Level of explanation detail")
    
    @validator('code')
    def validate_code(cls, v):
        """Validate code input"""
        if not v or not v.strip():
            raise ValueError("Code cannot be empty")
        
        # Check for obvious OCR garbage
        if len(v.strip()) < 5:
            raise ValueError("Code too short - minimum 5 characters required")
        
        # Check for excessive special characters (OCR artifacts)
        special_chars = sum(1 for c in v if not c.isalnum() and c not in ' \n\t(){}[].,;:"\'=-+*/<>!@#$%^&|\\')
        if special_chars > len(v) * 0.3:  # More than 30% special chars
            raise ValueError("Code contains too many invalid characters")
        
        return v.strip()


class ComplexityAnalysis(BaseModel):
    """Time and space complexity analysis"""
    time: str = Field(description="Time complexity with explanation")
    space: str = Field(description="Space complexity with explanation")


class DryRunExample(BaseModel):
    """Dry run execution example"""
    input_example: str = Field(description="Example input for the code")
    steps: List[str] = Field(description="Step-by-step execution trace")
    output: str = Field(description="Expected output")


class CodeExplanationResult(BaseModel):
    """Complete code explanation result"""
    overview: str = Field(description="Brief summary of what the code does")
    step_by_step: List[str] = Field(description="Detailed step-by-step explanation")
    complexity: ComplexityAnalysis = Field(description="Time and space complexity analysis")
    dry_run: DryRunExample = Field(description="Example execution walkthrough")
    warnings: List[str] = Field(default=[], description="Potential issues or warnings")
    processing_time_ms: Optional[int] = Field(description="Processing time in milliseconds")


class CodeExplanationResponse(BaseModel):
    """API response for code explanation"""
    success: bool
    result: Optional[CodeExplanationResult] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AIHealthCheck(BaseModel):
    """AI service health check response"""
    status: str  # "healthy", "degraded", "unhealthy"
    provider: str
    api_key_configured: bool
    timeout: int