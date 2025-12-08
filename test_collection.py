"""
Test script for data collection module
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from data_collection.nvd_client import NVDClient

print("Testing NVD Client...")
print("-" * 50)

# Initialize client
client = NVDClient(cache_enabled=True)

print(f"\nRate limit: {client.rate_limit} requests/30s")
print(f"Cache enabled: {client.cache_enabled}")

# Fetch a small number of recent CVEs
print("\nFetching 10 recent CVEs...")
try:
    cves = client.get_recent_cves(days=7, limit=10)

    print(f"\nSuccess! Fetched {len(cves)} CVEs")

    if cves:
        # Display first CVE
        sample = cves[0]
        cve_data = sample.get('cve', {})
        cve_id = cve_data.get('id', 'N/A')
        descriptions = cve_data.get('descriptions', [])
        description = descriptions[0].get('value', 'N/A')[:200] if descriptions else 'N/A'

        print(f"\nSample CVE:")
        print(f"  ID: {cve_id}")
        print(f"  Description: {description}...")

        # Save to file
        output_file = "data/raw/test_cves.json"
        client.save_to_json(cves, output_file)
        print(f"\nSaved to: {output_file}")

        print("\n[PASS] Data collection test successful!")
    else:
        print("\n[WARN] No CVEs returned")

except Exception as e:
    print(f"\n[FAIL] Error: {e}")
    import traceback
    traceback.print_exc()
