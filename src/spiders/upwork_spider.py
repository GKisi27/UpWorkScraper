"""
Upwork spider using Crawl4AI.
Handles scraping with stealth mode, pagination, and anti-bot measures.
"""

import asyncio
import random
from typing import Optional
from urllib.parse import quote_plus

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

from src.models.job import JobListing
from src.spiders.extraction_strategy import create_css_extraction_strategy
from src.utils.logging import get_logger
from src.utils.proxy_manager import ProxyManager

logger = get_logger(__name__)


class UpworkSpider:
    """
    Async spider for scraping Upwork job listings.
    
    Uses Crawl4AI with stealth mode and human-like behavior
    to avoid bot detection.
    """
    
    BASE_URL = "https://www.upwork.com/nx/search/jobs"
    
    def __init__(
        self,
        proxy_manager: Optional[ProxyManager] = None,
        headless: bool = True,
    ):
        """
        Initialize the spider.
        
        Args:
            proxy_manager: Optional proxy manager for IP rotation
            headless: Run browser in headless mode
        """
        self.proxy_manager = proxy_manager
        self.headless = headless
        self._crawler: Optional[AsyncWebCrawler] = None
    
    def _build_search_url(self, query: str, page: int = 1) -> str:
        """
        Build Upwork search URL with query and pagination.
        
        Args:
            query: Search query string
            page: Page number (1-indexed)
        
        Returns:
            Full search URL
        """
        encoded_query = quote_plus(query)
        url = f"{self.BASE_URL}?q={encoded_query}"
        
        if page > 1:
            url += f"&page={page}"
        
        return url
    
    def _get_browser_config(self) -> BrowserConfig:
        """
        Create browser configuration with stealth settings.
        
        Returns:
            Configured BrowserConfig
        """
        config = BrowserConfig(
            browser_type="chromium",
            headless=self.headless,
            verbose=False,
            # Anti-bot settings
            user_agent_mode="random",  # Random realistic user agent
            # Viewport settings for human-like browsing
            viewport_width=1920,
            viewport_height=1080,
        )
        
        # Add proxy if configured
        if self.proxy_manager and self.proxy_manager.is_configured:
            proxy_config = self.proxy_manager.get_proxy_config()
            if proxy_config:
                config.proxy = proxy_config.get("server")
                if "username" in proxy_config:
                    config.proxy_username = proxy_config.get("username")
                    config.proxy_password = proxy_config.get("password", "")
        
        return config
    
    def _get_crawler_config(self) -> CrawlerRunConfig:
        """
        Create crawler run configuration.
        
        Returns:
            Configured CrawlerRunConfig
        """
        return CrawlerRunConfig(
            # Stealth and anti-bot
            magic=True,  # Enable human-like behavior simulation
            simulate_user=True,  # Simulate user interactions
            override_navigator=True,  # Override navigator properties
            
            # Page loading
            wait_until="networkidle",
            page_timeout=60000,  # 60 seconds
            
            # Extraction
            extraction_strategy=create_css_extraction_strategy(),
            
            # Caching
            cache_mode=CacheMode.BYPASS,  # Don't use cache for fresh results
            
            # Wait for job cards to load
            wait_for="article[data-test='job-tile'], section.job-tile, div[data-ev-label='search_results_impression']",
            delay_before_return_html=2.0,  # Wait for dynamic content
        )
    
    async def _human_delay(self, min_sec: float = 1.5, max_sec: float = 3.5) -> None:
        """Add random delay to simulate human behavior."""
        delay = random.uniform(min_sec, max_sec)
        logger.debug(f"Human delay: {delay:.2f}s")
        await asyncio.sleep(delay)
    
    async def _parse_jobs(self, extracted_content: str) -> list[JobListing]:
        """
        Parse extracted content into JobListing objects.
        
        Args:
            extracted_content: JSON string from extraction strategy
        
        Returns:
            List of JobListing objects
        """
        import json
        
        jobs = []
        
        if not extracted_content:
            logger.warning("No content extracted from page")
            return jobs
        
        try:
            data = json.loads(extracted_content)
            
            # Handle different response formats
            if isinstance(data, list):
                raw_jobs = data
            elif isinstance(data, dict):
                raw_jobs = data.get("jobs", data.get("items", [data]))
            else:
                logger.warning(f"Unexpected data format: {type(data)}")
                return jobs
            
            for job_data in raw_jobs:
                try:
                    # Ensure URL is absolute
                    job_url = job_data.get("job_url", "")
                    if job_url and not job_url.startswith("http"):
                        job_url = f"https://www.upwork.com{job_url}"
                    
                    if not job_url:
                        logger.debug("Skipping job without URL")
                        continue
                    
                    # Handle skills as list
                    skills = job_data.get("skills", [])
                    if isinstance(skills, str):
                        skills = [s.strip() for s in skills.split(",")]
                    
                    job = JobListing(
                        title=job_data.get("title", "Untitled"),
                        description=job_data.get("description", ""),
                        budget=job_data.get("budget"),
                        hourly_rate=job_data.get("hourly_rate"),
                        client_location=job_data.get("client_location"),
                        posted_time=job_data.get("posted_time", "Unknown"),
                        job_url=job_url,
                        skills=skills,
                    )
                    jobs.append(job)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse job: {e}")
                    continue
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
        
        return jobs
    
    async def scrape(
        self,
        query: str,
        max_pages: int = 5,
    ) -> list[JobListing]:
        """
        Scrape Upwork jobs for the given query.
        
        Args:
            query: Search query (e.g., "Python Developer")
            max_pages: Maximum number of pages to scrape
        
        Returns:
            List of JobListing objects
        """
        all_jobs: list[JobListing] = []
        
        logger.info(f"Starting Upwork scrape: query='{query}', max_pages={max_pages}")
        
        browser_config = self._get_browser_config()
        crawler_config = self._get_crawler_config()
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            for page in range(1, max_pages + 1):
                url = self._build_search_url(query, page)
                logger.info(f"Scraping page {page}/{max_pages}: {url}")
                
                try:
                    # Add human-like delay between pages
                    if page > 1:
                        await self._human_delay(2.0, 4.0)
                    
                    # Crawl the page
                    result = await crawler.arun(
                        url=url,
                        config=crawler_config,
                    )
                    
                    if not result.success:
                        logger.error(f"Failed to crawl page {page}: {result.error_message}")
                        continue
                    
                    # Parse jobs from extracted content
                    if result.extracted_content:
                        jobs = await self._parse_jobs(result.extracted_content)
                        logger.info(f"Found {len(jobs)} jobs on page {page}")
                        all_jobs.extend(jobs)
                    else:
                        logger.warning(f"No jobs extracted from page {page}")
                        
                        # If no jobs on this page, likely reached end
                        if page > 1:
                            logger.info("No more results, stopping pagination")
                            break
                    
                except Exception as e:
                    logger.error(f"Error scraping page {page}: {e}")
                    continue
        
        # Deduplicate by URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            url_str = str(job.job_url)
            if url_str not in seen_urls:
                seen_urls.add(url_str)
                unique_jobs.append(job)
        
        logger.info(f"Scraping complete. Total unique jobs: {len(unique_jobs)}")
        return unique_jobs
    
    async def close(self) -> None:
        """Close the crawler if open."""
        if self._crawler:
            await self._crawler.close()
            self._crawler = None
