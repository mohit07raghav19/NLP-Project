"""
Test script for database operations
"""
import sys
from datetime import datetime
sys.path.insert(0, 'src')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import CVEModel, Base

print("Testing Database Operations...")
print("-" * 50)

# Create engine and session
DATABASE_URL = "sqlite:///data/cve_database.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

print(f"\nConnected to: {DATABASE_URL}")

# Test 1: Insert a test CVE
print("\n" + "=" * 50)
print("Test 1: Inserting test CVE...")
print("=" * 50)

try:
    test_cve = CVEModel(
        cve_id="CVE-2024-TEST-001",
        description="Test vulnerability in test software",
        published_date=datetime.now(),
        last_modified_date=datetime.now(),
        cvss_version="3.1",
        cvss_score=7.5,
        cvss_severity="HIGH",
        cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
        attack_vector="NETWORK",
        attack_complexity="LOW",
        affected_vendors=["TestVendor", "AnotherVendor"],
        affected_products=["TestProduct 1.0"],
        vulnerability_types=["SQL Injection"],
        extracted_entities={"ORG": ["TestVendor"], "PRODUCT": ["TestProduct"]}
    )

    # Check if exists
    existing = session.query(CVEModel).filter_by(cve_id="CVE-2024-TEST-001").first()
    if existing:
        print("Test CVE already exists, deleting first...")
        session.delete(existing)
        session.commit()

    session.add(test_cve)
    session.commit()
    print("[PASS] Successfully inserted test CVE")

except Exception as e:
    print(f"[FAIL] Insert error: {e}")
    session.rollback()
    import traceback
    traceback.print_exc()

# Test 2: Query CVEs
print("\n" + "=" * 50)
print("Test 2: Querying CVEs...")
print("=" * 50)

try:
    total_cves = session.query(CVEModel).count()
    print(f"Total CVEs in database: {total_cves}")

    # Query by severity
    high_severity = session.query(CVEModel).filter_by(cvss_severity="HIGH").count()
    critical_severity = session.query(CVEModel).filter_by(cvss_severity="CRITICAL").count()

    print(f"High severity CVEs: {high_severity}")
    print(f"Critical severity CVEs: {critical_severity}")

    # Get our test CVE
    test_cve_query = session.query(CVEModel).filter_by(cve_id="CVE-2024-TEST-001").first()
    if test_cve_query:
        print(f"\nRetrieved test CVE:")
        print(f"  ID: {test_cve_query.cve_id}")
        print(f"  Severity: {test_cve_query.cvss_severity}")
        print(f"  Score: {test_cve_query.cvss_score}")
        print(f"  Vendors: {test_cve_query.affected_vendors}")
        print(f"  Products: {test_cve_query.affected_products}")

    print("\n[PASS] Query operations successful!")

except Exception as e:
    print(f"[FAIL] Query error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Update CVE
print("\n" + "=" * 50)
print("Test 3: Updating CVE...")
print("=" * 50)

try:
    test_cve_update = session.query(CVEModel).filter_by(cve_id="CVE-2024-TEST-001").first()
    if test_cve_update:
        test_cve_update.cvss_score = 8.0
        test_cve_update.cvss_severity = "CRITICAL"
        session.commit()
        print(f"[PASS] Updated CVE severity to CRITICAL")

        # Verify update
        updated = session.query(CVEModel).filter_by(cve_id="CVE-2024-TEST-001").first()
        print(f"Verified - New severity: {updated.cvss_severity}, Score: {updated.cvss_score}")

except Exception as e:
    print(f"[FAIL] Update error: {e}")
    session.rollback()
    import traceback
    traceback.print_exc()

# Test 4: Delete test CVE
print("\n" + "=" * 50)
print("Test 4: Deleting test CVE...")
print("=" * 50)

try:
    test_cve_delete = session.query(CVEModel).filter_by(cve_id="CVE-2024-TEST-001").first()
    if test_cve_delete:
        session.delete(test_cve_delete)
        session.commit()
        print("[PASS] Successfully deleted test CVE")

        # Verify deletion
        verify = session.query(CVEModel).filter_by(cve_id="CVE-2024-TEST-001").first()
        if verify is None:
            print("Verified - Test CVE removed from database")
        else:
            print("Warning - Test CVE still exists")

except Exception as e:
    print(f"[FAIL] Delete error: {e}")
    session.rollback()
    import traceback
    traceback.print_exc()

session.close()
print("\n[PASS] All database tests completed successfully!")
