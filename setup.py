"""
CodeSnap AI - Setup and Verification Script
Run this to verify your installation and configuration
"""
import sys
import subprocess
import os
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9 or higher is required")
        return False
    print("✅ Python version is compatible")
    return True


def check_easyocr():
    """Check if EasyOCR is installed"""
    print_header("Checking EasyOCR")
    try:
        import easyocr
        print("✅ EasyOCR installed successfully")
        print("   No external dependencies needed!")
        print("   Note: First run will download language models (~100MB)")
        return True
    except ImportError:
        print("❌ EasyOCR not installed")
        print("\nInstall with:")
        print("  pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error checking EasyOCR: {e}")
        return False


def check_dependencies():
    """Check if required Python packages are installed"""
    print_header("Checking Python Dependencies")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "easyocr",
        "opencv-python",
        "Pillow",
        "openai",
        "groq",
        "pydantic",
        "pydantic-settings",
        "python-multipart",
        "python-dotenv",
        "httpx"
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing {len(missing)} package(s)")
        print("\nInstall with:")
        print("  pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies installed")
    return True


def check_env_file():
    """Check if .env file exists and is configured"""
    print_header("Checking Environment Configuration")
    
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env file not found")
        print("\nCreate it with:")
        print("  cp .env.example .env")
        return False
    
    print("✅ .env file exists")
    
    # Check for API keys
    with open(env_path, 'r') as f:
        content = f.read()
    
    has_openai = "OPENAI_API_KEY=" in content and len(content.split("OPENAI_API_KEY=")[1].split('\n')[0].strip()) > 0
    has_groq = "GROQ_API_KEY=" in content and len(content.split("GROQ_API_KEY=")[1].split('\n')[0].strip()) > 0
    
    if not (has_openai or has_groq):
        print("⚠️  No API keys configured")
        print("\nAdd your API key to .env:")
        print("  OPENAI_API_KEY=your_key_here")
        print("  OR")
        print("  GROQ_API_KEY=your_key_here")
        return False
    
    if has_openai:
        print("✅ OpenAI API key configured")
    if has_groq:
        print("✅ Groq API key configured")
    
    return True


def check_project_structure():
    """Verify project structure"""
    print_header("Checking Project Structure")
    
    required_dirs = [
        "app",
        "app/api",
        "app/core",
        "app/services",
        "app/schemas",
        "app/utils",
        "frontend",
        "tests"
    ]
    
    required_files = [
        "app/main.py",
        "requirements.txt",
        "frontend/index.html",
        "frontend/app.js",
        "frontend/style.css"
    ]
    
    all_good = True
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - MISSING")
            all_good = False
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_good = False
    
    return all_good


def main():
    """Run all checks"""
    print("\n🚀 CodeSnap AI - Setup Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("EasyOCR", check_easyocr),
        ("Python Dependencies", check_dependencies),
        ("Environment Configuration", check_env_file),
        ("Project Structure", check_project_structure)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error during {name} check: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Setup Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All checks passed! You're ready to run CodeSnap AI")
        print("\nNext steps:")
        print("  1. Add your API key to .env file")
        print("  2. Start the server: python -m app.main")
        print("  3. Open frontend/index.html in your browser")
        print("  4. Upload a code screenshot and analyze!")
        print("\nAPI Documentation: http://localhost:8000/docs")
        print("\nNote: First run will download EasyOCR models (~100MB)")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nQuick fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Configure .env: Add your API key")
        return 1


if __name__ == "__main__":
    sys.exit(main())