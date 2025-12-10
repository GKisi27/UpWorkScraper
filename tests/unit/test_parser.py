"""
Unit tests for HTML parsing and extraction.
Tests extraction logic with mocked HTML - no network calls.
"""

import json
import pytest


# Skip tests that depend on crawl4ai if import fails
try:
    from src.spiders.extraction_strategy import (
        UPWORK_JOB_CARD_SCHEMA,
        create_css_extraction_strategy,
    )
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    UPWORK_JOB_CARD_SCHEMA = None


class TestExtractionStrategy:
    """Tests for extraction strategies."""
    
    @pytest.mark.skipif(not CRAWL4AI_AVAILABLE, reason="crawl4ai not available")
    def test_schema_has_required_fields(self):
        """Test that schema defines all required fields."""
        fields = {f["name"] for f in UPWORK_JOB_CARD_SCHEMA["fields"]}
        
        required = {"title", "description", "budget", "hourly_rate", 
                   "client_location", "posted_time", "job_url", "skills"}
        
        assert required.issubset(fields)
    
    @pytest.mark.skipif(not CRAWL4AI_AVAILABLE, reason="crawl4ai not available")
    def test_create_css_strategy(self):
        """Test creating CSS extraction strategy."""
        strategy = create_css_extraction_strategy()
        
        assert strategy is not None
    
    @pytest.mark.skipif(not CRAWL4AI_AVAILABLE, reason="crawl4ai not available")
    def test_base_selector_defined(self):
        """Test that base selector is defined for job cards."""
        assert "baseSelector" in UPWORK_JOB_CARD_SCHEMA
        assert len(UPWORK_JOB_CARD_SCHEMA["baseSelector"]) > 0


@pytest.mark.skipif(not CRAWL4AI_AVAILABLE, reason="crawl4ai not available")
class TestJobParsing:
    """Tests for job parsing from extracted content."""
    
    def test_parse_extracted_json_list(self):
        """Test parsing extracted content as JSON list."""
        from src.spiders.upwork_spider import UpworkSpider
        
        extracted = json.dumps([
            {
                "title": "Python Developer",
                "description": "We need a Python developer.",
                "budget": "$1,000",
                "client_location": "USA",
                "posted_time": "2 hours ago",
                "job_url": "/jobs/~012345",
                "skills": ["Python", "Django"],
            }
        ])
        
        spider = UpworkSpider()
        # We need to run the async method
        import asyncio
        jobs = asyncio.run(spider._parse_jobs(extracted))
        
        assert len(jobs) == 1
        assert jobs[0].title == "Python Developer"
        assert jobs[0].budget == "$1,000"
        assert "Python" in jobs[0].skills
    
    def test_parse_extracted_json_dict(self):
        """Test parsing extracted content as JSON dict with jobs key."""
        from src.spiders.upwork_spider import UpworkSpider
        
        extracted = json.dumps({
            "jobs": [
                {
                    "title": "React Developer",
                    "description": "Build a React app.",
                    "hourly_rate": "$40/hr",
                    "posted_time": "1 day ago",
                    "job_url": "https://www.upwork.com/jobs/~067890",
                    "skills": ["React", "JavaScript"],
                }
            ]
        })
        
        spider = UpworkSpider()
        import asyncio
        jobs = asyncio.run(spider._parse_jobs(extracted))
        
        assert len(jobs) == 1
        assert jobs[0].title == "React Developer"
    
    def test_parse_empty_content(self):
        """Test parsing empty content returns empty list."""
        from src.spiders.upwork_spider import UpworkSpider
        
        spider = UpworkSpider()
        import asyncio
        
        # Empty string
        jobs = asyncio.run(spider._parse_jobs(""))
        assert jobs == []
        
        # None
        jobs = asyncio.run(spider._parse_jobs(None))
        assert jobs == []
    
    def test_parse_invalid_json(self):
        """Test parsing invalid JSON returns empty list."""
        from src.spiders.upwork_spider import UpworkSpider
        
        spider = UpworkSpider()
        import asyncio
        jobs = asyncio.run(spider._parse_jobs("not valid json"))
        
        assert jobs == []
    
    def test_relative_url_converted_to_absolute(self):
        """Test that relative URLs are converted to absolute."""
        from src.spiders.upwork_spider import UpworkSpider
        
        extracted = json.dumps([
            {
                "title": "Test Job",
                "description": "Test",
                "posted_time": "1 hour ago",
                "job_url": "/jobs/~012345",  # Relative URL
            }
        ])
        
        spider = UpworkSpider()
        import asyncio
        jobs = asyncio.run(spider._parse_jobs(extracted))
        
        assert str(jobs[0].job_url).startswith("https://www.upwork.com")
    
    def test_skip_jobs_without_url(self):
        """Test that jobs without URL are skipped."""
        from src.spiders.upwork_spider import UpworkSpider
        
        extracted = json.dumps([
            {
                "title": "Job Without URL",
                "description": "Test",
                "posted_time": "1 hour ago",
                # No job_url
            },
            {
                "title": "Job With URL",
                "description": "Test",
                "posted_time": "1 hour ago",
                "job_url": "https://www.upwork.com/jobs/~012345",
            }
        ])
        
        spider = UpworkSpider()
        import asyncio
        jobs = asyncio.run(spider._parse_jobs(extracted))
        
        assert len(jobs) == 1
        assert jobs[0].title == "Job With URL"
    
    def test_skills_as_string_converted_to_list(self):
        """Test that comma-separated skills string is converted to list."""
        from src.spiders.upwork_spider import UpworkSpider
        
        extracted = json.dumps([
            {
                "title": "Test Job",
                "description": "Test",
                "posted_time": "1 hour ago",
                "job_url": "https://www.upwork.com/jobs/~012345",
                "skills": "Python, Django, PostgreSQL",  # String instead of list
            }
        ])
        
        spider = UpworkSpider()
        import asyncio
        jobs = asyncio.run(spider._parse_jobs(extracted))
        
        assert isinstance(jobs[0].skills, list)
        assert "Python" in jobs[0].skills
