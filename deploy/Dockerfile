# ===========================================
# Multi-stage Dockerfile for Upwork Job Scraper
# Optimized for production with Playwright browsers
# ===========================================

# Stage 1: Builder
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.7.1

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Export requirements and install
RUN poetry export -f requirements.txt --without-hashes -o requirements.txt && \
    pip install --prefix=/install -r requirements.txt

# -------------------------------------------
# Stage 2: Runtime
FROM python:3.11-slim as runtime

# Labels
LABEL maintainer="developer@example.com" \
      version="1.0.0" \
      description="Upwork Job Scraper with AI Cover Letter Generator"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    # Playwright settings
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Create non-root user for security
RUN groupadd -r scraper && useradd -r -g scraper scraper

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Required for Playwright
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    fonts-liberation \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Set working directory
WORKDIR /app

# Install Playwright and browsers
RUN pip install playwright && \
    playwright install chromium && \
    playwright install-deps chromium

# Copy application code
COPY src/ ./src/
COPY profile.yaml.example ./

# Create output directory
RUN mkdir -p /app/output && chown -R scraper:scraper /app

# Switch to non-root user
USER scraper

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import src.core.config; print('OK')" || exit 1

# Default command
ENTRYPOINT ["python", "-m", "src.main"]

# Default arguments (can be overridden)
CMD ["--help"]
