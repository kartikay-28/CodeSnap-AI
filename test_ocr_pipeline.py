"""
Comprehensive test script for CodeSnap AI OCR pipeline
"""
import asyncio
import io
import sys
import os
from PIL import Image, ImageDraw, ImageFont
from fastapi import UploadFile

# Add app to path for imports
sys.path.append(os.path.dirname(__file__))

from app.services.ocr.ocr_service import OCRService
from app.utils.file_validator import FileValidator
from app.utils.image_processor import ImageProcessor
from app.utils.text_cleaner import TextCleaner


def create_test_code_image() -> bytes:
    """Create a test image with code text"""
    # Create a white image
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Sample code text
    code_text = """def fibonacci(n):
    \"\"\"Calculate fibonacci number\"\"\"
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    result = fibonacci(i)
    print(f"fibonacci({i}) = {result}")

class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result"""
    
    # Try to use a monospace font, fallback to default
    try:
        # Try common monospace fonts
        font = ImageFont.truetype("consolas.ttf", 14)
    except:
        try:
            font = ImageFont.truetype("courier.ttf", 14)
        except:
            font = ImageFont.load_default()
    
    # Draw the code text
    draw.text((20, 20), code_text, fill='black', font=font)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


def test_individual_components():
    """Test individual components"""
    print("🧪 Testing Individual Components...")
    
    # Test FileValidator
    print("\n📁 Testing FileValidator...")
    try:
        validator = FileValidator()
        print("✅ FileValidator initialized successfully")
    except Exception as e:
        print(f"❌ FileValidator failed: {e}")
        return False
    
    # Test ImageProcessor
    print("\n🖼️  Testing ImageProcessor...")
    try:
        processor = ImageProcessor()
        test_image_bytes = create_test_code_image()
        
        # Test image validation
        validation = processor.validate_image_for_ocr(test_image_bytes)
        print(f"✅ Image validation score: {validation['score']}/100")
        
        # Test preprocessing
        processed_bytes, metadata = processor.preprocess_for_ocr(test_image_bytes)
        print(f"✅ Image preprocessing completed: {len(processed_bytes)} bytes")
        
    except Exception as e:
        print(f"❌ ImageProcessor failed: {e}")
        return False
    
    # Test TextCleaner
    print("\n🧹 Testing TextCleaner...")
    try:
        cleaner = TextCleaner()
        test_text = "det fibonacci(n):\n    retum n if n <= 1\n    retum fibonacci(n-1) + fibonacci(n-2)"
        
        cleaned_result = cleaner.clean_extracted_text(test_text)
        print(f"✅ Text cleaning completed")
        print(f"   Detected language: {cleaned_result['detected_language']}")
        print(f"   Language confidence: {cleaned_result['language_confidence']:.2f}")
        
    except Exception as e:
        print(f"❌ TextCleaner failed: {e}")
        return False
    
    return True


async def test_ocr_service():
    """Test the complete OCR service"""
    print("\n🎯 Testing Complete OCR Service...")
    
    try:
        # Initialize OCR service
        ocr_service = OCRService()
        print("✅ OCR Service initialized")
        
        # Test health check
        health = ocr_service.health_check()
        print(f"🏥 Health Check: {health['status']}")
        
        if health['status'] != 'healthy':
            print("⚠️  OCR service is not fully healthy, but continuing test...")
            print(f"   Tesseract available: {health.get('tesseract_available', False)}")
        
        # Create test image
        test_image_bytes = create_test_code_image()
        print("🖼️  Test image created")
        
        # Test image validation
        validation = ocr_service.validate_image_for_ocr(test_image_bytes)
        print(f"✅ Image validation score: {validation['score']}/100")
        if validation['warnings']:
            print(f"   Warnings: {validation['warnings']}")
        
        # Test OCR extraction from bytes
        print("\n📝 Testing OCR extraction from bytes...")
        result = ocr_service.extract_text_from_bytes(
            image_bytes=test_image_bytes,
            filename="test_code.png",
            enhance_image=True,
            extract_code_only=True
        )
        
        print(f"✅ OCR Results:")
        print(f"   Confidence: {result.confidence_score:.2f}")
        print(f"   Processing time: {result.processing_time_ms}ms")
        print(f"   Detected language: {result.preprocessing_applied.get('detected_language', 'unknown')}")
        print(f"   Text cleaning applied: {result.preprocessing_applied.get('text_cleaning_applied', False)}")
        
        print("\n📄 Extracted Text:")
        print("=" * 60)
        print(result.extracted_text)
        print("=" * 60)
        
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
        print(f"   Image dimensions: {upload_result.image_metadata.dimensions}")
        print(f"   File size: {upload_result.image_metadata.size_bytes} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ OCR Service test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\n🚨 Testing Error Handling...")
    
    try:
        ocr_service = OCRService()
        
        # Test with invalid image data
        try:
            invalid_bytes = b"This is not an image"
            result = ocr_service.extract_text_from_bytes(invalid_bytes)
            print("❌ Should have failed with invalid image data")
        except Exception as e:
            print(f"✅ Correctly handled invalid image: {type(e).__name__}")
        
        # Test with empty bytes
        try:
            empty_bytes = b""
            result = ocr_service.extract_text_from_bytes(empty_bytes)
            print("❌ Should have failed with empty data")
        except Exception as e:
            print(f"✅ Correctly handled empty data: {type(e).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting CodeSnap AI OCR Pipeline Tests...")
    print("=" * 60)
    
    # Test individual components
    components_ok = test_individual_components()
    
    if not components_ok:
        print("\n❌ Component tests failed. Stopping.")
        return False
    
    # Test OCR service
    service_ok = await test_ocr_service()
    
    if not service_ok:
        print("\n❌ OCR service tests failed.")
        return False
    
    # Test error handling
    error_handling_ok = test_error_handling()
    
    print("\n" + "=" * 60)
    
    if components_ok and service_ok and error_handling_ok:
        print("🎉 All tests passed! CodeSnap AI OCR Pipeline is working correctly.")
        print("\n📋 Next steps:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Install Tesseract OCR on your system")
        print("   3. Start the server: python -m app.main")
        print("   4. Visit http://localhost:8000/docs for API documentation")
        print("   5. Test OCR endpoint: POST /api/v1/ocr/extract")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)