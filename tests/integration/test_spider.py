"""
Integration tests for the Upwork spider.
Tests the spider with mocked crawler responses.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.utils.proxy_manager import ProxyManager

# Try to import UpworkSpider - may fail if crawl4ai has dependency issues
try:
    from src.spiders.upwork_spider import UpworkSpider
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    UpworkSpider = None


@pytest.mark.skipif(not CRAWL4AI_AVAILABLE, reason="crawl4ai not available")
class TestUpworkSpider:
    """Integration tests for UpworkSpider."""
    
    def test_spider_initialization(self):
        """Test spider initializes with default settings."""
        spider = UpworkSpider()
        
        assert spider.headless is True
        assert spider.proxy_manager is None
    
    def test_spider_with_proxy_manager(self):
        """Test spider with proxy configuration."""
        proxy_manager = ProxyManager("http://user:pass@proxy.example.com:8080")
        spider = UpworkSpider(proxy_manager=proxy_manager, headless=True)
        
        assert spider.proxy_manager is not None
        assert spider.proxy_manager.is_configured
    
    def test_build_search_url(self):
        """Test search URL construction."""
        spider = UpworkSpider()
        
        url = spider._build_search_url("Python Developer", page=1)
        assert "upwork.com" in url
        assert "Python" in url or "python" in url.lower()
        
        url_page2 = spider._build_search_url("Python Developer", page=2)
        assert "page=2" in url_page2
    
    def test_browser_config_headless(self):
        """Test browser config in headless mode."""
        spider = UpworkSpider(headless=True)
        config = spider._get_browser_config()
        
        assert config.headless is True
        assert config.browser_type == "chromium"
    
    def test_browser_config_with_proxy(self):
        """Test browser config includes proxy when configured."""
        proxy_manager = ProxyManager("http://proxy.example.com:8080")
        spider = UpworkSpider(proxy_manager=proxy_manager)
        config = spider._get_browser_config()
        
        assert config.proxy is not None
    
    def test_crawler_config_settings(self):
        """Test crawler run config has correct settings."""
        spider = UpworkSpider()
        config = spider._get_crawler_config()
        
        # Check stealth settings
        assert config.magic is True
        assert config.simulate_user is True
    
    @pytest.mark.asyncio
    async def test_scrape_with_mocked_crawler(self):
        """Test scrape method with fully mocked crawler."""
        spider = UpworkSpider(headless=True)
        
        # Create mock extracted content
        mock_jobs = [
            {
                "title": "Python Developer",
                "description": "We need a Python developer.",
                "budget": "$1,000",
                "posted_time": "2 hours ago",
                "job_url": "https://www.upwork.com/jobs/~012345",
                "skills": ["Python", "Django"],
            },
            {
                "title": "React Developer",
                "description": "Build a React app.",
                "hourly_rate": "$40/hr",
                "posted_time": "1 day ago",
                "job_url": "https://www.upwork.com/jobs/~067890",
                "skills": ["React", "TypeScript"],
            },
        ]
        
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.extracted_content = json.dumps(mock_jobs)
        mock_result.error_message = None
        
        # Patch AsyncWebCrawler
        with patch('src.spiders.upwork_spider.AsyncWebCrawler') as MockCrawler:
            mock_crawler_instance = AsyncMock()
            mock_crawler_instance.arun = AsyncMock(return_value=mock_result)
            mock_crawler_instance.__aenter__ = AsyncMock(return_value=mock_crawler_instance)
            mock_crawler_instance.__aexit__ = AsyncMock(return_value=None)
            MockCrawler.return_value = mock_crawler_instance
            
            jobs = await spider.scrape(query="Python Developer", max_pages=1)
        
        assert len(jobs) == 2
        assert jobs[0].title == "Python Developer"
        assert jobs[1].title == "React Developer"
    
    @pytest.mark.asyncio
    async def test_scrape_deduplicates_by_url(self):
        """Test that duplicate jobs (same URL) are deduplicated."""
        spider = UpworkSpider(headless=True)
        
        # Same job appearing twice
        mock_jobs = [
            {
                "title": "Python Developer",
                "description": "Test",
                "posted_time": "2 hours ago",
                "job_url": "https://www.upwork.com/jobs/~012345",
            },
            {
                "title": "Python Developer",  # Duplicate
                "description": "Test",
                "posted_time": "2 hours ago",
                "job_url": "https://www.upwork.com/jobs/~012345",  # Same URL
            },
        ]
        
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.extracted_content = json.dumps(mock_jobs)
        
        with patch('src.spiders.upwork_spider.AsyncWebCrawler') as MockCrawler:
            mock_crawler_instance = AsyncMock()
            mock_crawler_instance.arun = AsyncMock(return_value=mock_result)
            mock_crawler_instance.__aenter__ = AsyncMock(return_value=mock_crawler_instance)
            mock_crawler_instance.__aexit__ = AsyncMock(return_value=None)
            MockCrawler.return_value = mock_crawler_instance
            
            jobs = await spider.scrape(query="Python", max_pages=1)
        
        assert len(jobs) == 1  # Deduplicated
    
    @pytest.mark.asyncio
    async def test_scrape_handles_failed_page(self):
        """Test scrape continues when a page fails."""
        spider = UpworkSpider(headless=True)
        
        mock_result_fail = MagicMock()
        mock_result_fail.success = False
        mock_result_fail.error_message = "Network error"
        mock_result_fail.extracted_content = None
        
        mock_jobs = [
            {
                "title": "Python Developer",
                "description": "Test",
                "posted_time": "2 hours ago",
                "job_url": "https://www.upwork.com/jobs/~012345",
            }
        ]
        mock_result_success = MagicMock()
        mock_result_success.success = True
        mock_result_success.extracted_content = json.dumps(mock_jobs)
        
        with patch('src.spiders.upwork_spider.AsyncWebCrawler') as MockCrawler:
            mock_crawler_instance = AsyncMock()
            # First page fails, second succeeds
            mock_crawler_instance.arun = AsyncMock(
                side_effect=[mock_result_fail, mock_result_success]
            )
            mock_crawler_instance.__aenter__ = AsyncMock(return_value=mock_crawler_instance)
            mock_crawler_instance.__aexit__ = AsyncMock(return_value=None)
            MockCrawler.return_value = mock_crawler_instance
            
            jobs = await spider.scrape(query="Python", max_pages=2)
        
        # Should still get jobs from successful page
        assert len(jobs) == 1


class TestProxyManager:
    """Tests for proxy manager."""
    
    def test_no_proxy_configured(self):
        """Test manager with no proxy URL."""
        manager = ProxyManager(None)
        
        assert not manager.is_configured
        assert manager.get_proxy_config() is None
    
    def test_empty_string_proxy(self):
        """Test manager with empty string proxy."""
        manager = ProxyManager("")
        
        assert not manager.is_configured
    
    def test_simple_proxy_url(self):
        """Test manager with simple proxy URL."""
        manager = ProxyManager("http://proxy.example.com:8080")
        
        assert manager.is_configured
        config = manager.get_proxy_config()
        assert config["server"] == "http://proxy.example.com:8080"
    
    def test_proxy_with_auth(self):
        """Test manager with authenticated proxy."""
        manager = ProxyManager("http://user:password@proxy.example.com:8080")
        
        assert manager.is_configured
        config = manager.get_proxy_config()
        assert config["server"] == "http://proxy.example.com:8080"
        assert config["username"] == "user"
        assert config["password"] == "password"
    
    def test_mask_proxy_url(self):
        """Test that proxy URL is masked in logs."""
        manager = ProxyManager("http://user:secret@proxy.example.com:8080")
        
        masked = manager._mask_proxy_url("http://user:secret@proxy.example.com:8080")
        assert "secret" not in masked
        assert "user" in masked
        assert "****" in masked
