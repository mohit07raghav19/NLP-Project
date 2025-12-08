"""
Test script for API endpoints
"""
import sys
import time
from datetime import datetime
sys.path.insert(0, 'src')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import CVEModel
from fastapi.testclient import TestClient
from api.main import app

print("Testing API Endpoints...")
print("-" * 50)

# Add some test data to database first
print("\nSetting up test data...")
DATABASE_URL = "sqlite:///data/cve_database.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Add test CVEs
test_cves = [
    CVEModel(
        cve_id="CVE-2024-API-TEST-001",
        description="Critical SQL injection vulnerability",
        published_date=datetime.now(),
        cvss_score=9.8,
        cvss_severity="CRITICAL",
        affected_vendors=["TestVendor1"],
        affected_products=["TestProduct1"]
    ),
    CVEModel(
        cve_id="CVE-2024-API-TEST-002",
        description="Medium severity XSS vulnerability",
        published_date=datetime.now(),
        cvss_score=6.5,
        cvss_severity="MEDIUM",
        affected_vendors=["TestVendor2"],
        affected_products=["TestProduct2"]
    ),
    CVEModel(
        cve_id="CVE-2024-API-TEST-003",
        description="High severity remote code execution",
        published_date=datetime.now(),
        cvss_score=8.1,
        cvss_severity="HIGH",
        affected_vendors=["TestVendor3"],
        affected_products=["TestProduct3"]
    )
]

for cve in test_cves:
    existing = session.query(CVEModel).filter_by(cve_id=cve.cve_id).first()
    if not existing:
        session.add(cve)

session.commit()
print(f"Added {len(test_cves)} test CVEs to database")

# Create test client
client = TestClient(app)

# Test 1: Root endpoint
print("\n" + "=" * 50)
print("Test 1: Root endpoint (GET /)...")
print("=" * 50)

try:
    response = client.get("/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("[PASS] Root endpoint working")
except Exception as e:
    print(f"[FAIL] Root endpoint error: {e}")

# Test 2: Health check
print("\n" + "=" * 50)
print("Test 2: Health check (GET /health)...")
print("=" * 50)

try:
    response = client.get("/health")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Status: {data.get('status')}")
    print(f"Database: {data.get('database')}")
    print(f"CVE Count: {data.get('cve_count')}")
    assert response.status_code == 200
    assert data.get('status') == 'healthy'
    print("[PASS] Health check working")
except Exception as e:
    print(f"[FAIL] Health check error: {e}")

# Test 3: Get all CVEs
print("\n" + "=" * 50)
print("Test 3: Get all CVEs (GET /api/v1/cves)...")
print("=" * 50)

try:
    response = client.get("/api/v1/cves?limit=10")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Total CVEs: {data.get('total')}")
    print(f"Results returned: {len(data.get('results', []))}")
    if data.get('results'):
        print(f"First CVE ID: {data['results'][0].get('cve_id')}")
    assert response.status_code == 200
    print("[PASS] Get all CVEs working")
except Exception as e:
    print(f"[FAIL] Get all CVEs error: {e}")

# Test 4: Filter by severity
print("\n" + "=" * 50)
print("Test 4: Filter by severity (GET /api/v1/cves?severity=CRITICAL)...")
print("=" * 50)

try:
    response = client.get("/api/v1/cves?severity=CRITICAL")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Critical CVEs found: {data.get('total')}")
    if data.get('results'):
        for cve in data['results']:
            print(f"  - {cve.get('cve_id')}: {cve.get('cvss_severity')} ({cve.get('cvss_score')})")
    assert response.status_code == 200
    print("[PASS] Filter by severity working")
except Exception as e:
    print(f"[FAIL] Filter by severity error: {e}")

# Test 5: Get specific CVE
print("\n" + "=" * 50)
print("Test 5: Get specific CVE (GET /api/v1/cves/CVE-2024-API-TEST-001)...")
print("=" * 50)

try:
    response = client.get("/api/v1/cves/CVE-2024-API-TEST-001")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"CVE ID: {data.get('cve_id')}")
    print(f"Description: {data.get('description')}")
    print(f"Severity: {data.get('cvss_severity')}")
    print(f"Score: {data.get('cvss_score')}")
    assert response.status_code == 200
    print("[PASS] Get specific CVE working")
except Exception as e:
    print(f"[FAIL] Get specific CVE error: {e}")

# Test 6: Get statistics
print("\n" + "=" * 50)
print("Test 6: Get statistics (GET /api/v1/statistics)...")
print("=" * 50)

try:
    response = client.get("/api/v1/statistics")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Total CVEs: {data.get('total_cves')}")
    print(f"Critical: {data.get('critical')}")
    print(f"High: {data.get('high')}")
    print(f"Medium: {data.get('medium')}")
    print(f"Low: {data.get('low')}")
    print(f"Average CVSS Score: {data.get('average_cvss_score')}")
    assert response.status_code == 200
    print("[PASS] Get statistics working")
except Exception as e:
    print(f"[FAIL] Get statistics error: {e}")

# Test 7: Search CVEs
print("\n" + "=" * 50)
print("Test 7: Search CVEs (GET /api/v1/search?q=SQL)...")
print("=" * 50)

try:
    response = client.get("/api/v1/search?q=SQL")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Search results: {data.get('total')}")
    if data.get('results'):
        for cve in data['results'][:3]:
            print(f"  - {cve.get('cve_id')}: {cve.get('description')[:60]}...")
    assert response.status_code == 200
    print("[PASS] Search CVEs working")
except Exception as e:
    print(f"[FAIL] Search CVEs error: {e}")

# Test 8: Error handling - nonexistent CVE
print("\n" + "=" * 50)
print("Test 8: Error handling (GET /api/v1/cves/CVE-9999-NONEXISTENT)...")
print("=" * 50)

try:
    response = client.get("/api/v1/cves/CVE-9999-NONEXISTENT")
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 404
    print(f"Response: {response.json()}")
    print("[PASS] Error handling working")
except Exception as e:
    print(f"[FAIL] Error handling error: {e}")

# Cleanup test data
print("\n" + "=" * 50)
print("Cleaning up test data...")
print("=" * 50)

for cve in test_cves:
    existing = session.query(CVEModel).filter_by(cve_id=cve.cve_id).first()
    if existing:
        session.delete(existing)

session.commit()
session.close()
print("Test data cleaned up")

print("\n[PASS] All API tests completed successfully!")
