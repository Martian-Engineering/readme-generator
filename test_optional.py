#!/usr/bin/env python3
"""
Simple test to verify Optional type annotations work correctly
"""

from generate_readmes import READMEGenerator, AppendOnlyREADMEGenerator, READMEModule
from pathlib import Path
from typing import get_type_hints

def test_type_annotations():
    """Test that Optional type annotations are properly set"""
    print("Testing type annotations...")
    
    # Check READMEGenerator annotations
    hints = get_type_hints(READMEGenerator)
    optional_fields = ['badges', 'features', 'contributing', 'license_info', 'acknowledgments']
    
    for field in optional_fields:
        if field in hints:
            print(f"✓ {field}: {hints[field]}")
        else:
            print(f"✗ {field}: Not found in type hints")
    
    # Check AppendOnlyREADMEGenerator annotations  
    append_hints = get_type_hints(AppendOnlyREADMEGenerator)
    append_fields = ['api_docs', 'architecture', 'development', 'testing', 'deployment', 'performance', 'security', 'troubleshooting']
    
    for field in append_fields:
        if field in append_hints:
            print(f"✓ {field}: {append_hints[field]}")
        else:
            print(f"✗ {field}: Not found in type hints")

def test_none_handling():
    """Test that assembly logic handles None values correctly"""
    print("\nTesting None value handling...")
    
    # Create a mock result object
    class MockResult:
        title = "Test Project"
        overview = "Test overview"
        badges = None  # This should be skipped
        features = "- Feature 1\n- Feature 2"
        prerequisites = "Python 3.8+"
        installation = "pip install test"
        usage = "python test.py"
        file_structure = "test.py - main file"
        contributing = None  # This should be skipped
        license_info = None  # This should be skipped
        acknowledgments = "Thanks to everyone"
    
    # Test assembly logic
    module = READMEModule()
    readme_content = module._assemble_readme(MockResult())
    
    print("Generated README content:")
    print("-" * 40)
    print(readme_content)
    print("-" * 40)
    
    # Check that None fields are not included
    assert "## Contributing" not in readme_content, "Contributing section should be omitted when None"
    assert "## License" not in readme_content, "License section should be omitted when None" 
    assert "badges" not in readme_content.lower(), "Badges should be omitted when None"
    assert "## Features" in readme_content, "Features should be included when not None"
    assert "## Acknowledgments" in readme_content, "Acknowledgments should be included when not None"
    
    print("✓ None value handling works correctly!")

if __name__ == "__main__":
    test_type_annotations()
    test_none_handling()
    print("\n✓ All tests passed!")