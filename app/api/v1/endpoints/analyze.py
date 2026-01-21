"""
Code Analysis Endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.analysis import CodeAnalysisResponse
from app.services.code_analyzer import CodeAnalyzerService

router = APIRouter()

@router.post("/code", response_model=CodeAnalysisResponse)
async def analyze_code_from_image(
    file: UploadFile = File(..., description="Screenshot of source code")
) -> CodeAnalysisResponse:
    """
    Analyze code from a screenshot image.
    
    - **file**: Image file containing source code screenshot
    - Returns: Detailed code analysis with explanations
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    try:
        # Initialize analyzer service
        analyzer = CodeAnalyzerService()
        
        # Process the image and analyze code
        result = await analyzer.analyze_from_image(file)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )