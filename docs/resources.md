# 📚 Resources & References

Comprehensive collection of resources, tools, APIs, datasets, and research papers for the CVE NLP Analysis System.

---

## 🔌 APIs & Data Sources

### National Vulnerability Database (NVD) API

**Primary Data Source**

- **Base URL**: `https://services.nvd.nist.gov/rest/json/cves/2.0`
- **Documentation**: https://nvd.nist.gov/developers/vulnerabilities
- **API Key Registration**: https://nvd.nist.gov/developers/request-an-api-key
- **Rate Limits**:
  - Without API key: 5 requests / 30 seconds
  - With API key: 50 requests / 30 seconds
- **Response Format**: JSON
- **Coverage**: All CVEs from 1999 to present (~250,000+ entries)

**Features:**

- Full CVE details with CVSS scores
- CWE mappings
- CPE (Common Platform Enumeration) data
- References and advisories
- Historical data access

### Alternative & Complementary Sources

#### CVE.org Official Site

- **URL**: https://www.cve.org/
- **API**: https://cveawg.mitre.org/api/
- **Use Case**: Cross-reference and validation

#### MITRE CVE List

- **URL**: https://cve.mitre.org/
- **Downloads**: https://cve.mitre.org/data/downloads/index.html
- **Format**: CSV, XML, JSON
- **Use Case**: Bulk downloads, offline processing

#### GitHub Advisory Database

- **URL**: https://github.com/advisories
- **API**: https://api.github.com/advisories
- **Use Case**: Software-specific vulnerabilities

#### OSV (Open Source Vulnerabilities)

- **URL**: https://osv.dev/
- **API**: https://api.osv.dev/
- **Use Case**: Open-source package vulnerabilities

#### Vulners

- **URL**: https://vulners.com/
- **API**: https://vulners.com/api/v3/
- **Use Case**: Security intelligence aggregation

---

## 📦 Datasets

### Pre-compiled CVE Datasets

1. **Kaggle CVE Datasets**

   - [CVE-2020-2024 Dataset](https://www.kaggle.com/datasets)
   - Pre-processed for ML tasks
   - Updated quarterly

2. **NVD Data Feeds (Deprecated but available)**

   - **URL**: https://nvd.nist.gov/vuln/data-feeds
   - Format: JSON, XML
   - Historical archives available

3. **CVEDetails Database Exports**

   - **URL**: https://www.cvedetails.com/
   - Statistical data and trends
   - Vendor-specific datasets

4. **Security Intelligence Feeds**
   - CERT/CC Vulnerability Notes
   - US-CERT National Cyber Awareness System
   - SANS Internet Storm Center

### Research Datasets

1. **VulDeePecker** (Code vulnerability dataset)

   - GitHub: https://github.com/CGCL-codes/VulDeePecker
   - Use Case: Source code analysis

2. **SecBench** (Security benchmarking)
   - Focus: ML for vulnerability detection

---

## 🛠️ NLP Tools & Libraries

### Core NLP Frameworks

#### spaCy

- **URL**: https://spacy.io/
- **Documentation**: https://spacy.io/api
- **Models**:
  - `en_core_web_sm` - Small, fast (12MB)
  - `en_core_web_md` - Medium accuracy (40MB)
  - `en_core_web_lg` - Large, best accuracy (560MB)
  - `en_core_web_trf` - Transformer-based (438MB)
- **Use Cases**:
  - Named Entity Recognition (NER)
  - Dependency parsing
  - POS tagging
  - Lemmatization

#### HuggingFace Transformers

- **URL**: https://huggingface.co/
- **Documentation**: https://huggingface.co/docs/transformers
- **Recommended Models**:
  - `bert-base-uncased` - General purpose
  - `roberta-base` - Better performance
  - `distilbert-base-uncased` - Faster inference
  - `microsoft/codebert-base` - Code understanding
  - `allenai/scibert_scivocab_uncased` - Scientific text
- **Use Cases**:
  - Text classification
  - Semantic similarity
  - Question answering
  - Sentiment analysis

#### NLTK (Natural Language Toolkit)

- **URL**: https://www.nltk.org/
- **Use Cases**:
  - Tokenization
  - Stopword removal
  - Stemming/Lemmatization
  - Basic text preprocessing

### Additional NLP Tools

#### Gensim

- **URL**: https://radimrehurek.com/gensim/
- **Use Cases**:
  - Topic modeling (LDA, LSI)
  - Word embeddings
  - Document similarity

#### TextBlob

- **URL**: https://textblob.readthedocs.io/
- **Use Cases**:
  - Sentiment analysis
  - Simple NLP tasks

#### Stanford CoreNLP

- **URL**: https://stanfordnlp.github.io/CoreNLP/
- **Use Cases**:
  - Advanced linguistic analysis
  - Coreference resolution

---

## 📊 Data Processing & Analysis

### Data Manipulation

- **pandas**: https://pandas.pydata.org/
- **numpy**: https://numpy.org/
- **polars**: https://www.pola.rs/ (faster alternative)

### Visualization

- **matplotlib**: https://matplotlib.org/
- **seaborn**: https://seaborn.pydata.org/
- **plotly**: https://plotly.com/python/
- **altair**: https://altair-viz.github.io/

### Machine Learning

- **scikit-learn**: https://scikit-learn.org/
- **XGBoost**: https://xgboost.readthedocs.io/
- **LightGBM**: https://lightgbm.readthedocs.io/

---

## 🌐 Web Frameworks & APIs

### Backend Frameworks

- **FastAPI**: https://fastapi.tiangolo.com/ (Used in this project)
- **Flask**: https://flask.palletsprojects.com/
- **Django**: https://www.djangoproject.com/

### Database Tools

- **SQLAlchemy**: https://www.sqlalchemy.org/
- **Alembic**: https://alembic.sqlalchemy.org/
- **SQLite**: https://www.sqlite.org/
- **PostgreSQL**: https://www.postgresql.org/

---

## 📖 Research Papers & Articles

### Vulnerability Analysis with NLP

1. **"Automated Vulnerability Detection in Source Code Using Deep Representation Learning"**

   - Authors: R. Russell et al.
   - Conference: IEEE ICMLA 2018
   - [Link](https://arxiv.org/abs/1807.04320)

2. **"VulDeePecker: A Deep Learning-Based System for Vulnerability Detection"**

   - Authors: Z. Li et al.
   - Conference: NDSS 2018
   - Focus: Code vulnerability detection using LSTM

3. **"Automated Software Vulnerability Detection with Machine Learning"**

   - Authors: S. Ghaffarian & H. Shahriari
   - Journal: arXiv 2017
   - [Link](https://arxiv.org/abs/1803.04497)

4. **"Deep Learning for Vulnerability Detection: A Comparative Study"**
   - Authors: C. Croft et al.
   - Conference: RAID 2019

### NLP for Security

5. **"Natural Language Processing for Cybersecurity"**

   - Comprehensive survey of NLP applications in security
   - [Link](https://dl.acm.org/doi/10.1145/3362072)

6. **"Mining Security-Related Information from CVE Descriptions"**

   - Focus: Entity extraction from vulnerability descriptions
   - Techniques: NER, topic modeling

7. **"Predicting Vulnerability Exploitability Using NLP"**
   - Machine learning models for exploit prediction
   - Feature engineering from CVE text

### Topic Modeling & Classification

8. **"Latent Dirichlet Allocation for Security Intelligence"**

   - Application: Categorizing security threats

9. **"BERT for Cybersecurity Text Classification"**
   - Fine-tuning transformers for security domains

---

## 🎓 Tutorials & Courses

### NLP Tutorials

1. **spaCy Course**

   - https://course.spacy.io/
   - Free interactive course

2. **HuggingFace NLP Course**

   - https://huggingface.co/learn/nlp-course
   - Comprehensive transformer training

3. **Fast.ai NLP**
   - https://www.fast.ai/
   - Practical deep learning for NLP

### Security-Specific

4. **OWASP Vulnerability Research**

   - https://owasp.org/
   - Security vulnerability patterns

5. **SANS Reading Room**
   - https://www.sans.org/reading-room/
   - Security whitepapers

---

## 🔧 Development Tools

### Web Scraping

- **BeautifulSoup4**: https://www.crummy.com/software/BeautifulSoup/
- **Scrapy**: https://scrapy.org/
- **Selenium**: https://selenium-python.readthedocs.io/

### Testing

- **pytest**: https://pytest.org/
- **unittest**: https://docs.python.org/3/library/unittest.html
- **coverage.py**: https://coverage.readthedocs.io/

### Documentation

- **Sphinx**: https://www.sphinx-doc.org/
- **MkDocs**: https://www.mkdocs.org/
- **Jupyter Book**: https://jupyterbook.org/

---

## 📱 Deployment & Cloud

### Cloud Platforms for Notebooks

- **Google Colab**: https://colab.research.google.com/
- **Kaggle Kernels**: https://www.kaggle.com/code
- **Binder**: https://mybinder.org/

### Hosting

- **Heroku**: https://www.heroku.com/
- **Railway**: https://railway.app/
- **Render**: https://render.com/
- **AWS**: https://aws.amazon.com/
- **Google Cloud**: https://cloud.google.com/

### Containerization

- **Docker**: https://www.docker.com/
- **Docker Hub**: https://hub.docker.com/

---

## 📚 Books

1. **"Natural Language Processing with Python"** (Bird, Klein, Loper)

   - O'Reilly, 2009
   - Focus: NLTK library

2. **"Speech and Language Processing"** (Jurafsky & Martin)

   - 3rd Edition Draft
   - [Free Online](https://web.stanford.edu/~jurafsky/slp3/)

3. **"Neural Network Methods for Natural Language Processing"** (Goldberg)

   - Morgan & Claypool, 2017

4. **"Hands-On Machine Learning"** (Géron)

   - O'Reilly, 2019
   - Chapter on NLP

5. **"Applied Text Analysis with Python"** (Bengfort et al.)
   - O'Reilly, 2018

---

## 🎯 Security Resources

### Vulnerability Databases

- **CWE (Common Weakness Enumeration)**: https://cwe.mitre.org/
- **CAPEC (Attack Pattern Database)**: https://capec.mitre.org/
- **OVAL (Open Vulnerability Assessment)**: https://oval.mitre.org/

### Standards & Guidelines

- **CVSS (Common Vulnerability Scoring System)**: https://www.first.org/cvss/
- **NIST Cybersecurity Framework**: https://www.nist.gov/cyberframework
- **ISO 27001**: Information Security Standards

### Communities

- **Reddit r/netsec**: https://www.reddit.com/r/netsec/
- **Security Stack Exchange**: https://security.stackexchange.com/
- **OWASP Slack**: https://owasp.org/slack/invite

---

## 🔍 Useful GitHub Repositories

1. **awesome-nlp**

   - https://github.com/keon/awesome-nlp
   - Curated NLP resources

2. **awesome-cybersecurity**

   - https://github.com/fabionoth/awesome-cyber-security
   - Security tools and resources

3. **CVE-Search**

   - https://github.com/cve-search/cve-search
   - CVE database search engine

4. **VulnWhisperer**

   - https://github.com/HASecuritySolutions/VulnWhisperer
   - Vulnerability data aggregation

5. **OpenVAS**
   - https://github.com/greenbone/openvas
   - Vulnerability scanning

---

## 📊 Visualization Tools

### Interactive Dashboards

- **Dash (Plotly)**: https://dash.plotly.com/
- **Streamlit**: https://streamlit.io/
- **Panel**: https://panel.holoviz.org/

### Chart Libraries

- **D3.js**: https://d3js.org/
- **Chart.js**: https://www.chartjs.org/
- **ECharts**: https://echarts.apache.org/

---

## 🎓 Academic Resources

### Journals

- **IEEE Transactions on Information Forensics and Security**
- **ACM Transactions on Privacy and Security**
- **Computers & Security (Elsevier)**

### Conferences

- **ACM CCS** (Computer and Communications Security)
- **USENIX Security**
- **NDSS** (Network and Distributed System Security)
- **IEEE S&P** (Security & Privacy)
- **ACL** (Association for Computational Linguistics)
- **EMNLP** (Empirical Methods in NLP)

---

## 💻 IDEs & Editors

- **VS Code**: https://code.visualstudio.com/
- **PyCharm**: https://www.jetbrains.com/pycharm/
- **Jupyter Lab**: https://jupyterlab.readthedocs.io/
- **Google Colab**: https://colab.research.google.com/

---

## 📮 Stay Updated

### Newsletters

- **NLP News**: http://newsletter.ruder.io/
- **The Batch (Andrew Ng)**: https://www.deeplearning.ai/the-batch/
- **Python Weekly**: https://www.pythonweekly.com/

### Blogs

- **Jay Alammar**: https://jalammar.github.io/
- **Sebastian Ruder**: https://ruder.io/
- **Towards Data Science**: https://towardsdatascience.com/

### Twitter Accounts

- @spacy_io
- @huggingface
- @nvd_nist
- @ThePSF (Python Software Foundation)

---

**Last Updated**: November 2025

**Maintained By**: CVE NLP Project Team

**Contributions**: Pull requests welcome to add more resources!
