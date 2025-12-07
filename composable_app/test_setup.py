#!/usr/bin/env python3
"""Quick test script to verify the setup is working."""
import os
import sys
from dotenv import load_dotenv

# Load from .env file
if os.path.exists('.env'):
    load_dotenv('.env')
    print("✅ Loaded .env file")
else:
    print("⚠️  No .env file found")
    print("   Please create .env file with OPENAI_API_KEY=sk-your-key-here")

# Check API key
api_key = os.getenv('OPENAI_API_KEY', '')
if not api_key or api_key.startswith('#'):
    print("\n❌ OPENAI_API_KEY is not set or is a placeholder!")
    print("   Please edit .env file and add:")
    print("   OPENAI_API_KEY=sk-your-actual-key-here")
    sys.exit(1)
elif not api_key.startswith('sk-'):
    print(f"\n⚠️  OPENAI_API_KEY doesn't start with 'sk-' (current: {api_key[:10]}...)")
    print("   Please verify your API key is correct")
else:
    print(f"\n✅ OPENAI_API_KEY is set (length: {len(api_key)})")

# Test imports
print("\n📦 Testing imports...")
try:
    from utils import llms
    print("✅ utils.llms imported")
    
    from agents import task_assigner
    print("✅ agents.task_assigner imported")
    
    import streamlit
    print("✅ streamlit imported")
    
    print("\n✅ All imports successful!")
    print("\n🚀 You can now run:")
    print("   uv run streamlit run streamlit_app.py")
    
except Exception as e:
    print(f"\n❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

