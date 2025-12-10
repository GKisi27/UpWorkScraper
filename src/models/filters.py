"""
Job filter criteria model.
Defines filter parameters for job selection.
"""

from typing import Optional
from pydantic import BaseModel, Field


class JobFilter(BaseModel):
    """Filter criteria for job selection."""
    
    # Budget filters
    min_budget: Optional[float] = Field(default=None, description="Minimum budget")
    max_budget: Optional[float] = Field(default=None, description="Maximum budget")
    
    # Skill matching
    required_skills: list[str] = Field(default_factory=list, description="Required skills")
    min_skill_match: int = Field(default=1, ge=0, description="Minimum skills to match")
    
    # Keyword filters
    include_keywords: list[str] = Field(default_factory=list, description="Must contain keywords")
    exclude_keywords: list[str] = Field(default_factory=list, description="Must not contain keywords")
    
    # Location filters
    location_whitelist: list[str] = Field(default_factory=list, description="Allowed locations")
    location_blacklist: list[str] = Field(default_factory=list, description="Excluded locations")
    
    # Time filters
    max_age_hours: Optional[int] = Field(default=None, description="Maximum job age in hours")
    
    def has_any_filter(self) -> bool:
        """Check if any filter is active."""
        return any([
            self.min_budget is not None,
            self.max_budget is not None,
            len(self.required_skills) > 0,
            len(self.include_keywords) > 0,
            len(self.exclude_keywords) > 0,
            len(self.location_whitelist) > 0,
            len(self.location_blacklist) > 0,
            self.max_age_hours is not None,
        ])
    
    @classmethod
    def from_settings(cls, settings) -> "JobFilter":
        """Create filter from application settings."""
        return cls(
            min_budget=settings.filters.min_budget,
            max_budget=settings.filters.max_budget,
            required_skills=settings.filters.required_skills,
            min_skill_match=settings.filters.min_skill_match,
            include_keywords=settings.filters.include_keywords,
            exclude_keywords=settings.filters.exclude_keywords,
            max_age_hours=settings.filters.max_age_hours,
        )
