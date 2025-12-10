# Upwork Job Scraper with AI Cover Letter Generator

[![CI](https://github.com/yourusername/upwork-scraper/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/upwork-scraper/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-grade, containerized Python application to scrape job data from Upwork.com using [Crawl4AI](https://github.com/unclecode/crawl4ai), filter jobs based on custom criteria, and automatically generate personalized cover letters using LangChain and OpenAI.

## 🚀 Features

- **🕷️ Smart Scraping**: Uses Crawl4AI with stealth mode, random user agents, and human-like behavior to bypass anti-bot detection
- **🔍 Powerful Filtering**: Filter jobs by budget, skills, keywords, client location, and posting age
- **🤖 AI Cover Letters**: Generate personalized, professional cover letters using LangChain + OpenAI
- **📊 Excel Export**: Beautiful formatted Excel output with multiple sheets
- **🐳 Docker Ready**: Multi-stage Dockerfile optimized for production
- **🔄 CI/CD**: GitHub Actions pipeline with linting, testing, and security scans
- **⚙️ 12-Factor Compliant**: All configuration via environment variables

## 📋 Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Docker & Docker Compose (optional, for containerized deployment)
- OpenAI API key (for cover letter generation)

## 🛠️ Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/upwork-scraper.git
   cd upwork-scraper
   ```

2. **Install dependencies with Poetry**
   ```bash
   poetry install
   ```

3. **Install Playwright browsers**
   ```bash
   poetry run playwright install chromium
   ```

4. **Copy and configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Create your profile**
   ```bash
   cp profile.yaml.example profile.yaml
   # Edit profile.yaml with your information
   ```

### Using Conda

If you prefer conda:

```bash
conda create -n upwork-scraper python=3.11
conda activate upwork-scraper
pip install poetry
poetry install
poetry run playwright install chromium
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Scraping
UPWORK_SEARCH_QUERY="Python Developer"
MAX_PAGES=5
OUTPUT_PATH="./output"

# Proxy (optional)
PROXY_URL=  # Leave empty to run without proxy

# Filters
MIN_BUDGET=500
MAX_BUDGET=5000
REQUIRED_SKILLS="Python,Django,FastAPI"
EXCLUDE_KEYWORDS="Junior,Intern"
MAX_AGE_HOURS=48

# AI
OPENAI_API_KEY=your-api-key-here
LLM_MODEL=gpt-4o-mini
PROFILE_PATH=./profile.yaml

# Logging
LOG_LEVEL=INFO
```

### User Profile (profile.yaml)

```yaml
name: "John Doe"
title: "Senior Python Developer"
years_experience: 8
skills:
  - Python
  - FastAPI
  - PostgreSQL
  - Web Scraping
bio: |
  Passionate software engineer with 8+ years of experience...
achievements:
  - "Built a data pipeline processing 10M+ records daily"
  - "Reduced API latency by 60%"
portfolio_url: "https://github.com/johndoe"
rate: "$50-75/hr"
tone: "professional"
```

## 🚀 Usage

### Basic Usage

```bash
# Run with defaults from .env
poetry run python -m src.main

# Or use the Poetry script
poetry run scrape
```

### Command Line Options

```bash
# Custom search query and pages
poetry run python -m src.main --query "JavaScript Developer" --pages 3

# Skip cover letter generation
poetry run python -m src.main --skip-cover-letters

# Run with visible browser (for debugging)
poetry run python -m src.main --no-headless

# Dry run (show config without running)
poetry run python -m src.main --dry-run

# JSON logs (for production)
poetry run python -m src.main --json-logs
```

### Using Docker

```bash
# Build the image
docker-compose build

# Run the scraper
docker-compose run scraper --query "Python Developer" --pages 5

# Run in development mode (with source mounting)
docker-compose --profile dev up scraper-dev
```

## 📁 Project Structure

```
WorkScraper/
├── src/
│   ├── core/           # Configuration (pydantic-settings)
│   ├── models/         # Pydantic data models
│   ├── spiders/        # Crawl4AI scraping logic
│   ├── filters/        # Job filtering engine
│   ├── ai/             # LangChain cover letter generation
│   ├── pipelines/      # Excel export
│   ├── utils/          # Logging, proxy management
│   └── main.py         # Entry point
├── tests/
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── deploy/
│   └── Dockerfile      # Multi-stage Docker build
├── .github/workflows/
│   └── ci.yml          # GitHub Actions CI/CD
├── pyproject.toml      # Dependencies (Poetry)
├── docker-compose.yml  # Container orchestration
└── README.md
```

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Scraper   │────▶│   Filters   │────▶│   AI Gen    │
│  (Crawl4AI) │     │   Engine    │     │ (LangChain) │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
                                        ┌─────────────┐
                                        │   Export    │
                                        │   (Excel)   │
                                        └─────────────┘
```

## 🧪 Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_filters.py

# Run only unit tests
poetry run pytest tests/unit/

# Run with verbose output
poetry run pytest -v
```

## 🔧 Development

### Code Quality

```bash
# Linting
poetry run ruff check src/

# Formatting
poetry run black src/ tests/

# Type checking
poetry run mypy src/
```

### Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

## ⚠️ Important Notes

### Rate Limiting & Anti-Bot

- The scraper includes human-like delays between requests
- Uses random user agents and stealth mode
- Consider using residential proxies for production use
- Respect Upwork's robots.txt and Terms of Service

### Legal Disclaimer

> **Warning**: Web scraping may violate Upwork's Terms of Service. This tool is provided for educational purposes only. Users are responsible for ensuring compliance with all applicable laws and terms of service before using this tool in any capacity.

## 📊 Output

The scraper generates an Excel file with multiple sheets:

1. **Summary**: Overview of scraping results
2. **All Jobs**: Every job scraped
3. **Filtered Jobs**: Jobs matching your criteria
4. **With Cover Letters**: Jobs with generated cover letters

Additionally, individual cover letter text files are saved to `output/cover_letters/`.

---

## 💡 Use Case Examples

### Example 1: Find High-Paying Python Jobs

```bash
# .env configuration
UPWORK_SEARCH_QUERY="Python Developer"
MAX_PAGES=10
MIN_BUDGET=2000
MAX_BUDGET=10000
REQUIRED_SKILLS="Python,FastAPI,PostgreSQL"
EXCLUDE_KEYWORDS="Junior,Entry Level,Intern"
MAX_AGE_HOURS=24

# Run
poetry run python -m src.main
```

**Result**: Scrapes high-budget senior Python jobs posted in last 24 hours

---

### Example 2: Generate Cover Letters for Niche Skills

```yaml
# profile.yaml
name: "Jane Smith"
title: "Machine Learning Engineer"
skills:
  - Python
  - TensorFlow
  - PyTorch
  - MLOps
  - AWS SageMaker
bio: |
  ML Engineer with 5 years specializing in computer vision...
```

```bash
# .env
UPWORK_SEARCH_QUERY="Machine Learning Computer Vision"
REQUIRED_SKILLS="TensorFlow,PyTorch,Computer Vision"
MIN_SKILL_MATCH=2

# Run
poetry run python -m src.main --pages 5
```

**Result**: Finds ML jobs matching 2+ of your skills and generates tailored cover letters

---

### Example 3: Quick Scan Without Cover Letters

```bash
# Fast scrape to see available jobs
poetry run python -m src.main \
  --query "Web Scraping" \
  --pages 3 \
  --skip-cover-letters
```

**Result**: Quick Excel export of all web scraping jobs without AI processing

---

### Example 4: Target Specific Locations

```bash
# .env
UPWORK_SEARCH_QUERY="Full Stack Developer"
LOCATION_WHITELIST="United States,Canada,United Kingdom"

# Run
poetry run python -m src.main
```

**Result**: Only jobs from US, Canada, or UK clients

---

### Example 5: Debugging Mode

```bash
# See what the scraper is doing
poetry run python -m src.main \
  --query "React Developer" \
  --pages 1 \
  --no-headless \
  --dry-run

# Then run for real
poetry run python -m src.main \
  --query "React Developer" \
  --pages 1 \
  --no-headless
```

**Result**: See browser actions in real-time, helpful for debugging issues

---

### Example 6: Using Docker for Isolation

```bash
# Build once
docker-compose build

# Run different queries without changing .env
docker-compose run scraper \
  --query "Django Developer" \
  --pages 5

docker-compose run scraper \
  --query "FastAPI Developer" \
  --pages 5
```

**Result**: Clean runs without environment pollution

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### ❌ Issue: `ImportError: cannot import name 'StealthConfig'`

**Cause**: Version conflict between `crawl4ai` and `playwright_stealth`

**Solution**:
```bash
# Reinstall dependencies
poetry lock
poetry install

# Or install playwright-stealth manually
pip install playwright-stealth --upgrade
```

---

#### ❌ Issue: `No jobs found` or `Empty Excel file`

**Possible Causes**:
1. Filters too restrictive
2. Upwork's HTML structure changed
3. Anti-bot detection triggered

**Solutions**:

**Option 1: Check filters**
```bash
# Run without filters first
poetry run python -m src.main --skip-cover-letters --pages 1

# Check the Excel - if you see jobs, your filters are too strict
```

**Option 2: Test with visible browser**
```bash
# See what's happening
poetry run python -m src.main --no-headless --pages 1
```

**Option 3: Check logs**
```bash
# Enable debug logging
# In .env, set:
LOG_LEVEL=DEBUG

poetry run python -m src.main
```

---

#### ❌ Issue: `OpenAI API Error` or `Rate limit exceeded`

**Cause**: OpenAI API key issue or quota exceeded

**Solutions**:

**Check API key**:
```bash
# Verify your key is set correctly in .env
grep OPENAI_API_KEY .env

# Make sure it doesn't have quotes or extra spaces
# Should be: OPENAI_API_KEY=sk-...
```

**Skip cover letters temporarily**:
```bash
poetry run python -m src.main --skip-cover-letters
```

**Slow down API calls**:
```python
# In src/ai/cover_letter_generator.py, line ~147
# Change delay_between parameter
await generator.generate_batch(filtered_jobs, delay_between=3.0)  # 3 seconds instead of 1
```

---

#### ❌ Issue: `Playwright browser not found`

**Cause**: Chromium browser not installed

**Solution**:
```bash
# Install Playwright browsers
poetry run playwright install chromium

# If still fails, install system dependencies
poetry run playwright install-deps chromium
```

---

#### ❌ Issue: `PermissionError` when saving Excel file

**Cause**: Output file is open in Excel or lacks write permissions

**Solutions**:

**Close the file**:
- Close any Excel windows viewing the output file

**Change output directory**:
```bash
# .env
OUTPUT_PATH=/tmp/upwork_output

# Or use CLI
poetry run python -m src.main --output /tmp/upwork_output
```

**Check permissions**:
```bash
# Create output directory with correct permissions
mkdir -p output
chmod 755 output
```

---

#### ❌ Issue: `Profile file not found`

**Cause**: `profile.yaml` doesn't exist

**Solution**:
```bash
# Create from template
cp profile.yaml.example profile.yaml

# Edit with your info
nano profile.yaml

# Verify path in .env
grep PROFILE_PATH .env
```

---

#### ❌ Issue: Jobs have missing fields (budget, location, etc.)

**Cause**: Upwork's HTML selectors changed

**Solutions**:

**Check extraction strategy**:
```python
# Edit src/spiders/extraction_strategy.py
# Update CSS selectors to match current Upwork HTML

# Test with:
poetry run pytest tests/unit/test_parser.py -v
```

**Fallback to LLM extraction**:
```python
# In src/spiders/upwork_spider.py
# The code automatically falls back to LLM extraction
# if CSS extraction fails
```

---

#### ❌ Issue: `Proxy connection failed`

**Cause**: Invalid proxy URL or proxy server down

**Solutions**:

**Test without proxy**:
```bash
# In .env, leave PROXY_URL empty
PROXY_URL=

# The scraper will continue without proxy
```

**Verify proxy format**:
```bash
# Correct formats:
PROXY_URL=http://proxy.example.com:8080
PROXY_URL=http://user:password@proxy.example.com:8080
```

---

#### ❌ Issue: `Memory error` or `Process killed` during scraping

**Cause**: Too many concurrent requests or large dataset

**Solutions**:

**Reduce page count**:
```bash
# Start with fewer pages
poetry run python -m src.main --pages 3
```

**Increase Docker memory** (if using Docker):
```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      memory: 8G  # Increase from 4G
```

**Close other applications**:
- Free up system RAM before running

---

### Debug Checklist

When something goes wrong, follow this checklist:

- [ ] **Check logs**: Set `LOG_LEVEL=DEBUG` in `.env`
- [ ] **Verify .env file**: All required variables set correctly
- [ ] **Test profile loading**: Run with `--dry-run` to see config
- [ ] **Run with visible browser**: Use `--no-headless` to watch
- [ ] **Start small**: Test with `--pages 1` first
- [ ] **Check tests**: Run `poetry run pytest -v` to verify installation
- [ ] **Update dependencies**: Run `poetry update`
- [ ] **Check Playwright**: Run `poetry run playwright install chromium`

---

### Getting Help

If you're still stuck:

1. **Check logs** in detail:
   ```bash
   poetry run python -m src.main --json-logs 2>&1 | tee debug.log
   ```

2. **Run tests** to verify setup:
   ```bash
   poetry run pytest tests/ -v
   ```

3. **Check GitHub Issues**: See if others had similar problems

4. **Minimal example**: Try the simplest possible command:
   ```bash
   poetry run python -m src.main --query "Python" --pages 1 --skip-cover-letters --no-headless
   ```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Crawl4AI](https://github.com/unclecode/crawl4ai) - AI-powered web crawling
- [LangChain](https://www.langchain.com/) - LLM application framework
- [Playwright](https://playwright.dev/) - Browser automation
