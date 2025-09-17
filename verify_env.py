#!/usr/bin/env python3
"""
Virtual Environment Verification Script
Verifies that the virtual environment is properly set up with all dependencies
"""

import sys
import os

def verify_virtual_env():
    """Verify that we're running in a virtual environment"""
    print("=== Virtual Environment Verification ===")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Running in virtual environment")
    else:
        print("✗ NOT running in virtual environment")
        return False
    
    return True

def verify_dependencies():
    """Verify that all required dependencies are installed"""
    print("\n=== Dependency Verification ===")
    dependencies = ['pygame', 'PIL']
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep} is installed")
        except ImportError:
            print(f"✗ {dep} is NOT installed")
            return False
    
    return True

def verify_project_structure():
    """Verify that the project structure is correct"""
    print("\n=== Project Structure Verification ===")
    required_files = [
        'main.py',
        'requirements.txt',
        'activate_env.bat',
        'activate_env.sh',
        'src',
        'config',
        'assets',
        'tests'
    ]
    
    for item in required_files:
        if os.path.exists(item):
            print(f"✓ {item} exists")
        else:
            print(f"✗ {item} is missing")
            return False
    
    return True

if __name__ == "__main__":
    print("Zelda-like 2D Game - Environment Verification")
    print("=" * 50)
    
    env_ok = verify_virtual_env()
    deps_ok = verify_dependencies()
    structure_ok = verify_project_structure()
    
    print("\n=== Summary ===")
    if env_ok and deps_ok and structure_ok:
        print("✓ All verifications passed! Environment is ready for development.")
        sys.exit(0)
    else:
        print("✗ Some verifications failed. Please check the issues above.")
        sys.exit(1)