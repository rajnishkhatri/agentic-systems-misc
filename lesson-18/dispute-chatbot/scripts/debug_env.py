import sys
import os
import site

print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")
print("sys.path:")
for p in sys.path:
    print(f"  {p}")

print("\nSite packages:")
for p in site.getsitepackages():
    print(f"  {p}")

print("\nTrying import torch...")
try:
    import torch
    print(f"Success! torch version: {torch.__version__}")
    print(f"torch file: {torch.__file__}")
except ImportError as e:
    print(f"ImportError: {e}")

print("\nTrying import sentence_transformers...")
try:
    import sentence_transformers
    print(f"Success! sentence_transformers version: {sentence_transformers.__version__}")
except ImportError as e:
    print(f"ImportError: {e}")



