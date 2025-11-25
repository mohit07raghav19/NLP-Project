#!/usr/bin/env python3
"""
Database Setup Script

Initialize the CVE database with proper schema and tables.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from src.database.models import Base
from src.utils.config import get_database_url
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_database(database_url: str = None):
    """
    Create database and all tables.
    
    Args:
        database_url: Database connection string (default from config)
    """
    if database_url is None:
        database_url = get_database_url()
    
    logger.info(f"Setting up database: {database_url}")
    
    # Create engine
    engine = create_engine(database_url, echo=False)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    logger.info("✅ Database schema created successfully!")
    logger.info(f"📊 Tables created: {', '.join(Base.metadata.tables.keys())}")
    
    return engine


if __name__ == "__main__":
    try:
        setup_database()
        print("\n🎉 Database setup complete!")
        print("\nYou can now:")
        print("  1. Run data collection: python scripts/run_pipeline.py --step collection")
        print("  2. Start API server: uvicorn api.main:app --reload")
        print("  3. Open Jupyter notebook: jupyter notebook notebooks/CVE_NLP_Pipeline.ipynb")
    except Exception as e:
        print(f"\n❌ Error setting up database: {e}")
        sys.exit(1)
