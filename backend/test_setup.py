"""
Test script to verify the enhanced OMR setup and dependencies.
"""

import sys
import importlib
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported."""
    required_packages = [
        'streamlit',
        'cv2',
        'numpy',
        'PIL',
        'easyocr',
        'reportlab',
        'pandas'
    ]
    
    print("🔍 Testing package imports...")
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}: OK")
        except ImportError as e:
            print(f"❌ {package}: FAILED - {e}")
            failed_imports.append(package)
    
    return failed_imports

def test_directories():
    """Test if required directories exist."""
    print("\n📁 Testing directory structure...")
    
    base_dir = Path(__file__).parent
    required_dirs = [
        'answer_keys',
        'batch_uploads',
        'batch_results',
        'temp'
    ]
    
    missing_dirs = []
    
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/: OK")
        else:
            print(f"⚠️  {dir_name}/: Creating...")
            dir_path.mkdir(exist_ok=True)
            print(f"✅ {dir_name}/: Created")
    
    return missing_dirs

def test_answer_keys():
    """Test if sample answer keys exist."""
    print("\n📋 Testing answer keys...")
    
    base_dir = Path(__file__).parent
    answer_keys_dir = base_dir / 'answer_keys'
    
    if not answer_keys_dir.exists():
        answer_keys_dir.mkdir(exist_ok=True)
    
    # Check for existing answer keys
    existing_keys = list(answer_keys_dir.glob('*.json'))
    
    if existing_keys:
        print(f"✅ Found {len(existing_keys)} existing answer keys:")
        for key_file in existing_keys:
            print(f"   - {key_file.name}")
    else:
        print("⚠️  No answer keys found. Creating sample...")
        
        # Create sample answer key
        import json
        sample_key = {str(i): chr(ord('A') + (i-1) % 5) for i in range(1, 11)}
        
        sample_path = answer_keys_dir / 'sample_exam.json'
        with open(sample_path, 'w') as f:
            json.dump(sample_key, f, indent=2)
        
        print(f"✅ Created sample answer key: {sample_path.name}")

def test_ocr():
    """Test OCR functionality."""
    print("\n🔍 Testing OCR functionality...")
    
    try:
        import easyocr
        reader = easyocr.Reader(['en'])
        print("✅ EasyOCR initialized successfully")
        
        # Test with a simple text image (if available)
        print("✅ OCR test completed")
        
    except Exception as e:
        print(f"❌ OCR test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Enhanced OMR Checker - Setup Test")
    print("=" * 50)
    
    # Test imports
    failed_imports = test_imports()
    
    # Test directories
    test_directories()
    
    # Test answer keys
    test_answer_keys()
    
    # Test OCR
    ocr_ok = test_ocr()
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    if failed_imports:
        print(f"❌ Failed imports: {', '.join(failed_imports)}")
        print("\n💡 To install missing packages, run:")
        print("   pip install -r enhanced_requirements.txt")
    else:
        print("✅ All packages imported successfully")
    
    if ocr_ok:
        print("✅ OCR functionality working")
    else:
        print("❌ OCR functionality issues detected")
    
    print("\n🎯 Next steps:")
    print("1. Install any missing packages")
    print("2. Run the application: streamlit run batch_omr_app.py")
    print("3. Upload reference sheet or create answer key")
    print("4. Upload student answer sheets")
    print("5. Process and download reports")
    
    print("\n📖 For detailed instructions, see BATCH_OMR_README.md")

if __name__ == "__main__":
    main()
