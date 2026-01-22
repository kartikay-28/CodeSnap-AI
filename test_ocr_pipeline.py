"""
Simple test script to verify OCR pipeline functionality
"""
import asyncio
import io
from PIL import Image, ImageDraw, ImageFont
from fastapi import UploadFile

from app.services.ocr.ocr_service import OCRService


def create_test_code_image() -> bytes:
    """Create a test image with code text"""
    # Create a white image
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Sample code text
    code_text = """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
result = fibonacci(10)
print(f"Fibonacci(10) = {result}")"""
    
    # Try to use a monospace font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Draw the code text
    draw.text((20, 20), code_text, fill='black', font=font)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


async def test_ocr_pipeline():
    """Test the complete OCR pipeline"""
    print("🧪 Testing OCR Pipeline...")
    
    try:
        # Initialize OCR service
        ocr_service = OCRService()
        print("✅ OCR Service initialized")
        
        # Test health check
        health = ocr_service.health_check()
        print(f"🏥 Health Check: {health['status']}")
        
        if health['status'] != 'healthy':
            print("❌ OCR service is not healthy. Check Tesseract installation.")
            return
        
        # Create test image
        test_image_bytes = create_test_code_image()
        print("🖼️  Test image created")
        
        # Test image validation
        validation = ocr_service.validate_image_for_ocr(test_image_bytes)
        print(f"✅ Image validation score: {validation['score']}/100")
        
        # Test OCR extraction
        result = ocr_service.extract_text_from_bytes(
            image_bytes=test_image_bytes,
            filename="test_code.png",
            enhance_image=True,
            extract_code_only=True
        )
        
        print("\n📝 OCR Results:")
        print(f"   Confidence: {result.confidence_score:.2f}")
        print(f"   Processing time: {result.processing_time_ms}ms")
        print(f"   Detected language: {result.preprocessing_applied.get('detected_language', 'unknown')}")
        print("\n📄 Extracted Text:")
        print("=" * 50)
        print(result.extracted_text)
        print("=" * 50)
        
        # Test with file upload simulation
        print("\n🔄 Testing file upload simulation...")
        
        # Create UploadFile-like object
        file_obj = io.BytesIO(test_image_bytes)
        upload_file = UploadFile(
            filename="test_code.png",
            file=file_obj,
            content_type="image/png"
        )
        
        upload_result = await ocr_service.extract_text_from_upload(
            file=upload_file,
            enhance_image=True,
            extract_code_only=True,
            language_hint="python"
        )
        
        print(f"✅ Upload processing completed in {upload_result.processing_time_ms}ms")
        print(f"   Text length: {len(upload_result.extracted_text)} characters")
        
        print("\n🎉 OCR Pipeline test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_ocr_pipeline())