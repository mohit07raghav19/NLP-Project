"""
SQLAlchemy Database Models

Define database schema for CVE data storage.
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, JSON, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# Association table for many-to-many relationship between CVEs and CWEs
cve_cwe_association = Table(
    'cve_cwe',
    Base.metadata,
    Column('cve_id', String, ForeignKey('cves.cve_id'), primary_key=True),
    Column('cwe_id', String, ForeignKey('cwes.cwe_id'), primary_key=True)
)


# Association table for CVEs and References
cve_reference_association = Table(
    'cve_references',
    Base.metadata,
    Column('cve_id', String, ForeignKey('cves.cve_id'), primary_key=True),
    Column('reference_id', Integer, ForeignKey('references.id'), primary_key=True)
)


class CVEModel(Base):
    """
    Main CVE table storing vulnerability information.
    """
    __tablename__ = 'cves'
    
    # Primary identification
    cve_id = Column(String(20), primary_key=True, index=True)
    
    # Description and metadata
    description = Column(Text, nullable=False)
    published_date = Column(DateTime, index=True)
    last_modified_date = Column(DateTime)
    
    # CVSS Scoring
    cvss_version = Column(String(10))
    cvss_score = Column(Float, index=True)
    cvss_severity = Column(String(20), index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    cvss_vector = Column(String(100))
    
    # CVSS v3 metrics
    attack_vector = Column(String(20))
    attack_complexity = Column(String(20))
    privileges_required = Column(String(20))
    user_interaction = Column(String(20))
    scope = Column(String(20))
    confidentiality_impact = Column(String(20))
    integrity_impact = Column(String(20))
    availability_impact = Column(String(20))
    
    # Extracted entities (JSON for flexibility)
    affected_products = Column(JSON)  # List of products
    affected_vendors = Column(JSON)   # List of vendors
    vulnerability_types = Column(JSON)  # List of vulnerability types
    extracted_entities = Column(JSON)  # All NER entities
    
    # Additional metadata
    source = Column(String(50), default="NVD")
    status = Column(String(20))  # e.g., "Analyzed", "Awaiting Analysis"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cwes = relationship("CWEModel", secondary=cve_cwe_association, back_populates="cves")
    references = relationship("ReferenceModel", secondary=cve_reference_association, back_populates="cves")
    
    def __repr__(self):
        return f"<CVE {self.cve_id}: {self.cvss_severity} ({self.cvss_score})>"


class CWEModel(Base):
    """
    Common Weakness Enumeration table.
    """
    __tablename__ = 'cwes'
    
    cwe_id = Column(String(20), primary_key=True, index=True)
    name = Column(String(200))
    description = Column(Text)
    
    # Relationships
    cves = relationship("CVEModel", secondary=cve_cwe_association, back_populates="cwes")
    
    def __repr__(self):
        return f"<CWE {self.cwe_id}: {self.name}>"


class ReferenceModel(Base):
    """
    External references and advisories for CVEs.
    """
    __tablename__ = 'references'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(500), nullable=False)
    source = Column(String(100))
    tags = Column(JSON)  # List of tags like "Patch", "Vendor Advisory"
    
    # Relationships
    cves = relationship("CVEModel", secondary=cve_reference_association, back_populates="references")
    
    def __repr__(self):
        return f"<Reference {self.id}: {self.source}>"


class CPEModel(Base):
    """
    Common Platform Enumeration - affected product configurations.
    """
    __tablename__ = 'cpes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cve_id = Column(String(20), ForeignKey('cves.cve_id'), index=True)
    
    cpe_uri = Column(String(500))
    vendor = Column(String(100), index=True)
    product = Column(String(100), index=True)
    version = Column(String(50))
    update_version = Column(String(50))
    edition = Column(String(50))
    
    vulnerable = Column(String(10))  # true/false
    version_start_including = Column(String(50))
    version_start_excluding = Column(String(50))
    version_end_including = Column(String(50))
    version_end_excluding = Column(String(50))
    
    def __repr__(self):
        return f"<CPE {self.vendor}:{self.product}:{self.version}>"


class AnalysisMetrics(Base):
    """
    Store analysis metrics and statistics.
    """
    __tablename__ = 'analysis_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Timestamp
    analysis_date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Counts
    total_cves = Column(Integer)
    critical_count = Column(Integer)
    high_count = Column(Integer)
    medium_count = Column(Integer)
    low_count = Column(Integer)
    
    # Top entities (JSON)
    top_vendors = Column(JSON)
    top_products = Column(JSON)
    top_cwes = Column(JSON)
    top_vuln_types = Column(JSON)
    
    # Additional metrics
    metrics_data = Column(JSON)  # Flexible storage for custom metrics
    
    def __repr__(self):
        return f"<Metrics {self.analysis_date}: {self.total_cves} CVEs>"


# Example of creating all tables
if __name__ == "__main__":
    from sqlalchemy import create_engine
    
    # Create SQLite database
    engine = create_engine('sqlite:///data/cve_database.db', echo=True)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    print("✅ Database schema created successfully!")
