"""
Statistical Analysis Module

Calculate statistical metrics and distributions from CVE data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class StatisticsCalculator:
    """Calculate statistical metrics from CVE data."""

    def __init__(self, session=None, df: Optional[pd.DataFrame] = None):
        """
        Initialize with either database session or DataFrame.

        Args:
            session: SQLAlchemy session for database queries (optional)
            df: Pandas DataFrame with CVE data (optional)
        """
        self.session = session
        self.df = df

        if df is not None:
            # Ensure published_date is datetime
            if 'published_date' in self.df.columns:
                self.df['published_date'] = pd.to_datetime(self.df['published_date'])

    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Calculate basic summary statistics.

        Returns:
            Dictionary with:
            - total_cves: int
            - date_range: {'start': date, 'end': date, 'days': int}
            - severity_distribution: {'CRITICAL': int, 'HIGH': int, ...}
            - cvss_stats: {'mean': float, 'median': float, 'std': float, 'min': float, 'max': float}
            - attack_vector_distribution: {'NETWORK': int, ...}
            - attack_complexity_distribution: {'LOW': int, 'HIGH': int}
        """
        if self.df is None or len(self.df) == 0:
            return {
                'total_cves': 0,
                'date_range': {'start': None, 'end': None, 'days': 0},
                'severity_distribution': {},
                'cvss_stats': {},
                'attack_vector_distribution': {},
                'attack_complexity_distribution': {}
            }

        # Total CVEs
        total_cves = len(self.df)

        # Date range
        if 'published_date' in self.df.columns:
            start_date = self.df['published_date'].min()
            end_date = self.df['published_date'].max()
            days = (end_date - start_date).days if start_date and end_date else 0
        else:
            start_date = end_date = None
            days = 0

        # Severity distribution
        severity_dist = {}
        if 'cvss_severity' in self.df.columns:
            severity_dist = self.df['cvss_severity'].value_counts().to_dict()

        # CVSS statistics
        cvss_stats = {}
        if 'cvss_score' in self.df.columns:
            cvss_scores = self.df['cvss_score'].dropna()
            cvss_scores = cvss_scores[cvss_scores > 0]  # Filter out zeros
            if len(cvss_scores) > 0:
                cvss_stats = {
                    'mean': float(cvss_scores.mean()),
                    'median': float(cvss_scores.median()),
                    'std': float(cvss_scores.std()),
                    'min': float(cvss_scores.min()),
                    'max': float(cvss_scores.max())
                }

        # Attack vector distribution
        attack_vector_dist = {}
        if 'attack_vector' in self.df.columns:
            attack_vector_dist = self.df[self.df['attack_vector'] != '']['attack_vector'].value_counts().to_dict()

        # Attack complexity distribution
        attack_complexity_dist = {}
        if 'attack_complexity' in self.df.columns:
            attack_complexity_dist = self.df[self.df['attack_complexity'] != '']['attack_complexity'].value_counts().to_dict()

        return {
            'total_cves': total_cves,
            'date_range': {
                'start': start_date,
                'end': end_date,
                'days': days
            },
            'severity_distribution': severity_dist,
            'cvss_stats': cvss_stats,
            'attack_vector_distribution': attack_vector_dist,
            'attack_complexity_distribution': attack_complexity_dist
        }

    def calculate_severity_percentages(self) -> Dict[str, float]:
        """
        Calculate percentage distribution of severities.

        Returns:
            Dictionary like {'CRITICAL': 15.2, 'HIGH': 42.1, 'MEDIUM': 35.8, 'LOW': 6.9}
        """
        if self.df is None or len(self.df) == 0:
            return {}

        if 'cvss_severity' not in self.df.columns:
            return {}

        severity_counts = self.df['cvss_severity'].value_counts()
        total = len(self.df)

        percentages = {
            severity: (count / total * 100)
            for severity, count in severity_counts.items()
        }

        return percentages

    def get_top_entities(self, entity_type: str = 'vendors', top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Get most frequently mentioned entities.

        Args:
            entity_type: 'vendors', 'products', or 'vuln_types'
            top_n: Number of top items to return

        Returns:
            List of tuples: [('Microsoft', 45), ('Apache', 32), ...]
        """
        if self.df is None or len(self.df) == 0:
            return []

        # Map entity type to column name
        column_map = {
            'vendors': 'vendors',
            'products': 'products',
            'vuln_types': 'vuln_types'
        }

        column = column_map.get(entity_type)
        if not column or column not in self.df.columns:
            return []

        # Flatten all entities from lists
        all_entities = []
        for entities in self.df[column]:
            if isinstance(entities, list):
                all_entities.extend(entities)
            elif isinstance(entities, str) and entities:
                all_entities.append(entities)

        # Count occurrences
        entity_counts = Counter(all_entities)

        return entity_counts.most_common(top_n)

    def calculate_cvss_percentiles(self) -> Dict[str, float]:
        """
        Calculate CVSS score percentiles.

        Returns:
            Dictionary like {'p10': 3.2, 'p25': 5.1, 'p50': 7.2, 'p75': 8.5, 'p90': 9.1, 'p95': 9.6}
        """
        if self.df is None or 'cvss_score' not in self.df.columns:
            return {}

        cvss_scores = self.df['cvss_score'].dropna()
        cvss_scores = cvss_scores[cvss_scores > 0]

        if len(cvss_scores) == 0:
            return {}

        percentiles = {
            'p10': float(cvss_scores.quantile(0.10)),
            'p25': float(cvss_scores.quantile(0.25)),
            'p50': float(cvss_scores.quantile(0.50)),
            'p75': float(cvss_scores.quantile(0.75)),
            'p90': float(cvss_scores.quantile(0.90)),
            'p95': float(cvss_scores.quantile(0.95))
        }

        return percentiles

    def calculate_vulnerability_density(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate vulnerability density metrics (CVEs per day).

        Returns:
            Dictionary with:
            - by_vendor: {'Microsoft': 0.42, 'Apache': 0.38, ...}
            - by_product: {'Windows': 0.15, 'Tomcat': 0.12, ...}
            - by_severity: {'CRITICAL': 0.08, 'HIGH': 0.25, ...}
        """
        if self.df is None or len(self.df) == 0:
            return {'by_vendor': {}, 'by_product': {}, 'by_severity': {}}

        # Calculate total days in dataset
        if 'published_date' not in self.df.columns:
            return {'by_vendor': {}, 'by_product': {}, 'by_severity': {}}

        start_date = self.df['published_date'].min()
        end_date = self.df['published_date'].max()
        total_days = (end_date - start_date).days

        if total_days == 0:
            total_days = 1  # Avoid division by zero

        # Density by vendor
        vendor_density = {}
        if 'vendors' in self.df.columns:
            top_vendors = self.get_top_entities('vendors', 20)
            for vendor, count in top_vendors:
                vendor_density[vendor] = count / total_days

        # Density by product
        product_density = {}
        if 'products' in self.df.columns:
            top_products = self.get_top_entities('products', 20)
            for product, count in top_products:
                product_density[product] = count / total_days

        # Density by severity
        severity_density = {}
        if 'cvss_severity' in self.df.columns:
            severity_counts = self.df['cvss_severity'].value_counts()
            for severity, count in severity_counts.items():
                severity_density[severity] = count / total_days

        return {
            'by_vendor': vendor_density,
            'by_product': product_density,
            'by_severity': severity_density
        }


# Example usage
if __name__ == "__main__":
    # Test with sample data
    sample_data = {
        'cve_id': ['CVE-2024-001', 'CVE-2024-002', 'CVE-2024-003'],
        'cvss_score': [7.5, 9.8, 5.3],
        'cvss_severity': ['HIGH', 'CRITICAL', 'MEDIUM'],
        'published_date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
        'vendors': [['Microsoft'], ['Apache'], ['Google']],
        'products': [['Windows'], ['Tomcat'], ['Chrome']],
        'attack_vector': ['NETWORK', 'NETWORK', 'LOCAL'],
        'attack_complexity': ['LOW', 'LOW', 'HIGH']
    }

    df = pd.DataFrame(sample_data)
    calc = StatisticsCalculator(df=df)

    print("Summary Stats:")
    print(calc.get_summary_stats())

    print("\nSeverity Percentages:")
    print(calc.calculate_severity_percentages())

    print("\nTop Vendors:")
    print(calc.get_top_entities('vendors', 5))
