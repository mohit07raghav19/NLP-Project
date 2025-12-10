# 🔐 CVE NLP Analysis System

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**Automated extraction and analysis of Common Vulnerabilities and Exposures (CVE) data using Natural Language Processing**

A comprehensive NLP project that collects, processes, and analyzes CVE data from the National Vulnerability Database (NVD), extracting structured information and providing actionable insights through advanced natural language processing techniques.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Web Dashboard](#-web-dashboard)
- [Examples](#-examples)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🎯 Core Capabilities

- **Automated Data Collection**: Fetch CVE data from NVD API with intelligent rate limiting and caching
- **Advanced NLP Processing**:
  - Named Entity Recognition (NER) using spaCy
  - Transformer-based extraction using BERT
  - Rule-based pattern matching for CVE-specific entities
- **Multi-Model Approach**: Combines statistical and neural NLP techniques
- **Structured Information Extraction**:
  - CVE IDs and references
  - Severity scores (CVSS)
  - Affected products and vendors
  - CWE classifications
  - Temporal metadata
- **Comprehensive Analysis**:
  - Temporal trend analysis
  - Severity distribution
  - Vendor vulnerability patterns
  - Topic modeling
  - Predictive insights

### 🛠️ Technical Features

- **Database Storage**: SQLite (with PostgreSQL support)
- **RESTful API**: FastAPI-based endpoints for data access
- **Web Dashboard**: Interactive UI for browsing and visualization
- **Google Colab Support**: Run entire pipeline in cloud environment
- **Caching & Rate Limiting**: Efficient API usage
- **Modular Architecture**: Easy to extend and customize

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CVE NLP SYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐   │
│  │ Data Sources │─────>│ Collection   │─────>│  Cache   │   │
│  │  - NVD API   │      │   Module     │      │          │   │
│  │  - Scraping  │      └──────────────┘      └──────────┘   │
│  └──────────────┘              │                            │
│                                ▼                            │
│                      ┌──────────────────┐                   │
│                      │  Preprocessing   │                   │
│                      │  - Clean text    │                   │
│                      │  - Tokenize      │                   │
│                      │  - Normalize     │                   │
│                      └──────────────────┘                   │
│                                 │                           │
│                                 ▼                           │
│                      ┌──────────────────┐                   │
│                      │  NLP Pipeline    │                   │
│                      │  - spaCy NER     │                   │
│                      │  - Transformers  │                   │
│                      │  - Rule Engine   │                   │
│                      └──────────────────┘                   │
│                                 │                           │
│                                 ▼                           │
│                      ┌──────────────────┐                   │
│                      │  Database        │                   │
│                      │  - SQLite/       │                   │
│                      │    PostgreSQL    │                   │
│                      └──────────────────┘                   │
│                                 │                           │
│                    ┌────────────┴────────────┐              │
│                    ▼                         ▼              │
│          ┌──────────────┐          ┌──────────────┐         │
│          │  FastAPI     │          │  Analysis    │         │
│          │  REST API    │          │  Engine      │         │
│          └──────────────┘          └──────────────┘         │
│                    │                         │              │
│                    ▼                         ▼              │
│          ┌──────────────┐          ┌──────────────┐         │
│          │  Web UI      │          │ Insights &   │         │
│          │  Dashboard   │          │ Visualize    │         │
│          └──────────────┘          └──────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git
- (Optional) CUDA for GPU acceleration

### Step 1: Clone Repository

```bash
git clone https://github.com/mohit07raghav19/NLP-Project.git
cd NLP-Project
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Download NLP Models

```bash
# Download spaCy model
python -m spacy download en_core_web_sm

# For better accuracy (optional, ~800MB)
python -m spacy download en_core_web_lg
```

### Step 5: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your NVD API key (optional but recommended)
# Get free key at: https://nvd.nist.gov/developers/request-an-api-key
```

### Step 6: Initialize Database

```bash
python scripts/setup_database.py
```

---

## ⚡ Quick Start

### Option 1: Run in Google Colab (Recommended for beginners)

1. Open `notebooks/CVE_NLP_Pipeline.ipynb` in Google Colab
2. Run all cells sequentially
3. No local installation needed!

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mohit07raghav19/NLP-Project/blob/main/notebooks/CVE_NLP_Pipeline.ipynb)

### Option 2: Run Locally

```bash
# 1. Collect CVE data
python scripts/run_pipeline.py --step collection --limit 1000

# 2. Process with NLP
python scripts/run_pipeline.py --step nlp

# 3. Generate analysis
python scripts/run_pipeline.py --step analysis

# Or run complete pipeline
python scripts/run_pipeline.py --all
```

### Option 3: Use Jupyter Notebook

```bash
jupyter notebook notebooks/CVE_NLP_Pipeline.ipynb
```

### Option 4: Start Web Interface

```bash
# Start API server
uvicorn api.main:app --reload

# Open browser at http://localhost:8000
# API docs at http://localhost:8000/docs
```

---

## 📖 Usage

### Data Collection

```python
from src.data_collection.nvd_client import NVDClient

# Initialize client
client = NVDClient(api_key="your_key_here")  # or None for no key

# Fetch recent CVEs
cves = client.fetch_cves(
    start_date="2024-01-01",
    end_date="2024-12-31",
    results_per_page=2000
)

# Save to file
client.save_to_json(cves, "data/raw/cves_2024.json")
```

### NLP Processing

```python
from src.nlp.ner_extractor import NERExtractor
from src.nlp.transformer import TransformerExtractor

# Initialize extractors
ner = NERExtractor(model="en_core_web_sm")
transformer = TransformerExtractor(model="bert-base-uncased")

# Extract entities from CVE description
text = "CVE-2024-1234 affects Apache Tomcat versions 9.0.0 to 9.0.70..."

entities = ner.extract_entities(text)
# Output: {'ORG': ['Apache'], 'PRODUCT': ['Tomcat'], 'VERSION': ['9.0.0', '9.0.70']}

# Use transformer for classification
severity = transformer.classify_severity(text)
# Output: {'label': 'HIGH', 'score': 0.89}
```

### Database Operations

```python
from src.database.crud import CVEDatabase

db = CVEDatabase("sqlite:///data/cve_database.db")

# Insert CVE
db.insert_cve({
    'cve_id': 'CVE-2024-1234',
    'description': '...',
    'severity': 'HIGH',
    'published_date': '2024-01-15'
})

# Query CVEs
results = db.query_cves(
    severity='HIGH',
    start_date='2024-01-01',
    vendor='Apache'
)
```

### Analysis

```python
from src.analysis.trends import TrendAnalyzer
from src.analysis.visualize import Visualizer

analyzer = TrendAnalyzer(db)
viz = Visualizer()

# Analyze temporal trends
trends = analyzer.get_temporal_trends(period='monthly')

# Create visualizations
viz.plot_severity_distribution(trends)
viz.plot_vendor_analysis(top_n=20)
viz.plot_cve_timeline()
```

---

## 🌐 API Documentation

### Base URL

```
http://localhost:8000
```

### Endpoints

#### Get All CVEs

```http
GET /api/v1/cves
```

**Query Parameters:**

- `limit` (int): Number of results (default: 100)
- `offset` (int): Pagination offset (default: 0)
- `severity` (str): Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)
- `start_date` (str): Filter from date (YYYY-MM-DD)
- `end_date` (str): Filter to date (YYYY-MM-DD)

**Response:**

```json
{
  "total": 1000,
  "results": [
    {
      "cve_id": "CVE-2024-1234",
      "description": "...",
      "severity": "HIGH",
      "cvss_score": 7.5,
      "published_date": "2024-01-15",
      "affected_products": ["Apache Tomcat"],
      "cwe_ids": ["CWE-79"]
    }
  ]
}
```

#### Get CVE by ID

```http
GET /api/v1/cves/{cve_id}
```

#### Get Statistics

```http
GET /api/v1/statistics
```

#### Search CVEs

```http
POST /api/v1/search
Content-Type: application/json

{
  "query": "SQL injection",
  "filters": {
    "severity": ["HIGH", "CRITICAL"],
    "vendors": ["Microsoft", "Oracle"]
  }
}
```

Full API documentation available at `/docs` (Swagger UI)

---

## 🎨 Web Dashboard

Access the interactive web dashboard at `http://localhost:8000` after starting the API server.

**Features:**

- 📊 Real-time statistics and charts
- 🔍 Advanced search and filtering
- 📈 Temporal trend visualization
- 🏢 Vendor vulnerability analysis
- 📥 Export data (JSON, CSV)

---

## 💡 Examples

### Example 1: Analyze Recent Critical Vulnerabilities

```python
from src.data_collection.nvd_client import NVDClient
from src.analysis.statistics import analyze_severity

client = NVDClient()
cves = client.fetch_cves(start_date="2024-01-01", severity="CRITICAL")

stats = analyze_severity(cves)
print(f"Critical CVEs in 2024: {len(cves)}")
print(f"Average CVSS Score: {stats['avg_cvss']:.2f}")
```

### Example 2: Extract Affected Products

```python
from src.nlp.ner_extractor import NERExtractor

extractor = NERExtractor()
description = "This vulnerability affects Microsoft Windows 10 and Windows 11..."

products = extractor.extract_products(description)
print(products)  # ['Microsoft Windows 10', 'Windows 11']
```

### Example 3: Generate Trend Report

```python
from src.analysis.trends import generate_report

report = generate_report(
    start_date="2023-01-01",
    end_date="2024-12-31",
    output_format="html"
)
# Saves interactive HTML report
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- National Vulnerability Database (NVD) for CVE data
- spaCy and HuggingFace for NLP tools
- FastAPI for the excellent web framework
- The open-source community

---

## 📞 Contact

**Mohit Raghav**

- GitHub: [@mohit07raghav19](https://github.com/mohit07raghav19)
- Project Link: [https://github.com/mohit07raghav19/NLP-Project](https://github.com/mohit07raghav19/NLP-Project)

---

## 🔗 Additional Resources

- [Setup Guide](docs/setup_guide.md)
- [API Reference](docs/api_reference.md)
- [Resources & Links](docs/resources.md)
- [Changelog](CHANGELOG.md)

---

**⭐ If you find this project useful, please consider giving it a star!**
