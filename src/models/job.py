"""
Job listing Pydantic model.
Represents a single job posting from Upwork.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


class JobListing(BaseModel):
    """Represents a job listing scraped from Upwork."""
    
    title: str = Field(..., description="Job title")
    description: str = Field(..., description="Job description")
    budget: Optional[str] = Field(default=None, description="Fixed budget (e.g., '$500')")
    hourly_rate: Optional[str] = Field(default=None, description="Hourly rate range (e.g., '$25-$50/hr')")
    client_location: Optional[str] = Field(default=None, description="Client's location")
    posted_time: str = Field(..., description="When the job was posted (e.g., '2 hours ago')")
    job_url: HttpUrl = Field(..., description="Direct URL to the job posting")
    skills: list[str] = Field(default_factory=list, description="Required skills")
    
    # Fields populated after processing
    cover_letter: Optional[str] = Field(default=None, description="Generated cover letter")
    scraped_at: datetime = Field(default_factory=datetime.now, description="When this job was scraped")
    
    # Computed/parsed fields
    budget_value: Optional[float] = Field(default=None, description="Parsed budget as float")
    
    @field_validator("budget", mode="after")
    @classmethod
    def parse_budget_value(cls, v: str | None, info) -> str | None:
        """Parse budget string and store numeric value."""
        if v is None:
            return v
        # Try to extract numeric value
        import re
        match = re.search(r'\$?([\d,]+(?:\.\d{2})?)', v.replace(',', ''))
        if match:
            try:
                # Store in budget_value field via model_post_init if needed
                pass
            except ValueError:
                pass
        return v
    
    def model_post_init(self, __context) -> None:
        """Post-initialization to compute derived fields."""
        import re
        
        # Parse budget to numeric value
        if self.budget and self.budget_value is None:
            match = re.search(r'\$?([\d,]+(?:\.\d{2})?)', self.budget.replace(',', ''))
            if match:
                try:
                    object.__setattr__(self, 'budget_value', float(match.group(1)))
                except ValueError:
                    pass
        
        # Parse hourly rate if budget not set
        if self.hourly_rate and self.budget_value is None:
            match = re.search(r'\$?([\d.]+)', self.hourly_rate)
            if match:
                try:
                    object.__setattr__(self, 'budget_value', float(match.group(1)))
                except ValueError:
                    pass
    
    def to_dict(self) -> dict:
        """Convert to dictionary for DataFrame export."""
        return {
            "Title": self.title,
            "Description": self.description[:500] + "..." if len(self.description) > 500 else self.description,
            "Budget": self.budget or self.hourly_rate or "Not specified",
            "Client Location": self.client_location or "Not specified",
            "Posted": self.posted_time,
            "Skills": ", ".join(self.skills),
            "Job URL": str(self.job_url),
            "Cover Letter": self.cover_letter or "",
            "Scraped At": self.scraped_at.isoformat(),
        }
    
    class Config:
        """Pydantic config."""
        populate_by_name = True
