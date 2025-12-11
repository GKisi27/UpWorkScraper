"""
Configuration module using Pydantic Settings.
Loads all configuration from environment variables following 12-Factor App methodology.
"""

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class FilterSettings(BaseSettings):
    """Job filtering configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    min_budget: Optional[float] = Field(default=None, description="Minimum budget filter")
    max_budget: Optional[float] = Field(default=None, description="Maximum budget filter")
    required_skills: list[str] = Field(default_factory=list, description="Skills to match")
    include_keywords: list[str] = Field(default_factory=list, description="Keywords to include")
    exclude_keywords: list[str] = Field(default_factory=list, description="Keywords to exclude")
    max_age_hours: Optional[int] = Field(default=None, description="Max job age in hours")
    min_skill_match: int = Field(default=1, description="Minimum skills to match")
    
    @field_validator("required_skills", "include_keywords", "exclude_keywords", mode="before")
    @classmethod
    def parse_comma_separated(cls, v: str | list | None) -> list[str]:
        """Parse comma-separated string into list."""
        if v is None or v == "":
            return []
        if isinstance(v, list):
            return v
        return [item.strip() for item in v.split(",") if item.strip()]


class Settings(BaseSettings):
    """Main application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # Scraping settings
    upwork_search_query: str = Field(
        default="Python Developer",
        description="Search query for Upwork jobs"
    )
    max_pages: int = Field(default=5, ge=1, le=50, description="Maximum pages to scrape")
    output_path: str = Field(default="./output", description="Output directory path")
    
    # Proxy settings (optional)
    proxy_url: Optional[str] = Field(default=None, description="Proxy URL (optional)")
    
    # AI settings
    ai_provider: str = Field(default="gemini", description="AI provider: 'openai' or 'gemini'")
    gemini_api_key: Optional[str] = Field(default=None, description="Google Gemini API key")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    llm_model: str = Field(default="gemini-1.5-flash", description="LLM model to use")
    profile_path: str = Field(default="./profile.yaml", description="Path to user profile")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Nested filter settings
    filters: FilterSettings = Field(default_factory=FilterSettings)
    
    @field_validator("proxy_url", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: str | None) -> str | None:
        """Convert empty string to None for optional fields."""
        if v == "":
            return None
        return v
    
    @property
    def has_proxy(self) -> bool:
        """Check if proxy is configured."""
        return self.proxy_url is not None and self.proxy_url != ""
    
    @property
    def has_ai_key(self) -> bool:
        """Check if an AI API key is configured."""
        if self.ai_provider == "gemini":
            return (
                self.gemini_api_key is not None 
                and self.gemini_api_key != "" 
                and not self.gemini_api_key.startswith("your-")
            )
        else:  # openai
            return (
                self.openai_api_key is not None 
                and self.openai_api_key != "" 
                and not self.openai_api_key.startswith("your-")
            )
    
    @property
    def api_key(self) -> Optional[str]:
        """Get the appropriate API key based on provider."""
        if self.ai_provider == "gemini":
            return self.gemini_api_key
        else:
            return self.openai_api_key
    
    @property
    def has_openai_key(self) -> bool:
        """Check if OpenAI API key is configured (legacy property)."""
        return (
            self.openai_api_key is not None 
            and self.openai_api_key != "" 
            and not self.openai_api_key.startswith("your-")
        )


# Singleton instance
settings = Settings()
