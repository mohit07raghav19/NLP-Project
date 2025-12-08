"""
Test script for NLP extraction module
"""
import sys
sys.path.insert(0, 'src')

from nlp.ner_extractor import NERExtractor
from preprocessing.cleaner import TextCleaner

print("Testing NLP Entity Extraction...")
print("-" * 50)

# Sample CVE description
sample_text = """
CVE-2024-1234 affects Apache Tomcat versions 9.0.0 to 9.0.70.
This vulnerability allows remote attackers to execute arbitrary code
through SQL injection in the authentication module.
The issue was discovered by researchers at Microsoft Security Response Center.
It has a CVSS score of 9.8 (Critical).
"""

print("\nSample Text:")
print(sample_text)

# Test text cleaner
print("\n" + "=" * 50)
print("Testing Text Cleaner...")
print("=" * 50)

try:
    cleaner = TextCleaner()
    cleaned = cleaner.clean(sample_text)
    cve_ids = cleaner.extract_cve_ids(sample_text)
    versions = cleaner.extract_versions(sample_text)

    print(f"\nCleaned text: {cleaned[:200]}...")
    print(f"CVE IDs found: {cve_ids}")
    print(f"Versions found: {versions}")
    print("\n[PASS] Text cleaning successful!")

except Exception as e:
    print(f"\n[FAIL] Text cleaning error: {e}")
    import traceback
    traceback.print_exc()

# Test NER extractor
print("\n" + "=" * 50)
print("Testing NER Extractor...")
print("=" * 50)

try:
    extractor = NERExtractor(model_name="en_core_web_sm")
    print(f"\nModel loaded: {extractor.model_name}")

    # Extract entities
    entities = extractor.extract_entities(sample_text)
    print(f"\nAll Entities extracted:")
    for label, items in entities.items():
        if items:
            print(f"  {label}: {items}")

    # Extract specific types
    products = extractor.extract_products(sample_text)
    vendors = extractor.extract_vendors(sample_text)
    vuln_types = extractor.extract_vulnerability_types(sample_text)

    print(f"\nProducts: {products}")
    print(f"Vendors: {vendors}")
    print(f"Vulnerability Types: {vuln_types}")

    # Get summary
    summary = extractor.get_entity_summary(sample_text)
    print(f"\nEntity Summary:")
    for key, value in summary.items():
        if value and key != 'all_entities':
            print(f"  {key}: {value}")

    print("\n[PASS] NLP extraction successful!")

except Exception as e:
    print(f"\n[FAIL] NLP extraction error: {e}")
    import traceback
    traceback.print_exc()
