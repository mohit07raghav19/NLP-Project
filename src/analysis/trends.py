"""
Trend Analysis Module

Analyze temporal trends and patterns in CVE data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from scipy import stats
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """Analyze temporal trends in CVE data."""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize with CVE data.

        Args:
            df: DataFrame with columns: published_date, cvss_severity, cvss_score, vendors, etc.
        """
        self.df = df.copy()

        # Ensure published_date is datetime
        if 'published_date' in self.df.columns:
            self.df['published_date'] = pd.to_datetime(self.df['published_date'])

    def calculate_growth_rate(self, period: str = 'daily') -> Dict[str, Any]:
        """
        Calculate CVE growth rate over time.

        Args:
            period: 'daily', 'weekly', or 'monthly'

        Returns:
            Dictionary with:
            - average_growth_rate: float (percentage)
            - growth_by_period: pd.Series (indexed by date)
            - trend_direction: str ('increasing', 'decreasing', 'stable')
            - compound_growth_rate: float (overall CAGR)
        """
        if self.df is None or len(self.df) == 0:
            return {
                'average_growth_rate': 0.0,
                'growth_by_period': pd.Series(),
                'trend_direction': 'stable',
                'compound_growth_rate': 0.0
            }

        # Group by period
        if period == 'daily':
            grouped = self.df.groupby(self.df['published_date'].dt.date).size()
        elif period == 'weekly':
            grouped = self.df.groupby(self.df['published_date'].dt.to_period('W')).size()
        elif period == 'monthly':
            grouped = self.df.groupby(self.df['published_date'].dt.to_period('M')).size()
        else:
            grouped = self.df.groupby(self.df['published_date'].dt.date).size()

        # Calculate period-over-period growth rate
        growth_rates = []
        for i in range(1, len(grouped)):
            prev = grouped.iloc[i-1]
            curr = grouped.iloc[i]
            if prev > 0:
                growth = ((curr - prev) / prev) * 100
                growth_rates.append(growth)

        # Average growth rate
        avg_growth = np.mean(growth_rates) if growth_rates else 0.0

        # Determine trend direction using linear regression
        if len(grouped) > 1:
            x = np.arange(len(grouped))
            y = grouped.values
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

            if slope > 0.1:
                trend_direction = 'increasing'
            elif slope < -0.1:
                trend_direction = 'decreasing'
            else:
                trend_direction = 'stable'
        else:
            trend_direction = 'stable'

        # Compound growth rate (CAGR)
        if len(grouped) > 1 and grouped.iloc[0] > 0:
            first_val = grouped.iloc[0]
            last_val = grouped.iloc[-1]
            n_periods = len(grouped) - 1
            cagr = ((last_val / first_val) ** (1 / n_periods) - 1) * 100
        else:
            cagr = 0.0

        return {
            'average_growth_rate': float(avg_growth),
            'growth_by_period': grouped,
            'trend_direction': trend_direction,
            'compound_growth_rate': float(cagr)
        }

    def detect_vulnerability_spikes(self, threshold_std: float = 2.0) -> List[Dict]:
        """
        Detect anomalous spikes in CVE publications.

        Args:
            threshold_std: Number of standard deviations for spike detection

        Returns:
            List of spike events with date, count, expected, zscore, severity_breakdown
        """
        if self.df is None or len(self.df) == 0:
            return []

        # Daily counts
        daily_counts = self.df.groupby(self.df['published_date'].dt.date).size()

        # Calculate rolling statistics (7-day window)
        rolling_mean = daily_counts.rolling(window=7, center=True).mean()
        rolling_std = daily_counts.rolling(window=7, center=True).std()

        # Calculate z-scores
        z_scores = (daily_counts - rolling_mean) / rolling_std

        # Identify spikes
        spikes = []
        for date, count in daily_counts.items():
            if pd.notna(z_scores[date]) and abs(z_scores[date]) > threshold_std:
                # Get severity breakdown for this date
                date_cves = self.df[self.df['published_date'].dt.date == date]
                severity_breakdown = {}

                if 'cvss_severity' in date_cves.columns:
                    severity_breakdown = date_cves['cvss_severity'].value_counts().to_dict()

                spikes.append({
                    'date': str(date),
                    'count': int(count),
                    'expected': float(rolling_mean[date]) if pd.notna(rolling_mean[date]) else 0.0,
                    'zscore': float(z_scores[date]),
                    'severity_breakdown': severity_breakdown
                })

        # Sort by z-score (highest first)
        spikes.sort(key=lambda x: abs(x['zscore']), reverse=True)

        return spikes

    def analyze_severity_trends(self) -> Dict[str, Any]:
        """
        Analyze how vulnerability severity changes over time.

        Returns:
            Dictionary with:
            - severity_over_time: pd.DataFrame (columns: date, CRITICAL, HIGH, MEDIUM, LOW)
            - severity_percentage_trends: pd.DataFrame (percentage distribution)
            - average_cvss_trend: pd.Series (average CVSS score by week)
            - critical_percentage_change: float (% change in critical vulns)
            - trend_interpretation: str (insight text)
        """
        if self.df is None or len(self.df) == 0:
            return {
                'severity_over_time': pd.DataFrame(),
                'severity_percentage_trends': pd.DataFrame(),
                'average_cvss_trend': pd.Series(),
                'critical_percentage_change': 0.0,
                'trend_interpretation': 'Insufficient data for trend analysis'
            }

        # Group by week
        self.df['week'] = self.df['published_date'].dt.to_period('W')

        # Count severities per week
        severity_counts = self.df.groupby(['week', 'cvss_severity']).size().unstack(fill_value=0)

        # Calculate percentage distribution
        severity_percentages = severity_counts.div(severity_counts.sum(axis=1), axis=0) * 100

        # Average CVSS score per week
        avg_cvss_trend = self.df.groupby('week')['cvss_score'].mean()

        # Calculate change in critical percentage
        if 'CRITICAL' in severity_percentages.columns and len(severity_percentages) > 1:
            first_critical_pct = severity_percentages['CRITICAL'].iloc[0]
            last_critical_pct = severity_percentages['CRITICAL'].iloc[-1]
            critical_pct_change = ((last_critical_pct - first_critical_pct) / first_critical_pct * 100) if first_critical_pct > 0 else 0.0
        else:
            critical_pct_change = 0.0

        # Generate interpretation
        if critical_pct_change > 10:
            interpretation = f"Vulnerabilities are getting MORE SEVERE (critical vulns increased {critical_pct_change:.1f}%)"
        elif critical_pct_change < -10:
            interpretation = f"Vulnerabilities are getting LESS SEVERE (critical vulns decreased {abs(critical_pct_change):.1f}%)"
        else:
            interpretation = "Vulnerability severity is STABLE over time"

        # Convert week back to string for DataFrame
        severity_counts.index = severity_counts.index.astype(str)
        severity_percentages.index = severity_percentages.index.astype(str)
        avg_cvss_trend.index = avg_cvss_trend.index.astype(str)

        return {
            'severity_over_time': severity_counts,
            'severity_percentage_trends': severity_percentages,
            'average_cvss_trend': avg_cvss_trend,
            'critical_percentage_change': float(critical_pct_change),
            'trend_interpretation': interpretation
        }

    def analyze_vendor_trends(self, top_n: int = 10) -> Dict[str, Any]:
        """
        Analyze trends for top vendors over time.

        Args:
            top_n: Number of top vendors to analyze

        Returns:
            Dictionary with:
            - vendor_timeline: pd.DataFrame (columns: date, vendor1, vendor2, ...)
            - vendor_growth_rates: pd.DataFrame (growth rate per vendor)
            - emerging_vendors: List[str] (vendors with increasing mentions)
            - declining_vendors: List[str] (vendors with decreasing mentions)
        """
        if self.df is None or len(self.df) == 0 or 'vendors' not in self.df.columns:
            return {
                'vendor_timeline': pd.DataFrame(),
                'vendor_growth_rates': pd.DataFrame(),
                'emerging_vendors': [],
                'declining_vendors': []
            }

        # Explode vendors (one row per vendor)
        df_exploded = self.df.explode('vendors')
        df_exploded = df_exploded[df_exploded['vendors'].notna()]

        # Get top N vendors overall
        top_vendors = df_exploded['vendors'].value_counts().head(top_n).index.tolist()

        # Filter to only top vendors
        df_top = df_exploded[df_exploded['vendors'].isin(top_vendors)]

        # Group by week and vendor
        df_top['week'] = df_top['published_date'].dt.to_period('W')
        vendor_timeline = df_top.groupby(['week', 'vendors']).size().unstack(fill_value=0)

        # Calculate growth rates using linear regression
        vendor_growth_rates = {}
        emerging = []
        declining = []

        for vendor in vendor_timeline.columns:
            counts = vendor_timeline[vendor].values
            if len(counts) > 1:
                x = np.arange(len(counts))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, counts)
                vendor_growth_rates[vendor] = slope

                if slope > 0.5:  # Threshold for emerging
                    emerging.append(vendor)
                elif slope < -0.5:  # Threshold for declining
                    declining.append(vendor)

        # Convert to DataFrame
        growth_df = pd.DataFrame.from_dict(vendor_growth_rates, orient='index', columns=['growth_rate'])
        growth_df = growth_df.sort_values('growth_rate', ascending=False)

        # Convert week index to string
        vendor_timeline.index = vendor_timeline.index.astype(str)

        return {
            'vendor_timeline': vendor_timeline,
            'vendor_growth_rates': growth_df,
            'emerging_vendors': emerging,
            'declining_vendors': declining
        }

    def detect_temporal_patterns(self) -> Dict[str, Any]:
        """
        Detect patterns in CVE publication timing.

        Returns:
            Dictionary with:
            - day_of_week_distribution: Dict[str, int]
            - monthly_seasonality: Dict[str, float]
            - busiest_day: str
            - quietest_day: str
            - weekly_pattern: str
        """
        if self.df is None or len(self.df) == 0:
            return {
                'day_of_week_distribution': {},
                'monthly_seasonality': {},
                'busiest_day': 'Unknown',
                'quietest_day': 'Unknown',
                'weekly_pattern': 'Unknown'
            }

        # Day of week distribution
        day_of_week = self.df['published_date'].dt.day_name()
        day_counts = day_of_week.value_counts().to_dict()

        # Find busiest and quietest days
        if day_counts:
            busiest = max(day_counts, key=day_counts.get)
            quietest = min(day_counts, key=day_counts.get)
        else:
            busiest = quietest = 'Unknown'

        # Monthly seasonality (normalize by number of occurrences)
        month_counts = self.df['published_date'].dt.month_name().value_counts()
        total_avg = month_counts.mean()
        monthly_seasonality = {month: count / total_avg for month, count in month_counts.items()}

        # Weekly pattern (weekday vs weekend)
        weekday_count = sum([day_counts.get(day, 0) for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']])
        weekend_count = sum([day_counts.get(day, 0) for day in ['Saturday', 'Sunday']])

        if weekday_count > weekend_count * 2:
            weekly_pattern = 'weekday_heavy'
        elif weekend_count > weekday_count:
            weekly_pattern = 'weekend_heavy'
        else:
            weekly_pattern = 'uniform'

        return {
            'day_of_week_distribution': day_counts,
            'monthly_seasonality': monthly_seasonality,
            'busiest_day': busiest,
            'quietest_day': quietest,
            'weekly_pattern': weekly_pattern
        }


# Example usage
if __name__ == "__main__":
    # Test with sample data
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    sample_data = {
        'cve_id': [f'CVE-2024-{i:03d}' for i in range(30)],
        'published_date': dates,
        'cvss_severity': np.random.choice(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'], 30),
        'cvss_score': np.random.uniform(3, 10, 30),
        'vendors': [[np.random.choice(['Microsoft', 'Apache', 'Google'])] for _ in range(30)]
    }

    df = pd.DataFrame(sample_data)
    analyzer = TrendAnalyzer(df=df)

    print("Growth Rate Analysis:")
    growth = analyzer.calculate_growth_rate('daily')
    print(f"  Average growth: {growth['average_growth_rate']:.2f}%")
    print(f"  Trend: {growth['trend_direction']}")

    print("\nSpike Detection:")
    spikes = analyzer.detect_vulnerability_spikes(threshold_std=1.5)
    print(f"  Found {len(spikes)} spikes")

    print("\nSeverity Trends:")
    severity = analyzer.analyze_severity_trends()
    print(f"  {severity['trend_interpretation']}")
