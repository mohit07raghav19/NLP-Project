"""
Analysis Package

Analytics and visualization utilities for CVE data.
"""

from .statistics import StatisticsCalculator
from .trends import TrendAnalyzer
from .impact import ImpactAnalyzer

__version__ = "0.1.0"
__all__ = ["TrendAnalyzer", "ImpactAnalyzer", "StatisticsCalculator"]
