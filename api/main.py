"""
FastAPI Backend for CVE NLP System

REST API endpoints for accessing processed CVE data.

To run:
    uvicorn api.main:app --reload

API Documentation available at:
    http://localhost:8000/docs (Swagger UI)
    http://localhost:8000/redoc (ReDoc)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import CVEModel
from src.utils.config import get_database_url

# Initialize FastAPI app
app = FastAPI(
    title="CVE NLP Analysis API",
    description="RESTful API for accessing CVE vulnerability data processed with NLP",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
try:
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"⚠️ Database connection error: {e}")
    print("Run: python scripts/setup_database.py")


# Pydantic models for API responses
class CVEResponse(BaseModel):
    cve_id: str
    description: str
    published_date: Optional[datetime]
    cvss_score: Optional[float]
    cvss_severity: Optional[str]
    affected_vendors: Optional[List[str]]
    affected_products: Optional[List[str]]
    
    class Config:
        from_attributes = True


class CVEListResponse(BaseModel):
    total: int
    results: List[CVEResponse]


class StatisticsResponse(BaseModel):
    total_cves: int
    critical: int
    high: int
    medium: int
    low: int
    average_cvss_score: float


# API Routes

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "CVE NLP Analysis API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "cves": "/api/v1/cves",
            "statistics": "/api/v1/statistics",
            "search": "/api/v1/search"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    try:
        db = SessionLocal()
        count = db.query(CVEModel).count()
        db.close()
        return {
            "status": "healthy",
            "database": "connected",
            "cve_count": count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@app.get("/api/v1/cves", response_model=CVEListResponse, tags=["CVEs"])
async def get_cves(
    limit: int = Query(100, ge=1, le=1000, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    severity: Optional[str] = Query(None, description="Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)"),
    min_cvss: Optional[float] = Query(None, ge=0, le=10, description="Minimum CVSS score")
):
    """
    Get list of CVEs with optional filtering.
    
    Parameters:
    - **limit**: Maximum number of results (1-1000)
    - **offset**: Pagination offset
    - **severity**: Filter by severity level
    - **min_cvss**: Minimum CVSS score threshold
    """
    try:
        db = SessionLocal()
        query = db.query(CVEModel)
        
        # Apply filters
        if severity:
            query = query.filter(CVEModel.cvss_severity == severity.upper())
        if min_cvss is not None:
            query = query.filter(CVEModel.cvss_score >= min_cvss)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        results = query.offset(offset).limit(limit).all()
        
        db.close()
        
        return {
            "total": total,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/cves/{cve_id}", response_model=CVEResponse, tags=["CVEs"])
async def get_cve(cve_id: str):
    """
    Get specific CVE by ID.
    
    Parameters:
    - **cve_id**: CVE identifier (e.g., CVE-2024-1234)
    """
    try:
        db = SessionLocal()
        cve = db.query(CVEModel).filter(CVEModel.cve_id == cve_id).first()
        db.close()
        
        if not cve:
            raise HTTPException(status_code=404, detail=f"CVE {cve_id} not found")
        
        return cve
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/statistics", response_model=StatisticsResponse, tags=["Statistics"])
async def get_statistics():
    """
    Get overall CVE statistics.
    """
    try:
        db = SessionLocal()
        
        total = db.query(CVEModel).count()
        critical = db.query(CVEModel).filter(CVEModel.cvss_severity == "CRITICAL").count()
        high = db.query(CVEModel).filter(CVEModel.cvss_severity == "HIGH").count()
        medium = db.query(CVEModel).filter(CVEModel.cvss_severity == "MEDIUM").count()
        low = db.query(CVEModel).filter(CVEModel.cvss_severity == "LOW").count()
        
        # Calculate average CVSS score
        from sqlalchemy import func
        avg_score = db.query(func.avg(CVEModel.cvss_score)).filter(CVEModel.cvss_score > 0).scalar() or 0.0
        
        db.close()
        
        return {
            "total_cves": total,
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "average_cvss_score": round(avg_score, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/search", response_model=CVEListResponse, tags=["Search"])
async def search_cves(
    q: str = Query(..., min_length=3, description="Search query"),
    limit: int = Query(50, ge=1, le=500)
):
    """
    Search CVEs by keyword in description.
    
    Parameters:
    - **q**: Search query (minimum 3 characters)
    - **limit**: Maximum results
    """
    try:
        db = SessionLocal()
        
        # Search in description
        query = db.query(CVEModel).filter(CVEModel.description.contains(q))
        
        total = query.count()
        results = query.limit(limit).all()
        
        db.close()
        
        return {
            "total": total,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run with: uvicorn api.main:app --reload
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting CVE NLP API server...")
    print("📚 API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
