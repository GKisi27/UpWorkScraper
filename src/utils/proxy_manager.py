"""
Proxy manager module.
Handles optional proxy rotation for web scraping.

If no proxy is configured, the scraper continues without proxy.
This does NOT stop the job - it's a graceful fallback.
"""

from typing import Optional
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ProxyManager:
    """
    Manages proxy configuration for web scraping.
    
    Loads proxy URL from environment. If not set, returns None
    and scraping proceeds without proxy (graceful fallback).
    """
    
    def __init__(self, proxy_url: Optional[str] = None):
        """
        Initialize proxy manager.
        
        Args:
            proxy_url: Proxy URL from settings (can be None)
        """
        self._proxy_url = proxy_url
        self._is_configured = proxy_url is not None and proxy_url != ""
        
        if self._is_configured:
            logger.info(f"Proxy configured: {self._mask_proxy_url(proxy_url)}")
        else:
            logger.warning(
                "No proxy configured. Running without proxy. "
                "This may result in IP blocking for aggressive scraping."
            )
    
    def _mask_proxy_url(self, url: str) -> str:
        """Mask credentials in proxy URL for logging."""
        if "@" not in url:
            return url
        
        # Mask password in URL like http://user:pass@host:port
        try:
            protocol_end = url.index("://") + 3
            at_sign = url.index("@")
            
            # Find colon between user and pass
            creds = url[protocol_end:at_sign]
            if ":" in creds:
                user = creds.split(":")[0]
                masked_creds = f"{user}:****"
            else:
                masked_creds = creds
            
            return url[:protocol_end] + masked_creds + url[at_sign:]
        except (ValueError, IndexError):
            return "****"
    
    @property
    def is_configured(self) -> bool:
        """Check if proxy is configured."""
        return self._is_configured
    
    def get_proxy_config(self) -> Optional[dict]:
        """
        Get proxy configuration for Playwright/Crawl4AI.
        
        Returns:
            Proxy config dict if configured, None otherwise.
            
        Example return:
            {"server": "http://proxy.example.com:8080"}
            or with auth:
            {
                "server": "http://proxy.example.com:8080",
                "username": "user",
                "password": "pass"
            }
        """
        if not self._is_configured:
            return None
        
        url = self._proxy_url
        
        # Parse proxy URL
        try:
            # Handle auth in URL: http://user:pass@host:port
            if "@" in url:
                protocol_end = url.index("://") + 3
                at_sign = url.index("@")
                
                creds = url[protocol_end:at_sign]
                server = url[:protocol_end] + url[at_sign + 1:]
                
                if ":" in creds:
                    username, password = creds.split(":", 1)
                    return {
                        "server": server,
                        "username": username,
                        "password": password,
                    }
                else:
                    return {
                        "server": server,
                        "username": creds,
                    }
            else:
                return {"server": url}
        except Exception as e:
            logger.error(f"Failed to parse proxy URL: {e}")
            return None
    
    def get_proxy_url(self) -> Optional[str]:
        """Get raw proxy URL if configured."""
        return self._proxy_url if self._is_configured else None


def create_proxy_manager(proxy_url: Optional[str] = None) -> ProxyManager:
    """
    Factory function to create proxy manager.
    
    Args:
        proxy_url: Optional proxy URL from settings
    
    Returns:
        Configured ProxyManager instance
    """
    return ProxyManager(proxy_url)
