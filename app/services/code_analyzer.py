"""
Main Code Analyzer Service - Orchestrates the analysis pipeline
"""
import time
import logging
from fastapi import UploadFile
from typing import Dict, Any

from app.schemas.analysis import CodeAnalysisResponse, ComplexityAnalysis, DryRunExample, DryRunStep
from app.services.ocr.ocr_service import OCRService
from app.services.ai_service import AIService
from app.core.exceptions import OCRException, LLMException, CodeSnapException

logger = logging.getLogger(__name__)


class CodeAnalyzerService:
    """
    Main service that orchestrates the code analysis pipeline:
    Image -> OCR -> Cleaning -> AI Analysis -> Response
    """
    
    def __init__(self):
        self.ocr_service = OCRService()
        self.ai_service = AIService()
    
    async def analyze_from_image(self, file: UploadFile) -> CodeAnalysisResponse:
        """
        Main analysis pipeline
        
        Args:
            file: Uploaded image file containing code
            
        Returns:
            Complete code analysis with explanations
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting code analysis for file: {file.filename}")
            
            # Step 1: Extract code from image using OCR
            logger.info("Step 1: Extracting code from image...")
            ocr_result = await self.ocr_service.extract_text_from_upload(
                file=file,
                enhance_image=True,
                extract_code_only=True
            )
            
            extracted_code = ocr_result.extracted_text
            ocr_confidence = ocr_result.confidence_score
            detected_language = ocr_result.preprocessing_applied.get('detected_language', 'unknown')
            
            logger.info(f"OCR completed. Language: {detected_language}, Confidence: {ocr_confidence:.2f}")
            
            # Check if we got meaningful code
            if not extracted_code or len(extracted_code.strip()) < 10:
                raise CodeSnapException("No code detected in image. Please ensure the image contains clear, readable code.")
            
            # Step 2: Generate AI explanation
            logger.info("Step 2: Generating AI explanation...")
            prompt = self._create_analysis_prompt(extracted_code, detected_language)
            ai_response = await self.ai_service.generate_explanation(prompt)
            
            logger.info("AI explanation generated successfully")
            
            # Step 3: Format response
            logger.info("Step 3: Formatting response...")
            response = self._format_response(
                extracted_code=extracted_code,
                detected_language=detected_language,
                ocr_confidence=ocr_confidence,
                ai_response=ai_response,
                start_time=start_time
            )
            
            logger.info(f"Code analysis completed in {response.processing_time_ms}ms")
            return response
            
        except (OCRException, LLMException) as e:
            # Re-raise known exceptions
            logger.error(f"Analysis failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during analysis: {str(e)}")
            raise CodeSnapException(f"Code analysis failed: {str(e)}")
    
    def _create_analysis_prompt(self, code: str, language: str) -> str:
        """
        Create comprehensive analysis prompt for LLM
        
        Args:
            code: Extracted code
            language: Detected programming language
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert code analyst. Analyze the following {language} code and provide a comprehensive explanation.

CODE:
```{language}
{code}
```

Provide your analysis in the following JSON format:

{{
  "overview": "Brief 2-3 sentence overview of what this code does",
  "step_by_step": [
    "Step 1: Detailed explanation",
    "Step 2: Detailed explanation",
    "..."
  ],
  "complexity": {{
    "time": "Time complexity (e.g., O(n), O(log n))",
    "space": "Space complexity (e.g., O(1), O(n))",
    "explanation": "Brief explanation of the complexity analysis"
  }},
  "dry_run": {{
    "input_example": "Example input for demonstration",
    "steps": [
      {{
        "step": 1,
        "description": "What happens in this step",
        "variables": {{"var_name": "value"}},
        "output": "Output at this step (if any)"
      }}
    ],
    "output": "Final output of the example"
  }},
  "beginner_explanation": "Explain this code as if teaching a beginner programmer",
  "edge_cases": [
    "Edge case 1",
    "Edge case 2"
  ],
  "common_mistakes": [
    "Common mistake 1",
    "Common mistake 2"
  ],
  "improvements": [
    "Potential improvement 1",
    "Potential improvement 2"
  ]
}}

Respond ONLY with valid JSON. No additional text."""
        
        return prompt
    
    def _format_response(
        self,
        extracted_code: str,
        detected_language: str,
        ocr_confidence: float,
        ai_response: Dict[str, Any],
        start_time: float
    ) -> CodeAnalysisResponse:
        """
        Format the final response
        
        Args:
            extracted_code: Code extracted from image
            detected_language: Programming language
            ocr_confidence: OCR confidence score
            ai_response: Parsed AI response
            start_time: Processing start time
            
        Returns:
            Formatted CodeAnalysisResponse
        """
        processing_time = int((time.time() - start_time) * 1000)
        
        # Parse complexity analysis
        complexity_data = ai_response.get('complexity', {})
        complexity_analysis = ComplexityAnalysis(
            time_complexity=complexity_data.get('time', 'Unknown'),
            space_complexity=complexity_data.get('space', 'Unknown'),
            explanation=complexity_data.get('explanation', 'No complexity analysis available')
        )
        
        # Parse dry run example
        dry_run_data = ai_response.get('dry_run', {})
        dry_run_steps = []
        
        for step_data in dry_run_data.get('steps', []):
            dry_run_steps.append(DryRunStep(
                step=step_data.get('step', 0),
                description=step_data.get('description', ''),
                variables=step_data.get('variables', {}),
                output=step_data.get('output')
            ))
        
        dry_run_example = DryRunExample(
            input_example=dry_run_data.get('input_example', 'No example provided'),
            steps=dry_run_steps if dry_run_steps else [
                DryRunStep(step=1, description="No dry run available", variables={}, output=None)
            ],
            final_output=dry_run_data.get('output', 'No output provided')
        )
        
        # Calculate confidence score (average of OCR and language detection)
        language_confidence = 0.8  # Default if not available
        overall_confidence = (ocr_confidence + language_confidence) / 2
        
        return CodeAnalysisResponse(
            extracted_code=extracted_code,
            detected_language=detected_language,
            confidence_score=overall_confidence,
            step_by_step_explanation=ai_response.get('step_by_step', ['No explanation available']),
            complexity_analysis=complexity_analysis,
            dry_run_example=dry_run_example,
            beginner_explanation=ai_response.get('beginner_explanation', 'No beginner explanation available'),
            edge_cases=ai_response.get('edge_cases', ['No edge cases identified']),
            common_mistakes=ai_response.get('common_mistakes', ['No common mistakes identified']),
            processing_time_ms=processing_time,
            ocr_confidence=ocr_confidence
        )