# Spiders module
# Note: Imports are lazy to avoid issues with crawl4ai dependencies during testing

def get_upwork_spider():
    """Lazy import of UpworkSpider to avoid import errors during testing."""
    from src.spiders.upwork_spider import UpworkSpider
    return UpworkSpider

__all__ = ["get_upwork_spider"]

