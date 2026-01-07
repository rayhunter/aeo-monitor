#!/usr/bin/env python3
"""
Quick diagnostic script to check Railway environment
Run this temporarily as your Railway start command to debug issues
"""
import os
import sys

print("=" * 60)
print("RAILWAY ENVIRONMENT CHECK")
print("=" * 60)

# Check critical environment variables
env_vars = {
    "PORT": os.getenv("PORT"),
    "APP_PASSWORD": "***" if os.getenv("APP_PASSWORD") else None,
    "OPENROUTER_API_KEY": "***" if os.getenv("OPENROUTER_API_KEY") else None,
    "POSTHOG_API_KEY": "***" if os.getenv("POSTHOG_API_KEY") else None,
}

print("\nEnvironment Variables:")
for key, value in env_vars.items():
    status = "✅" if value else "❌"
    print(f"  {status} {key}: {value}")

print("\nPython Info:")
print(f"  Python Version: {sys.version}")
print(f"  Python Path: {sys.executable}")

print("\nChecking Dependencies:")
try:
    import streamlit
    print(f"  ✅ Streamlit: {streamlit.__version__}")
except ImportError as e:
    print(f"  ❌ Streamlit: {e}")

try:
    import openai
    print(f"  ✅ OpenAI: {openai.__version__}")
except ImportError as e:
    print(f"  ❌ OpenAI: {e}")

try:
    import pandas
    print(f"  ✅ Pandas: {pandas.__version__}")
except ImportError as e:
    print(f"  ❌ Pandas: {e}")

print("\nFile Check:")
files = ["app.py", "suppress_warnings.py", ".streamlit/config.toml"]
for file in files:
    exists = "✅" if os.path.exists(file) else "❌"
    print(f"  {exists} {file}")

print("\n" + "=" * 60)
print("If all checks pass, the issue might be with Streamlit startup")
print("Check Railway logs for Streamlit-specific errors")
print("=" * 60)

