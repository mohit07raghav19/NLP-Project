# 🔧 Setup Guide - CVE NLP Analysis System

Complete step-by-step guide to set up and run the CVE NLP project on your local machine or Google Colab.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.8 or higher installed
- [ ] Git installed
- [ ] Basic command-line knowledge
- [ ] Text editor or IDE (VS Code, PyCharm, etc.)
- [ ] Internet connection for downloading data
- [ ] (Optional) NVD API key for faster data access

---

## 🚀 Installation Methods

Choose the installation method that best suits your needs:

### Method 1: Google Colab (Easiest - No Installation Required)

**Best for:** Quick testing, no local setup, free GPU access

1. Open Google Colab: https://colab.research.google.com/
2. Create new notebook or upload `notebooks/CVE_NLP_Pipeline.ipynb`
3. Run the first cell to install dependencies:

```python
!pip install -q spacy transformers torch pandas numpy matplotlib seaborn plotly
!python -m spacy download en_core_web_sm
```

4. Mount Google Drive (optional, for saving data):

```python
from google.colab import drive
drive.mount('/content/drive')
```

5. Clone the repository:

```python
!git clone https://github.com/mohit07raghav19/NLP-Project.git
%cd NLP-Project
```

6. Run the notebook cells sequentially!

**Advantages:**

- No local installation needed
- Free GPU/TPU access
- Easy sharing and collaboration
- Pre-installed many libraries

**Limitations:**

- Session timeout after inactivity
- Limited storage (15GB in Drive)
- Internet required

---

### Method 2: Local Installation (Recommended for Development)

**Best for:** Full control, offline work, production deployment

#### Step 1: Clone Repository

```bash
# Navigate to your projects directory
cd ~/Desktop/SEM7/NLP

# Clone the repository
git clone https://github.com/mohit07raghav19/NLP-Project.git

# Enter project directory
cd NLP-Project
```

#### Step 2: Create Virtual Environment

**macOS/Linux:**

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show venv path)
which python
```

**Windows:**

```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation
where python
```

#### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# This installs:
# - Data processing: pandas, numpy
# - NLP: spacy, transformers, torch, nltk
# - Database: sqlalchemy, alembic
# - API: fastapi, uvicorn
# - Visualization: matplotlib, seaborn, plotly
# - Testing: pytest
```

**Installation time:** 5-10 minutes depending on internet speed

#### Step 4: Download NLP Models

```bash
# Download spaCy small model (12MB, fast)
python -m spacy download en_core_web_sm

# Optional: Download large model for better accuracy (560MB)
python -m spacy download en_core_web_lg

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

#### Step 5: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your preferred editor
nano .env  # or vim, code, etc.
```

**Update these values in `.env`:**

```bash
# Optional but recommended: Get free API key from
# https://nvd.nist.gov/developers/request-an-api-key
NVD_API_KEY=your_api_key_here

# Database (default SQLite is fine for development)
DATABASE_URL=sqlite:///data/cve_database.db

# API Server
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# NLP Settings
SPACY_MODEL=en_core_web_sm
USE_GPU=False
```

#### Step 6: Initialize Database

```bash
# Run database setup script
python scripts/setup_database.py

# This creates:
# - SQLite database at data/cve_database.db
# - Required tables and schemas
# - Indexes for performance
```

#### Step 7: Verify Installation

```bash
# Run tests to verify everything works
pytest tests/ -v

# Or run a quick check
python -c "import spacy, transformers, fastapi, sqlalchemy; print('✅ All imports successful!')"
```

---

### Method 3: Docker Installation (Advanced)

**Best for:** Containerized deployment, consistent environments

```bash
# Build Docker image
docker build -t cve-nlp-system .

# Run container
docker run -p 8000:8000 -v $(pwd)/data:/app/data cve-nlp-system

# Access at http://localhost:8000
```

---

## 🔑 Getting NVD API Key (Recommended)

The NVD API key significantly improves data collection speed.

### Why You Need It:

- **Without key:** 5 requests / 30 seconds (~200 CVEs/minute)
- **With key:** 50 requests / 30 seconds (~2000 CVEs/minute)
- **It's FREE** and takes 2 minutes!

### How to Get:

1. Visit: https://nvd.nist.gov/developers/request-an-api-key

2. Fill out the form:

   - **Name:** Your name
   - **Email:** Your email (you'll receive the key here)
   - **Organization:** Your university/company (optional)
   - **Reason:** Academic/Research Project

3. Check your email for the API key

4. Add to `.env` file:

   ```bash
   NVD_API_KEY=your-actual-api-key-here
   ```

5. Done! The system will automatically use it.

---

## 📊 Data Directory Structure

After setup, your data directory should look like:

```
data/
├── raw/                    # Raw CVE JSON from API
│   ├── cves_2024.json
│   └── cves_batch_001.json
├── processed/              # Cleaned and processed data
│   ├── processed_cves.json
│   └── extracted_entities.csv
├── cache/                  # API response cache
│   └── nvd_cache_*.pkl
└── cve_database.db        # SQLite database
```

---

## 🎯 Quick Test Run

### Test 1: Data Collection

```bash
# Collect 100 recent CVEs
python scripts/run_pipeline.py --step collection --limit 100

# Expected output:
# ✅ Fetched 100 CVEs
# ✅ Saved to data/raw/cves_<timestamp>.json
```

### Test 2: NLP Processing

```bash
# Process collected CVEs
python scripts/run_pipeline.py --step nlp

# Expected output:
# ✅ Loaded 100 CVEs
# ✅ Extracted entities from 100 descriptions
# ✅ Saved results to data/processed/
```

### Test 3: Start API Server

```bash
# Start FastAPI server
uvicorn api.main:app --reload

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
```

Open browser: http://localhost:8000/docs (Interactive API documentation)

### Test 4: Run Notebook

```bash
# Start Jupyter
jupyter notebook

# Open notebooks/CVE_NLP_Pipeline.ipynb
# Run all cells (Cell -> Run All)
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'spacy'"

**Solution:**

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Issue: "Can't find model 'en_core_web_sm'"

**Solution:**

```bash
# Download the model
python -m spacy download en_core_web_sm

# Verify installation
python -m spacy validate
```

---

### Issue: "SQLite database is locked"

**Solution:**

```bash
# Close all applications accessing the database
# Delete database and reinitialize
rm data/cve_database.db
python scripts/setup_database.py
```

---

### Issue: "API rate limit exceeded (429 error)"

**Solution:**

1. Get an NVD API key (see above)
2. Add to `.env` file
3. Increase delay in `config/config.yaml`:
   ```yaml
   data_collection:
     nvd_api:
       rate_limit:
         delay_between_requests: 1.0 # Increase from 0.6
   ```

---

### Issue: "Slow model loading / Out of memory"

**Solution:**

```bash
# Use smaller spaCy model
python -m spacy download en_core_web_sm  # instead of lg

# Update .env
SPACY_MODEL=en_core_web_sm

# Reduce batch size in config/config.yaml
nlp:
  spacy:
    batch_size: 50  # Reduce from 100
```

---

### Issue: "Port 8000 already in use"

**Solution:**

```bash
# Use different port
uvicorn api.main:app --port 8001

# Or kill process using port 8000
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## 🔄 Updating the Project

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install --upgrade -r requirements.txt

# Update spaCy models if needed
python -m spacy download en_core_web_sm --upgrade

# Run tests
pytest tests/
```

---

## 📦 Optional Enhancements

### GPU Acceleration (for transformers)

If you have NVIDIA GPU:

```bash
# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Update .env
USE_GPU=True

# Verify GPU is available
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### PostgreSQL Database (for production)

```bash
# Install PostgreSQL
# macOS:
brew install postgresql

# Start PostgreSQL
brew services start postgresql

# Create database
createdb cve_db

# Update .env
DATABASE_URL=postgresql://localhost:5432/cve_db

# Run migrations
alembic upgrade head
```

---

## 📝 Configuration Files

### config/config.yaml

Main configuration file. Key settings:

```yaml
data_collection:
  nvd_api:
    rate_limit:
      requests_per_30s: 50 # With API key
      delay_between_requests: 0.6

nlp:
  spacy:
    model: "en_core_web_sm"
    batch_size: 100

database:
  type: "sqlite"
  sqlite:
    path: "data/cve_database.db"
```

Modify these based on your needs!

---

## ✅ Installation Checklist

After completing setup, verify:

- [ ] Python 3.8+ installed: `python --version`
- [ ] Virtual environment created and activated
- [ ] All dependencies installed: `pip list`
- [ ] spaCy model downloaded: `python -m spacy validate`
- [ ] `.env` file configured
- [ ] Database initialized: `ls data/cve_database.db`
- [ ] Tests pass: `pytest tests/ -v`
- [ ] API server starts: `uvicorn api.main:app`
- [ ] Jupyter notebook opens: `jupyter notebook`

---

## 🎓 Next Steps

Once installation is complete:

1. **Read the README.md** for project overview
2. **Explore notebooks/** for interactive examples
3. **Check docs/resources.md** for learning materials
4. **Run the pipeline**: `python scripts/run_pipeline.py --all`
5. **Start building!**

---

## 📞 Getting Help

If you encounter issues:

1. Check this setup guide thoroughly
2. Review error messages carefully
3. Check GitHub Issues: [Project Issues](https://github.com/mohit07raghav19/NLP-Project/issues)
4. Consult documentation in `docs/`
5. Ask on Stack Overflow with tag `nlp` and `cve`

---

## 📚 Additional Resources

- [Python Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)
- [spaCy Installation](https://spacy.io/usage)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [NVD API Documentation](https://nvd.nist.gov/developers)

---

**Happy Coding! 🚀**

If you successfully complete the setup, you're ready to dive into CVE analysis with NLP!
