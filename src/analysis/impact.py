"""
Vulnerability Impact Analysis Module

Analyze vulnerability impact and calculate risk scores.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)


class ImpactAnalyzer:
    """Analyze vulnerability impact and risk."""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize with CVE data.

        Args:
            df: DataFrame with CVE information
        """
        self.df = df.copy()

        # Severity weight mapping for risk scoring
        self.severity_weights = {
            'CRITICAL': 10,
            'HIGH': 7,
            'MEDIUM': 4,
            'LOW': 1,
            'UNKNOWN': 0
        }

    def calculate_vendor_risk_scores(self) -> pd.DataFrame:
        """
        Calculate risk scores for vendors based on CVE severity.

        Returns:
            DataFrame with columns:
            - vendor: str
            - total_cves: int
            - critical_count: int
            - high_count: int
            - medium_count: int
            - low_count: int
            - risk_score: float (CRITICAL*10 + HIGH*7 + MEDIUM*4 + LOW*1)
            - avg_cvss: float
            - risk_level: str ('Very High', 'High', 'Medium', 'Low')
        """
        if self.df is None or len(self.df) == 0 or 'vendors' not in self.df.columns:
            return pd.DataFrame()

        # Explode vendors (one row per vendor-CVE pair)
        df_exploded = self.df.explode('vendors')
        df_exploded = df_exploded[df_exploded['vendors'].notna()]

        # Group by vendor and calculate metrics
        vendor_data = []

        for vendor in df_exploded['vendors'].unique():
            vendor_cves = df_exploded[df_exploded['vendors'] == vendor]

            # Count by severity
            severity_counts = vendor_cves['cvss_severity'].value_counts().to_dict()
            critical_count = severity_counts.get('CRITICAL', 0)
            high_count = severity_counts.get('HIGH', 0)
            medium_count = severity_counts.get('MEDIUM', 0)
            low_count = severity_counts.get('LOW', 0)

            # Calculate risk score
            risk_score = (
                critical_count * self.severity_weights['CRITICAL'] +
                high_count * self.severity_weights['HIGH'] +
                medium_count * self.severity_weights['MEDIUM'] +
                low_count * self.severity_weights['LOW']
            )

            # Average CVSS score
            avg_cvss = vendor_cves['cvss_score'].mean() if 'cvss_score' in vendor_cves.columns else 0.0

            # Total CVEs
            total_cves = len(vendor_cves)

            vendor_data.append({
                'vendor': vendor,
                'total_cves': total_cves,
                'critical_count': critical_count,
                'high_count': high_count,
                'medium_count': medium_count,
                'low_count': low_count,
                'risk_score': risk_score,
                'avg_cvss': avg_cvss
            })

        # Create DataFrame
        df_vendors = pd.DataFrame(vendor_data)

        # Assign risk levels based on percentiles
        if len(df_vendors) > 0:
            risk_scores = df_vendors['risk_score']
            p75 = risk_scores.quantile(0.75)
            p50 = risk_scores.quantile(0.50)
            p25 = risk_scores.quantile(0.25)

            def assign_risk_level(score):
                if score >= p75:
                    return 'Very High'
                elif score >= p50:
                    return 'High'
                elif score >= p25:
                    return 'Medium'
                else:
                    return 'Low'

            df_vendors['risk_level'] = df_vendors['risk_score'].apply(assign_risk_level)

        # Sort by risk score (highest first)
        df_vendors = df_vendors.sort_values('risk_score', ascending=False)

        return df_vendors

    def get_highest_risk_vendors(self, top_n: int = 20) -> List[Dict]:
        """
        Get vendors with highest risk scores.

        Args:
            top_n: Number of vendors to return

        Returns:
            List of dictionaries with vendor risk information
        """
        vendor_risks = self.calculate_vendor_risk_scores()

        if vendor_risks.empty:
            return []

        # Get top N vendors
        top_vendors = vendor_risks.head(top_n)

        # Calculate critical percentage
        top_vendors['critical_percentage'] = (
            top_vendors['critical_count'] / top_vendors['total_cves'] * 100
        ).round(1)

        return top_vendors.to_dict('records')

    def analyze_attack_surface(self) -> Dict[str, Any]:
        """
        Analyze attack surface characteristics.

        Returns:
            Dictionary with:
            - attack_vector_distribution: {'NETWORK': 456, 'LOCAL': 123, ...}
            - attack_vector_severity: {'NETWORK': 7.8, 'LOCAL': 6.2, ...}
            - network_exploitable_percentage: float
            - high_risk_attack_surface: {count, percentage, top_vendors}
        """
        if self.df is None or len(self.df) == 0:
            return {
                'attack_vector_distribution': {},
                'attack_vector_severity': {},
                'network_exploitable_percentage': 0.0,
                'high_risk_attack_surface': {'count': 0, 'percentage': 0.0, 'top_vendors': []}
            }

        # Attack vector distribution
        attack_vector_dist = {}
        if 'attack_vector' in self.df.columns:
            df_with_vector = self.df[self.df['attack_vector'] != '']
            attack_vector_dist = df_with_vector['attack_vector'].value_counts().to_dict()

        # Average CVSS by attack vector
        attack_vector_severity = {}
        if 'attack_vector' in self.df.columns and 'cvss_score' in self.df.columns:
            for vector in attack_vector_dist.keys():
                vector_cves = self.df[self.df['attack_vector'] == vector]
                avg_cvss = vector_cves['cvss_score'].mean()
                attack_vector_severity[vector] = float(avg_cvss)

        # Network exploitable percentage
        total_with_vector = len(self.df[self.df['attack_vector'] != ''])
        network_count = attack_vector_dist.get('NETWORK', 0)
        network_pct = (network_count / total_with_vector * 100) if total_with_vector > 0 else 0.0

        # High-risk attack surface: NETWORK + LOW complexity + CRITICAL/HIGH severity
        high_risk_cves = self.df[
            (self.df['attack_vector'] == 'NETWORK') &
            (self.df['attack_complexity'] == 'LOW') &
            (self.df['cvss_severity'].isin(['CRITICAL', 'HIGH']))
        ]

        high_risk_count = len(high_risk_cves)
        high_risk_pct = (high_risk_count / len(self.df) * 100) if len(self.df) > 0 else 0.0

        # Top vendors in high-risk category
        top_vendors = []
        if 'vendors' in high_risk_cves.columns and len(high_risk_cves) > 0:
            all_vendors = []
            for vendors in high_risk_cves['vendors']:
                if isinstance(vendors, list):
                    all_vendors.extend(vendors)

            if all_vendors:
                vendor_counts = Counter(all_vendors)
                top_vendors = [vendor for vendor, count in vendor_counts.most_common(5)]

        return {
            'attack_vector_distribution': attack_vector_dist,
            'attack_vector_severity': attack_vector_severity,
            'network_exploitable_percentage': float(network_pct),
            'high_risk_attack_surface': {
                'count': int(high_risk_count),
                'percentage': float(high_risk_pct),
                'top_vendors': top_vendors
            }
        }

    def analyze_product_vulnerability_density(self) -> pd.DataFrame:
        """
        Analyze vulnerability density for products.

        Returns:
            DataFrame with columns:
            - product: str
            - vulnerability_count: int
            - avg_severity_score: float
            - critical_percentage: float
            - most_common_attack_vector: str
            - impact_score: float
        """
        if self.df is None or len(self.df) == 0 or 'products' not in self.df.columns:
            return pd.DataFrame()

        # Explode products
        df_exploded = self.df.explode('products')
        df_exploded = df_exploded[df_exploded['products'].notna()]

        # Group by product
        product_data = []

        for product in df_exploded['products'].unique():
            product_cves = df_exploded[df_exploded['products'] == product]

            vuln_count = len(product_cves)
            avg_cvss = product_cves['cvss_score'].mean() if 'cvss_score' in product_cves.columns else 0.0

            # Critical percentage
            if 'cvss_severity' in product_cves.columns:
                critical_count = (product_cves['cvss_severity'] == 'CRITICAL').sum()
                critical_pct = (critical_count / vuln_count * 100) if vuln_count > 0 else 0.0
            else:
                critical_pct = 0.0

            # Most common attack vector
            if 'attack_vector' in product_cves.columns:
                vector_counts = product_cves[product_cves['attack_vector'] != '']['attack_vector'].value_counts()
                most_common_vector = vector_counts.index[0] if len(vector_counts) > 0 else 'Unknown'
            else:
                most_common_vector = 'Unknown'

            # Impact score: (avg_cvss / 10) * vuln_count * critical_multiplier
            critical_multiplier = 1 + (critical_pct / 100)
            impact_score = (avg_cvss / 10) * vuln_count * critical_multiplier

            product_data.append({
                'product': product,
                'vulnerability_count': vuln_count,
                'avg_severity_score': avg_cvss,
                'critical_percentage': critical_pct,
                'most_common_attack_vector': most_common_vector,
                'impact_score': impact_score
            })

        # Create DataFrame and sort by impact score
        df_products = pd.DataFrame(product_data)
        df_products = df_products.sort_values('impact_score', ascending=False)

        return df_products

    def calculate_weighted_impact_metrics(self) -> Dict[str, Any]:
        """
        Calculate severity-weighted impact across dimensions.

        Returns:
            Dictionary with:
            - global_impact_score: float
            - impact_by_vendor: Dict[str, float]
            - impact_by_product: Dict[str, float]
            - impact_by_attack_vector: Dict[str, float]
            - daily_impact_trend: pd.Series
            - highest_impact_day: {date, score, reason}
        """
        if self.df is None or len(self.df) == 0:
            return {
                'global_impact_score': 0.0,
                'impact_by_vendor': {},
                'impact_by_product': {},
                'impact_by_attack_vector': {},
                'daily_impact_trend': pd.Series(),
                'highest_impact_day': {'date': None, 'score': 0.0, 'reason': 'No data'}
            }

        # Calculate weighted score for each CVE
        self.df['weighted_score'] = self.df.apply(
            lambda row: self.severity_weights.get(row['cvss_severity'], 0) * row.get('cvss_score', 0),
            axis=1
        )

        # Global impact score
        global_impact = self.df['weighted_score'].sum()

        # Impact by vendor
        impact_by_vendor = {}
        if 'vendors' in self.df.columns:
            df_exploded = self.df.explode('vendors')
            impact_by_vendor = df_exploded.groupby('vendors')['weighted_score'].sum().to_dict()

        # Impact by product
        impact_by_product = {}
        if 'products' in self.df.columns:
            df_exploded = self.df.explode('products')
            impact_by_product = df_exploded.groupby('products')['weighted_score'].sum().to_dict()

        # Impact by attack vector
        impact_by_vector = {}
        if 'attack_vector' in self.df.columns:
            df_with_vector = self.df[self.df['attack_vector'] != '']
            impact_by_vector = df_with_vector.groupby('attack_vector')['weighted_score'].sum().to_dict()

        # Daily impact trend
        if 'published_date' in self.df.columns:
            daily_impact = self.df.groupby(self.df['published_date'].dt.date)['weighted_score'].sum()

            # Find highest impact day
            if len(daily_impact) > 0:
                max_date = daily_impact.idxmax()
                max_score = daily_impact.max()

                # Determine reason
                max_day_cves = self.df[self.df['published_date'].dt.date == max_date]
                critical_count = (max_day_cves['cvss_severity'] == 'CRITICAL').sum()
                reason = f"{len(max_day_cves)} CVEs published, including {critical_count} critical"
            else:
                max_date = None
                max_score = 0.0
                reason = 'No data'
        else:
            daily_impact = pd.Series()
            max_date = None
            max_score = 0.0
            reason = 'No date data'

        return {
            'global_impact_score': float(global_impact),
            'impact_by_vendor': impact_by_vendor,
            'impact_by_product': impact_by_product,
            'impact_by_attack_vector': impact_by_vector,
            'daily_impact_trend': daily_impact,
            'highest_impact_day': {
                'date': str(max_date) if max_date else None,
                'score': float(max_score),
                'reason': reason
            }
        }

    def extract_impact_patterns_from_text(self) -> Dict[str, Any]:
        """
        Extract impact-related patterns from CVE descriptions using NLP entities.

        Returns:
            Dictionary with:
            - common_vulnerability_themes: List[Tuple[str, int]]
            - high_impact_keywords: List[str]
            - exploitability_indicators: {type: count}
            - vendor_vulnerability_themes: Dict[vendor, List[themes]]
        """
        if self.df is None or len(self.df) == 0:
            return {
                'common_vulnerability_themes': [],
                'high_impact_keywords': [],
                'exploitability_indicators': {},
                'vendor_vulnerability_themes': {}
            }

        # Extract vulnerability types from vuln_types column
        all_vuln_types = []
        if 'vuln_types' in self.df.columns:
            for vuln_types in self.df['vuln_types']:
                if isinstance(vuln_types, list):
                    all_vuln_types.extend(vuln_types)

        # Count vulnerability themes
        vuln_type_counts = Counter(all_vuln_types)
        common_themes = vuln_type_counts.most_common(15)

        # Exploitability indicators (pattern matching in vulnerability types)
        exploitability_indicators = {
            'remote_code_execution_count': sum(1 for v in all_vuln_types if 'rce' in v.lower() or 'remote code execution' in v.lower() or 'code execution' in v.lower()),
            'privilege_escalation_count': sum(1 for v in all_vuln_types if 'privilege' in v.lower() or 'escalation' in v.lower()),
            'authentication_bypass_count': sum(1 for v in all_vuln_types if 'authentication' in v.lower() or 'bypass' in v.lower()),
            'information_disclosure_count': sum(1 for v in all_vuln_types if 'information' in v.lower() or 'disclosure' in v.lower()),
            'sql_injection_count': sum(1 for v in all_vuln_types if 'sql' in v.lower() or 'injection' in v.lower()),
            'cross_site_scripting_count': sum(1 for v in all_vuln_types if 'xss' in v.lower() or 'cross-site' in v.lower() or 'cross site' in v.lower())
        }

        # High-impact keywords (from critical CVEs)
        high_impact_keywords = []
        if 'cvss_severity' in self.df.columns and 'vuln_types' in self.df.columns:
            critical_cves = self.df[self.df['cvss_severity'] == 'CRITICAL']
            critical_vuln_types = []
            for vuln_types in critical_cves['vuln_types']:
                if isinstance(vuln_types, list):
                    critical_vuln_types.extend(vuln_types)

            if critical_vuln_types:
                critical_counts = Counter(critical_vuln_types)
                high_impact_keywords = [vtype for vtype, count in critical_counts.most_common(10)]

        # Vendor vulnerability themes
        vendor_themes = {}
        if 'vendors' in self.df.columns and 'vuln_types' in self.df.columns:
            df_exploded = self.df.explode('vendors')
            df_exploded = df_exploded[df_exploded['vendors'].notna()]

            for vendor in df_exploded['vendors'].unique():
                vendor_cves = df_exploded[df_exploded['vendors'] == vendor]
                vendor_vuln_types = []

                for vuln_types in vendor_cves['vuln_types']:
                    if isinstance(vuln_types, list):
                        vendor_vuln_types.extend(vuln_types)

                if vendor_vuln_types:
                    vendor_counts = Counter(vendor_vuln_types)
                    top_themes = [vtype for vtype, count in vendor_counts.most_common(5)]
                    vendor_themes[vendor] = top_themes

        return {
            'common_vulnerability_themes': common_themes,
            'high_impact_keywords': high_impact_keywords,
            'exploitability_indicators': exploitability_indicators,
            'vendor_vulnerability_themes': vendor_themes
        }


# Example usage
if __name__ == "__main__":
    # Test with sample data
    sample_data = {
        'cve_id': ['CVE-2024-001', 'CVE-2024-002', 'CVE-2024-003', 'CVE-2024-004'],
        'cvss_score': [7.5, 9.8, 5.3, 8.1],
        'cvss_severity': ['HIGH', 'CRITICAL', 'MEDIUM', 'HIGH'],
        'published_date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04']),
        'vendors': [['Microsoft'], ['Apache'], ['Google'], ['Microsoft']],
        'products': [['Windows'], ['Tomcat'], ['Chrome'], ['Office']],
        'vuln_types': [['SQL Injection'], ['Remote Code Execution'], ['XSS'], ['Privilege Escalation']],
        'attack_vector': ['NETWORK', 'NETWORK', 'LOCAL', 'NETWORK'],
        'attack_complexity': ['LOW', 'LOW', 'HIGH', 'LOW']
    }

    df = pd.DataFrame(sample_data)
    analyzer = ImpactAnalyzer(df=df)

    print("Vendor Risk Scores:")
    print(analyzer.calculate_vendor_risk_scores())

    print("\nAttack Surface Analysis:")
    attack_surface = analyzer.analyze_attack_surface()
    print(f"  Network exploitable: {attack_surface['network_exploitable_percentage']:.1f}%")
    print(f"  High-risk CVEs: {attack_surface['high_risk_attack_surface']['count']}")

    print("\nImpact Patterns:")
    patterns = analyzer.extract_impact_patterns_from_text()
    print(f"  Common themes: {patterns['common_vulnerability_themes']}")
