"""
Data Collection Package

This package handles fetching CVE data from various sources:
- NVD API client with rate limiting and caching
- Web scraping utilities for fallback data collection
- Data validation and storage
"""

__version__ = "0.1.0"
__all__ = ["NVDClient", "CVEScraper"]
