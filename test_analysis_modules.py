"""
Test script for analysis modules

Test the new analysis modules with existing CVE data.
"""
import sys
import json
sys.path.insert(0, 'src')

import pandas as pd
from analysis.statistics import StatisticsCalculator
from analysis.trends import TrendAnalyzer
from analysis.impact import ImpactAnalyzer

print("="*60)
print("TESTING ADVANCED ANALYSIS MODULES")
print("="*60)

# Load test data
print("\nLoading test data from data/raw/test_cves.json...")
try:
    with open('data/raw/test_cves.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    cves = data.get('vulnerabilities', [])
    print(f"Loaded {len(cves)} CVEs")
except FileNotFoundError:
    print("ERROR: Test data file not found")
    sys.exit(1)

# Extract CVE information into DataFrame (simplified)
print("\nExtracting CVE information...")
extracted_data = []

for cve_entry in cves[:100]:  # Test with first 100 for speed
    cve = cve_entry.get('cve', {})

    # Basic info
    cve_id = cve.get('id', '')
    descriptions = cve.get('descriptions', [])
    description = descriptions[0].get('value', '') if descriptions else ''
    published = cve.get('published', '')

    # CVSS
    metrics = cve.get('metrics', {})
    cvss_v31 = metrics.get('cvssMetricV31', [{}])[0] if metrics.get('cvssMetricV31') else {}
    cvss_data = cvss_v31.get('cvssData', {})

    extracted_data.append({
        'cve_id': cve_id,
        'description': description,
        'published_date': published,
        'cvss_score': cvss_data.get('baseScore', 0.0),
        'cvss_severity': cvss_data.get('baseSeverity', 'UNKNOWN'),
        'attack_vector': cvss_data.get('attackVector', ''),
        'attack_complexity': cvss_data.get('attackComplexity', ''),
        'vendors': [],  # Simplified
        'products': [],  # Simplified
        'vuln_types': []  # Simplified
    })

df = pd.DataFrame(extracted_data)
df['published_date'] = pd.to_datetime(df['published_date'])

print(f"Created DataFrame with {len(df)} CVEs")
print(f"Columns: {', '.join(df.columns)}")

# Test 1: StatisticsCalculator
print("\n" + "="*60)
print("TEST 1: StatisticsCalculator")
print("="*60)

stats_calc = StatisticsCalculator(df=df)

summary = stats_calc.get_summary_stats()
print(f"\nTotal CVEs: {summary['total_cves']}")
print(f"Date Range: {summary['date_range']['start']} to {summary['date_range']['end']} ({summary['date_range']['days']} days)")

print("\nSeverity Distribution:")
for severity, count in summary['severity_distribution'].items():
    print(f"  {severity}: {count}")

if summary['cvss_stats']:
    print("\nCVSS Statistics:")
    for stat, value in summary['cvss_stats'].items():
        print(f"  {stat}: {value:.2f}")

print("\nSeverity Percentages:")
percentages = stats_calc.calculate_severity_percentages()
for severity, pct in percentages.items():
    print(f"  {severity}: {pct:.1f}%")

print("\n[PASS] StatisticsCalculator working!")

# Test 2: TrendAnalyzer
print("\n" + "="*60)
print("TEST 2: TrendAnalyzer")
print("="*60)

trend_analyzer = TrendAnalyzer(df=df)

growth = trend_analyzer.calculate_growth_rate('daily')
print(f"\nGrowth Rate Analysis:")
print(f"  Average Daily Growth: {growth['average_growth_rate']:.2f}%")
print(f"  Trend Direction: {growth['trend_direction']}")
print(f"  Compound Growth Rate: {growth['compound_growth_rate']:.2f}%")

spikes = trend_analyzer.detect_vulnerability_spikes(threshold_std=1.5)
print(f"\nSpike Detection:")
print(f"  Found {len(spikes)} spikes (threshold: 1.5 std dev)")
if spikes:
    print(f"  Top spike: {spikes[0]['date']} with {spikes[0]['count']} CVEs (z-score: {spikes[0]['zscore']:.2f})")

severity_trends = trend_analyzer.analyze_severity_trends()
print(f"\nSeverity Trend Analysis:")
print(f"  {severity_trends['trend_interpretation']}")
print(f"  Critical % Change: {severity_trends['critical_percentage_change']:.1f}%")

print("\n[PASS] TrendAnalyzer working!")

# Test 3: ImpactAnalyzer
print("\n" + "="*60)
print("TEST 3: ImpactAnalyzer")
print("="*60)

impact_analyzer = ImpactAnalyzer(df=df)

# Note: vendor/product analysis limited by simplified data
attack_surface = impact_analyzer.analyze_attack_surface()
print(f"\nAttack Surface Analysis:")
print(f"  Attack Vector Distribution:")
for vector, count in attack_surface['attack_vector_distribution'].items():
    print(f"    {vector}: {count}")

print(f"\n  Network-Exploitable: {attack_surface['network_exploitable_percentage']:.1f}%")
print(f"  High-Risk Attack Surface:")
print(f"    Count: {attack_surface['high_risk_attack_surface']['count']} CVEs")
print(f"    Percentage: {attack_surface['high_risk_attack_surface']['percentage']:.1f}%")

weighted_impact = impact_analyzer.calculate_weighted_impact_metrics()
print(f"\nWeighted Impact Metrics:")
print(f"  Global Impact Score: {weighted_impact['global_impact_score']:.2f}")
if weighted_impact['highest_impact_day']['date']:
    print(f"  Highest Impact Day: {weighted_impact['highest_impact_day']['date']}")
    print(f"    Score: {weighted_impact['highest_impact_day']['score']:.2f}")
    print(f"    Reason: {weighted_impact['highest_impact_day']['reason']}")

print("\n[PASS] ImpactAnalyzer working!")

# Summary
print("\n" + "="*60)
print("ALL TESTS PASSED!")
print("="*60)
print("\nAnalysis modules are ready to use in the notebook!")
print("\nNext step: Update Section 6 of CVE_NLP_Pipeline.ipynb")
