"""
Pydantic schemas for code analysis responses
"""
from pydantic import BaseModel
from typing import List, Optional

class ComplexityAnalysis(BaseModel):
    time_complexity: str
    space_complexity: str
    explanation: str

class DryRunStep(BaseModel):
    step: int
    description: str
    variables: dict
    output: Optional[str] = None

class DryRunExample(BaseModel):
    input_example: str
    steps: List[DryRunStep]
    final_output: str

class CodeAnalysisResponse(BaseModel):
    # Extracted and cleaned code
    extracted_code: str
    detected_language: str
    confidence_score: float
    
    # Analysis results
    step_by_step_explanation: List[str]
    complexity_analysis: ComplexityAnalysis
    dry_run_example: DryRunExample
    beginner_explanation: str
    edge_cases: List[str]
    common_mistakes: List[str]
    
    # Metadata
    processing_time_ms: int
    ocr_confidence: float