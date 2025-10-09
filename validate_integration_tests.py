"""
Test Integration Setup Validation - Run this to verify integration tests are configured correctly
"""

import importlib.util
import sys
from pathlib import Path

def check_test_structure():
    """Verify integration tests are structured correctly"""
    backend_dir = Path("backend")
    tests_dir = backend_dir / "tests"

    if not tests_dir.exists():
        print("❌ tests directory not found")
        return False

    # Check for integration test files
    integration_files = [
        "test_conversation_integration.py",
        "test_api_integration.py",
        "conftest.py"
    ]

    missing_files = []
    for file in integration_files:
        if not (tests_dir / file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"❌ Missing integration test files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All integration test files present")

    # Check pytest configuration
    pytest_ini = backend_dir / "pytest.ini"
    if not pytest_ini.exists():
        print("❌ pytest.ini configuration file missing")
        return False
    else:
        print("✅ pytest.ini configuration file found")

    # Check for test imports in integration files
    required_imports = [
        ("pytest", "pytest library must be available"),
        ("httpx", "httpx for HTTP client testing"),
        ("fastapi.testclient", "FastAPI test client"),
    ]

    missing_imports = []
    for import_name, description in required_imports:
        try:
            if '.' in import_name:
                # Handle submodule imports
                module_name = import_name.split('.')[0]
                importlib.import_module(module_name)
            else:
                importlib.import_module(import_name)
            print(f"✅ {import_name} import successful")
        except ImportError:
            missing_imports.append((import_name, description))

    if missing_imports:
        print("❌ Missing required packages:")
        for import_name, description in missing_imports:
            print(f"   - {import_name}: {description}")
        return False

    # Check test class structure
    try:
        with open(tests_dir / "test_conversation_integration.py", "r") as f:
            content = f.read()

        if "class TestConversationIntegration:" in content:
            print("✅ Test class structure detected")
        else:
            print("❌ Test class structure not found")
            return False

        if "@pytest.mark.asyncio" in content:
            print("✅ Async test markers found")
        else:
            print("❌ Async test markers missing")
            return False

    except Exception as e:
        print(f"❌ Error reading test file: {e}")
        return False

    print("\n🎉 Integration test setup validation completed successfully!")
    print("\nNext steps:")
    print("1. Ensure pytest is installed: cd backend && pip install pytest pytest-asyncio httpx")
    print("2. Run tests: make backend-test-integration")
    print("3. Check coverage: cd backend && python -m pytest --cov=app --cov-report=html")

    return True

if __name__ == "__main__":
    print("🔍 Validating Chimera Integration Test Setup")
    print("=" * 50)

    success = check_test_structure()

    if not success:
        print("\n❌ Integration test setup validation failed!")
        sys.exit(1)
    else:
        print("\n✅ Ready to run integration tests!")
        sys.exit(0)