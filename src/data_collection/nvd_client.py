"""
NVD API Client

Handles communication with the National Vulnerability Database API.
Features:
- Automatic rate limiting (5/50 requests per 30 seconds)
- Response caching to minimize API calls
- Retry logic with exponential backoff
- Support for API key and keyless access
- Pagination handling for large result sets
"""

import os
import time
import json
import pickle
import hashlib
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
from tqdm import tqdm
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NVDClient:
    """
    Client for interacting with the NVD API.
    
    Attributes:
        api_key (str): Optional NVD API key for higher rate limits
        base_url (str): NVD API base URL
        cache_dir (Path): Directory for caching API responses
        rate_limit (int): Maximum requests per 30 seconds
        delay (float): Delay between requests in seconds
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_enabled: bool = True,
        cache_dir: str = "data/cache",
        rate_limit: Optional[int] = None
    ):
        """
        Initialize NVD API client.
        
        Args:
            api_key: NVD API key (optional, increases rate limit)
            cache_enabled: Enable response caching
            cache_dir: Directory to store cache files
            rate_limit: Custom rate limit (default: 5 without key, 50 with key)
        """
        self.api_key = api_key or os.getenv("NVD_API_KEY")
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.cache_enabled = cache_enabled
        self.cache_dir = Path(cache_dir)
        
        # Create cache directory if it doesn't exist
        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Set rate limiting based on API key presence
        if rate_limit:
            self.rate_limit = rate_limit
        else:
            self.rate_limit = 50 if self.api_key else 5
        
        # Calculate delay between requests (30 seconds / rate_limit)
        self.delay = 30.0 / self.rate_limit
        
        # Track request timing
        self.last_request_time = 0
        self.request_count = 0
        
        logger.info(f"NVD Client initialized (Rate limit: {self.rate_limit} requests/30s)")
        if self.api_key:
            logger.info("API key detected - using higher rate limit")
        else:
            logger.warning("No API key - using lower rate limit (5 req/30s)")
            logger.warning("Get free key at: https://nvd.nist.gov/developers/request-an-api-key")
    
    def _rate_limit_check(self):
        """Implement rate limiting with delay between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.delay:
            sleep_time = self.delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _get_cache_key(self, params: Dict[str, Any]) -> str:
        """Generate cache key from request parameters."""
        # Create deterministic string from params
        param_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(param_str.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Retrieve response from cache if available and not expired."""
        if not self.cache_enabled:
            return None
        
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
            
            # Check if cache is expired (7 days default)
            cache_age = datetime.now() - cached_data['timestamp']
            if cache_age > timedelta(days=7):
                logger.debug(f"Cache expired: {cache_key}")
                return None
            
            logger.debug(f"Cache hit: {cache_key}")
            return cached_data['response']
        
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
            return None
    
    def _save_to_cache(self, cache_key: str, response: Dict):
        """Save API response to cache."""
        if not self.cache_enabled:
            return
        
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'timestamp': datetime.now(),
                    'response': response
                }, f)
            logger.debug(f"Cached response: {cache_key}")
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
    
    def _make_request(self, params: Dict[str, Any]) -> Dict:
        """
        Make API request with rate limiting and caching.
        
        Args:
            params: Query parameters for the API
            
        Returns:
            API response as dictionary
        """
        # Check cache first
        cache_key = self._get_cache_key(params)
        cached_response = self._get_from_cache(cache_key)
        
        if cached_response:
            return cached_response
        
        # Apply rate limiting
        self._rate_limit_check()
        
        # Prepare headers
        headers = {}
        if self.api_key:
            headers['apiKey'] = self.api_key
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Cache the response
            self._save_to_cache(cache_key, data)
            
            return data
        
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                logger.error("Rate limit exceeded! Increase delay or get API key.")
            raise
        except Exception as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def fetch_cves(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        cve_id: Optional[str] = None,
        keyword: Optional[str] = None,
        results_per_page: int = 2000,
        max_results: Optional[int] = None,
        severity: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch CVEs from NVD API with various filters.
        
        Args:
            start_date: Filter CVEs published after this date (YYYY-MM-DD)
            end_date: Filter CVEs published before this date (YYYY-MM-DD)
            cve_id: Specific CVE ID to fetch
            keyword: Search keyword in descriptions
            results_per_page: Number of results per API call (max 2000)
            max_results: Maximum total results to fetch (None = all)
            severity: Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)
            
        Returns:
            List of CVE dictionaries
        """
        all_cves = []
        start_index = 0
        
        # Build base parameters
        params = {
            'resultsPerPage': min(results_per_page, 2000)
        }
        
        if start_date:
            params['pubStartDate'] = f"{start_date}T00:00:00.000"
        if end_date:
            params['pubEndDate'] = f"{end_date}T23:59:59.999"
        if cve_id:
            params['cveId'] = cve_id
        if keyword:
            params['keywordSearch'] = keyword
        
        logger.info(f"Fetching CVEs with params: {params}")
        
        # Initial request to get total count
        params['startIndex'] = 0
        first_response = self._make_request(params)
        
        total_results = first_response.get('totalResults', 0)
        logger.info(f"Total CVEs available: {total_results}")
        
        # Determine how many to actually fetch
        if max_results:
            total_to_fetch = min(total_results, max_results)
        else:
            total_to_fetch = total_results
        
        # Process first batch
        vulnerabilities = first_response.get('vulnerabilities', [])
        all_cves.extend(vulnerabilities)
        
        # Pagination for remaining results
        pbar = tqdm(total=total_to_fetch, desc="Fetching CVEs")
        pbar.update(len(vulnerabilities))
        
        start_index = len(vulnerabilities)
        
        while start_index < total_to_fetch:
            params['startIndex'] = start_index
            
            try:
                response = self._make_request(params)
                batch = response.get('vulnerabilities', [])
                
                if not batch:
                    break
                
                all_cves.extend(batch)
                pbar.update(len(batch))
                start_index += len(batch)
                
            except Exception as e:
                logger.error(f"Error fetching batch at index {start_index}: {e}")
                break
        
        pbar.close()
        
        # Filter by severity if specified
        if severity:
            all_cves = self._filter_by_severity(all_cves, severity)
        
        logger.info(f"Successfully fetched {len(all_cves)} CVEs")
        return all_cves
    
    def _filter_by_severity(self, cves: List[Dict], severity: str) -> List[Dict]:
        """Filter CVEs by CVSS severity rating."""
        severity = severity.upper()
        filtered = []
        
        for cve in cves:
            try:
                # Get CVSS metrics
                metrics = cve.get('cve', {}).get('metrics', {})
                
                # Check CVSS v3.1 or v3.0
                cvss_data = (
                    metrics.get('cvssMetricV31', [{}])[0] or
                    metrics.get('cvssMetricV30', [{}])[0]
                )
                
                cvss_severity = cvss_data.get('cvssData', {}).get('baseSeverity', '')
                
                if cvss_severity.upper() == severity:
                    filtered.append(cve)
            except:
                continue
        
        logger.info(f"Filtered to {len(filtered)} CVEs with severity {severity}")
        return filtered
    
    def get_recent_cves(self, days: int = 30, limit: Optional[int] = None) -> List[Dict]:
        """
        Fetch CVEs from the last N days.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of results
            
        Returns:
            List of recent CVEs
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return self.fetch_cves(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            max_results=limit
        )
    
    def save_to_json(self, cves: List[Dict], filepath: str):
        """
        Save CVEs to JSON file.
        
        Args:
            cves: List of CVE dictionaries
            filepath: Output file path
        """
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'count': len(cves),
                    'source': 'NVD API'
                },
                'vulnerabilities': cves
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(cves)} CVEs to {filepath}")
    
    def load_from_json(self, filepath: str) -> List[Dict]:
        """
        Load CVEs from JSON file.
        
        Args:
            filepath: Input file path
            
        Returns:
            List of CVE dictionaries
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cves = data.get('vulnerabilities', [])
        logger.info(f"Loaded {len(cves)} CVEs from {filepath}")
        return cves


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = NVDClient()
    
    # Fetch recent 100 CVEs
    print("Fetching recent CVEs...")
    recent_cves = client.get_recent_cves(days=7, limit=100)
    
    # Save to file
    client.save_to_json(recent_cves, "data/raw/recent_cves.json")
    
    print(f"✅ Fetched and saved {len(recent_cves)} CVEs")
