# Changelog

All notable changes to the CVE NLP Analysis System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features

- Real-time CVE monitoring and alerts
- Multi-language support for international CVE descriptions
- Machine learning model for automatic severity prediction
- Integration with additional vulnerability databases
- Automated report generation with PDF export
- Docker containerization for easy deployment
- PostgreSQL migration scripts
- CI/CD pipeline integration
- Advanced topic modeling with dynamic topic discovery
- Vulnerability impact prediction models

---

## [0.1.0] - 2025-11-25

### Added

#### Project Structure

- Initial project directory structure with modular organization
- Created `src/` directory with separate modules for:
  - Data collection (`data_collection/`)
  - Preprocessing (`preprocessing/`)
  - NLP processing (`nlp/`)
  - Database operations (`database/`)
  - Analysis and visualization (`analysis/`)
  - Utilities (`utils/`)
- Set up `api/` directory for FastAPI backend
- Created `ui/` directory for web dashboard
- Added `notebooks/` for Jupyter notebooks
- Established `tests/` for unit testing
- Configured `config/` for application settings
- Created `docs/` for documentation

#### Configuration Files

- **requirements.txt**: Complete Python dependencies list
  - Core libraries: pandas, numpy, requests, beautifulsoup4
  - NLP: spaCy, transformers, torch, nltk
  - Database: SQLAlchemy, alembic, psycopg2-binary
  - API: FastAPI, uvicorn, pydantic
  - Visualization: matplotlib, seaborn, plotly
  - Testing: pytest, pytest-cov
- **.env.example**: Environment variable template
  - NVD API key configuration
  - Database connection settings
  - API server configuration
  - NLP model settings
- **config.yaml**: Comprehensive application configuration
  - Data collection parameters
  - NLP processing settings
  - Database configuration
  - API settings
  - Logging configuration
- **.gitignore**: Git ignore rules for Python, data, models, and IDE files

#### Documentation

- **README.md**: Comprehensive project documentation
  - Project overview and features
  - Architecture diagram
  - Detailed installation instructions
  - Quick start guide with multiple options
  - Usage examples for all major components
  - API documentation
  - Examples and use cases
- **docs/resources.md**: Extensive resource collection
  - NVD API documentation and guides
  - Alternative CVE data sources
  - Pre-compiled datasets
  - NLP tools and libraries (spaCy, HuggingFace)
  - Research papers on vulnerability analysis
  - Security resources and standards
  - Tutorials and courses
  - GitHub repositories
  - Visualization tools
- **CHANGELOG.md**: This file for tracking project changes

#### Core Modules (Structure Ready)

- Data Collection module skeleton
  - NVD API client placeholder
  - Web scraping utilities placeholder
- Preprocessing module skeleton
  - Text cleaning utilities placeholder
  - Tokenization module placeholder
- NLP module skeleton
  - NER extractor placeholder
  - Transformer-based extractor placeholder
  - Rule-based pattern matching placeholder
- Database module skeleton
  - SQLAlchemy models placeholder
  - CRUD operations placeholder
- Analysis module skeleton
  - Trend analysis placeholder
  - Statistical metrics placeholder
  - Visualization functions placeholder

#### Infrastructure

- Logging directory structure
- Data directory structure (raw, processed, cache)
- Models directory for saved ML models
- Scripts directory for utility scripts

### Technical Details

#### Dependencies

- Python 3.8+ required
- Core frameworks:
  - spaCy 3.7.2 for statistical NLP
  - Transformers 4.36.2 for neural models
  - FastAPI 0.108.0 for API
  - SQLAlchemy 2.0.23 for ORM
  - PyTorch 2.1.2 for deep learning
  - pandas 2.1.4 for data manipulation

#### Architecture Decisions

- **Database**: SQLite for development, PostgreSQL support for production
- **API Framework**: FastAPI for modern async API with automatic documentation
- **NLP Stack**: Hybrid approach using both spaCy and transformers
- **Deployment**: Google Colab compatibility for easy cloud execution
- **Configuration**: YAML-based config with environment variable overrides
- **Rate Limiting**: Built-in support for NVD API rate limits (5/50 requests per 30s)

### Security

- API keys stored in environment variables
- `.env` file excluded from version control
- Secure database connection string handling

### Documentation Standards

- Comprehensive inline code documentation
- README with detailed usage examples
- Separate resources document for external references
- Changelog following Keep a Changelog format

### Development Setup

- Virtual environment recommended
- Pre-commit hooks ready structure
- Testing framework configured (pytest)
- Coverage reporting enabled

---

## Project Metadata

### Version Numbering

- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible functionality additions
- **PATCH**: Backward-compatible bug fixes

### Release Dates

- Format: YYYY-MM-DD (ISO 8601)

### Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Vulnerability fixes

---

## Links

- [Project Repository](https://github.com/mohit07raghav19/NLP-Project)
- [Issue Tracker](https://github.com/mohit07raghav19/NLP-Project/issues)
- [Documentation](docs/)

---

**Note**: This project is under active development as part of an academic NLP project. Features and structure may change rapidly during early development phases.
