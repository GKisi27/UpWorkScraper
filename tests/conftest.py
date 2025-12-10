"""
Pytest configuration and fixtures.
"""

import pytest
from datetime import datetime


# Sample HTML for mocking Upwork responses
SAMPLE_UPWORK_HTML = """
<article data-test="job-tile">
    <h2><a href="/jobs/~012345abcdef">Senior Python Developer for Data Pipeline</a></h2>
    <p data-test="job-description-text">
        We need an experienced Python developer to build a scalable data pipeline.
        Must have experience with asyncio, PostgreSQL, and cloud infrastructure.
    </p>
    <span data-test="budget">$1,500</span>
    <span data-test="client-location">United States</span>
    <span data-test="posted-on">2 hours ago</span>
    <span data-test="token">Python</span>
    <span data-test="token">PostgreSQL</span>
    <span data-test="token">AWS</span>
</article>
<article data-test="job-tile">
    <h2><a href="/jobs/~067890ghijkl">Full Stack Developer - React & Django</a></h2>
    <p data-test="job-description-text">
        Looking for a full stack developer to build a web application.
        React frontend, Django REST backend. 3+ years experience required.
    </p>
    <span data-test="is-hourly"></span>
    <span data-test="hourly-rate">$35-$60/hr</span>
    <span data-test="client-location">Canada</span>
    <span data-test="posted-on">1 day ago</span>
    <span data-test="token">React</span>
    <span data-test="token">Django</span>
    <span data-test="token">Python</span>
</article>
<article data-test="job-tile">
    <h2><a href="/jobs/~0abcdefghijk">Junior Web Scraping Developer</a></h2>
    <p data-test="job-description-text">
        Need a developer to build web scrapers using Python and Selenium.
        Should know about proxies and anti-bot techniques.
    </p>
    <span data-test="budget">$200</span>
    <span data-test="client-location">India</span>
    <span data-test="posted-on">3 days ago</span>
    <span data-test="token">Python</span>
    <span data-test="token">Selenium</span>
    <span data-test="token">Web Scraping</span>
</article>
"""


@pytest.fixture
def sample_html():
    """Provide sample Upwork HTML for testing."""
    return SAMPLE_UPWORK_HTML


@pytest.fixture
def sample_job_data():
    """Provide sample job data dictionary."""
    return {
        "title": "Senior Python Developer",
        "description": "We need a Python developer for our data team.",
        "budget": "$1,500",
        "hourly_rate": None,
        "client_location": "United States",
        "posted_time": "2 hours ago",
        "job_url": "https://www.upwork.com/jobs/~012345abcdef",
        "skills": ["Python", "PostgreSQL", "AWS"],
    }


@pytest.fixture
def sample_jobs():
    """Provide list of sample JobListing objects."""
    from src.models.job import JobListing
    
    return [
        JobListing(
            title="Senior Python Developer",
            description="Build a data pipeline with asyncio.",
            budget="$1,500",
            client_location="United States",
            posted_time="2 hours ago",
            job_url="https://www.upwork.com/jobs/~012345abcdef",
            skills=["Python", "PostgreSQL", "AWS"],
        ),
        JobListing(
            title="Full Stack Developer",
            description="React frontend, Django backend.",
            hourly_rate="$35-$60/hr",
            client_location="Canada",
            posted_time="1 day ago",
            job_url="https://www.upwork.com/jobs/~067890ghijkl",
            skills=["React", "Django", "Python"],
        ),
        JobListing(
            title="Junior Web Scraper",
            description="Build web scrapers with Selenium.",
            budget="$200",
            client_location="India",
            posted_time="3 days ago",
            job_url="https://www.upwork.com/jobs/~0abcdefghijk",
            skills=["Python", "Selenium", "Web Scraping"],
        ),
    ]


@pytest.fixture
def sample_profile_yaml(tmp_path):
    """Create a temporary profile YAML file."""
    profile_content = """
name: "Test User"
title: "Senior Python Developer"
years_experience: 5
skills:
  - Python
  - FastAPI
  - PostgreSQL
bio: |
  Experienced Python developer specializing in web scraping 
  and data engineering.
achievements:
  - "Built high-performance scrapers"
  - "Led team of 3 developers"
portfolio_url: "https://github.com/testuser"
rate: "$50-75/hr"
availability: "30 hours/week"
location: "Remote"
tone: "professional"
"""
    profile_path = tmp_path / "profile.yaml"
    profile_path.write_text(profile_content)
    return profile_path


@pytest.fixture
def sample_profile_txt(tmp_path):
    """Create a temporary profile TXT file."""
    profile_content = """name: Test User
title: Python Developer
skills: Python, FastAPI, PostgreSQL
bio: Experienced developer with 5 years experience.
rate: $50/hr
"""
    profile_path = tmp_path / "profile.txt"
    profile_path.write_text(profile_content)
    return profile_path
