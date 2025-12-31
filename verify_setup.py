"""
Verify that the AI Incident Responder setup is correct
"""

import sys
import os
from pathlib import Path

def check_backend():
    """Check backend setup"""
    print("🔍 Checking backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Check required files
    required_files = [
        "main.py",
        "requirements.txt",
        "models/incident.py",
        "services/datadog_service.py",
        "services/gemini_service.py",
        "services/slack_service.py"
    ]
    
    all_good = True
    for file in required_files:
        file_path = backend_dir / file
        if file_path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            all_good = False
    
    # Check if venv exists
    venv_path = backend_dir / "venv"
    if venv_path.exists():
        print("  ✅ Virtual environment exists")
    else:
        print("  ⚠️  Virtual environment not found (run: cd backend && python -m venv venv)")
    
    return all_good

def check_frontend():
    """Check frontend setup"""
    print("\n🔍 Checking frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Check required files
    required_files = [
        "package.json",
        "vite.config.js",
        "src/App.jsx",
        "src/main.jsx",
        "index.html"
    ]
    
    all_good = True
    for file in required_files:
        file_path = frontend_dir / file
        if file_path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            all_good = False
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        print("  ✅ node_modules exists")
    else:
        print("  ⚠️  node_modules not found (run: cd frontend && npm install)")
    
    return all_good

def check_env_file():
    """Check environment configuration"""
    print("\n🔍 Checking environment configuration...")
    
    env_file = Path("backend/.env")
    env_example = Path("backend/.env.example")
    
    if env_example.exists():
        print("  ✅ .env.example exists")
    else:
        print("  ⚠️  .env.example not found")
    
    if env_file.exists():
        print("  ✅ .env file exists")
        
        # Check if it has actual values (not just placeholders)
        with open(env_file) as f:
            content = f.read()
            if "your_" in content or "YOUR" in content:
                print("  ⚠️  .env file contains placeholder values")
                print("     (This is OK - system works in mock mode)")
    else:
        print("  ⚠️  .env file not found")
        print("     (This is OK - system works in mock mode)")
        print("     Copy .env.example to .env to configure API keys")

def main():
    """Run all checks"""
    print("="*50)
    print("🧪 AI Incident Responder - Setup Verification")
    print("="*50)
    print()
    
    backend_ok = check_backend()
    frontend_ok = check_frontend()
    check_env_file()
    
    print("\n" + "="*50)
    if backend_ok and frontend_ok:
        print("✅ Setup looks good!")
        print("\nNext steps:")
        print("  1. cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt")
        print("  2. cd frontend && npm install")
        print("  3. Start backend: cd backend && python -m uvicorn main:app --reload")
        print("  4. Start frontend: cd frontend && npm run dev")
        print("  5. Open http://localhost:3000")
    else:
        print("❌ Some issues found. Please fix them before proceeding.")
    print("="*50)

if __name__ == "__main__":
    main()


