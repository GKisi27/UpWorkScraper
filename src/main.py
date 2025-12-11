"""
Upwork Job Scraper - Main Entry Point

Orchestrates the complete pipeline:
1. Load configuration from .env
2. Scrape jobs from Upwork
3. Apply filters
4. Generate cover letters (optional)
5. Export to Excel
"""

import argparse
import asyncio
import sys
from pathlib import Path

from src.core.config import settings
from src.models.filters import JobFilter
from src.models.profile import UserProfile
from src.spiders.upwork_spider import UpworkSpider
from src.filters.job_filter import JobFilterEngine
from src.ai.cover_letter_generator import CoverLetterGenerator
from src.pipelines.excel_pipeline import ExcelExporter
from src.utils.logging import setup_logging, get_logger
from src.utils.proxy_manager import ProxyManager

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Upwork Job Scraper with AI Cover Letter Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with defaults from .env
  python -m src.main
  
  # Override search query and max pages
  python -m src.main --query "JavaScript Developer" --pages 3
  
  # Skip cover letter generation
  python -m src.main --skip-cover-letters
  
  # Filter only mode (no scraping, use cached data)
  python -m src.main --filter-only
  
  # Dry run (show what would happen)
  python -m src.main --dry-run
        """,
    )
    
    parser.add_argument(
        "--query", "-q",
        type=str,
        default=None,
        help="Search query (overrides UPWORK_SEARCH_QUERY in .env)"
    )
    
    parser.add_argument(
        "--pages", "-p",
        type=int,
        default=None,
        help="Maximum pages to scrape (overrides MAX_PAGES in .env)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output directory (overrides OUTPUT_PATH in .env)"
    )
    
    parser.add_argument(
        "--skip-cover-letters",
        action="store_true",
        help="Skip AI cover letter generation"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)"
    )
    
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser with visible UI (for debugging)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show configuration without running"
    )
    
    parser.add_argument(
        "--json-logs",
        action="store_true",
        help="Use JSON log format (for production)"
    )
    
    return parser.parse_args()


async def run_pipeline(args: argparse.Namespace) -> int:
    """
    Run the complete scraping pipeline.
    
    Args:
        args: Parsed command line arguments
    
    Returns:
        Exit code (0 for success)
    """
    # Apply argument overrides
    query = args.query or settings.upwork_search_query
    max_pages = args.pages or settings.max_pages
    output_path = args.output or settings.output_path
    headless = not args.no_headless
    
    logger.info("=" * 60)
    logger.info("UPWORK JOB SCRAPER")
    logger.info("=" * 60)
    logger.info(f"Search Query: {query}")
    logger.info(f"Max Pages: {max_pages}")
    logger.info(f"Output Path: {output_path}")
    logger.info(f"Headless Mode: {headless}")
    logger.info(f"Skip Cover Letters: {args.skip_cover_letters}")
    logger.info(f"Proxy Configured: {settings.has_proxy}")
    logger.info(f"AI Provider: {settings.ai_provider.upper()}")
    logger.info(f"AI Key Configured: {settings.has_ai_key}")
    logger.info("=" * 60)
    
    if args.dry_run:
        logger.info("DRY RUN - Exiting without action")
        return 0
    
    # Initialize components
    proxy_manager = ProxyManager(settings.proxy_url)
    filter_config = JobFilter.from_settings(settings)
    filter_engine = JobFilterEngine(filter_config)
    exporter = ExcelExporter(output_path)
    
    # Step 1: Scrape jobs
    logger.info("STEP 1: Scraping Upwork jobs...")
    spider = UpworkSpider(proxy_manager=proxy_manager, headless=headless)
    
    try:
        all_jobs = await spider.scrape(query=query, max_pages=max_pages)
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        return 1
    
    if not all_jobs:
        logger.warning("No jobs found. Exiting.")
        return 0
    
    logger.info(f"Scraped {len(all_jobs)} jobs")
    
    # Step 2: Apply filters
    logger.info("STEP 2: Applying filters...")
    filtered_jobs = filter_engine.apply_all_filters(all_jobs)
    
    if not filtered_jobs:
        logger.warning("No jobs passed filters. Exporting all jobs without cover letters.")
        exporter.export(all_jobs=all_jobs, filtered_jobs=[])
        return 0
    
    logger.info(f"{len(filtered_jobs)} jobs passed filters")
    
    # Step 3: Generate cover letters (optional)
    jobs_with_letters = filtered_jobs
    
    if not args.skip_cover_letters:
        if settings.has_ai_key:
            logger.info(f"STEP 3: Generating cover letters using {settings.ai_provider.upper()}...")
            
            # Load profile
            profile_path = Path(settings.profile_path)
            if not profile_path.exists():
                logger.warning(f"Profile not found: {profile_path}")
                logger.warning("Skipping cover letter generation. Create profile from profile.yaml.example")
            else:
                try:
                    profile = UserProfile.load(profile_path)
                    generator = CoverLetterGenerator(
                        api_key=settings.api_key,
                        model=settings.llm_model,
                        profile=profile,
                        provider=settings.ai_provider,
                    )
                    
                    jobs_with_letters = await generator.generate_batch(filtered_jobs)
                    
                except Exception as e:
                    logger.error(f"Cover letter generation failed: {e}")
                    logger.warning("Continuing without cover letters")
        else:
            logger.warning(f"STEP 3: Skipping cover letters (no {settings.ai_provider.upper()} API key)")
    else:
        logger.info("STEP 3: Skipping cover letters (--skip-cover-letters)")
    
    # Step 4: Export to Excel
    logger.info("STEP 4: Exporting to Excel...")
    output_file = exporter.export(
        all_jobs=all_jobs,
        filtered_jobs=filtered_jobs,
        jobs_with_letters=jobs_with_letters,
    )
    
    # Also export cover letters as text files
    if any(j.cover_letter for j in jobs_with_letters):
        exporter.export_cover_letters_txt(jobs_with_letters)
    
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info(f"Output: {output_file}")
    logger.info(f"Total Jobs: {len(all_jobs)}")
    logger.info(f"Filtered Jobs: {len(filtered_jobs)}")
    logger.info(f"With Cover Letters: {sum(1 for j in jobs_with_letters if j.cover_letter)}")
    logger.info("=" * 60)
    
    return 0


def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    # Setup logging
    setup_logging(
        level=settings.log_level,
        json_output=args.json_logs,
    )
    
    # Run async pipeline
    try:
        return asyncio.run(run_pipeline(args))
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 130
    except Exception as e:
        logger.exception(f"Unhandled error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
