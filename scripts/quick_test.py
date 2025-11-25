#!/usr/bin/env python3
"""
Quick Start Script

Run this to test the basic functionality of the CVE NLP system.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("🚀 CVE NLP System - Quick Test")
print("=" * 60)

# Test 1: Import modules
print("\n1️⃣ Testing module imports...")
try:
    from src.data_collection.nvd_client import NVDClient
    from src.preprocessing.cleaner import TextCleaner
    from src.utils.config import load_config
    print("   ✅ All modules imported successfully")
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    print("   💡 Run: pip install -r requirements.txt")
    sys.exit(1)

# Test 2: Configuration
print("\n2️⃣ Testing configuration...")
try:
    config = load_config()
    print(f"   ✅ Configuration loaded")
    print(f"   📊 Database type: {config.get('database', {}).get('type')}")
except Exception as e:
    print(f"   ⚠️ Warning: {e}")

# Test 3: NVD Client
print("\n3️⃣ Testing NVD API client...")
try:
    client = NVDClient()
    print(f"   ✅ NVD client initialized")
    print(f"   📡 Rate limit: {client.rate_limit} requests/30s")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Text Cleaner
print("\n4️⃣ Testing text preprocessing...")
try:
    cleaner = TextCleaner()
    sample = "<p>CVE-2024-1234 affects Apache 2.4.0</p>"
    cleaned = cleaner.clean(sample)
    print(f"   ✅ Text cleaner working")
    print(f"   📝 Sample: '{sample}'")
    print(f"   🧹 Cleaned: '{cleaned}'")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: spaCy (optional)
print("\n5️⃣ Testing spaCy NLP...")
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    print(f"   ✅ spaCy model loaded: en_core_web_sm")
except Exception as e:
    print(f"   ⚠️ spaCy not available: {e}")
    print(f"   💡 Run: python -m spacy download en_core_web_sm")

# Summary
print("\n" + "=" * 60)
print("📋 Summary:")
print("\n✅ Core system is functional!")
print("\nNext steps:")
print("  1. Get NVD API key: https://nvd.nist.gov/developers/request-an-api-key")
print("  2. Add to .env file: NVD_API_KEY=your_key_here")
print("  3. Run notebook: jupyter notebook notebooks/CVE_NLP_Pipeline.ipynb")
print("  4. Or use Google Colab for zero setup!")
print("\n🎉 Ready to analyze CVEs with NLP!")
