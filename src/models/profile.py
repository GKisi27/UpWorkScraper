"""
User profile model for cover letter generation.
Loads from YAML file and provides structured data for LangChain prompts.
"""

from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """User profile for personalized cover letter generation."""
    
    # Basic info
    name: str = Field(..., description="Full name")
    title: str = Field(..., description="Professional title")
    years_experience: int = Field(default=0, description="Years of experience")
    
    # Skills and expertise
    skills: list[str] = Field(default_factory=list, description="List of skills")
    
    # Professional content
    bio: str = Field(default="", description="Professional bio/summary")
    achievements: list[str] = Field(default_factory=list, description="Key achievements")
    
    # Links
    portfolio_url: Optional[str] = Field(default=None, description="Portfolio URL")
    linkedin_url: Optional[str] = Field(default=None, description="LinkedIn URL")
    website_url: Optional[str] = Field(default=None, description="Personal website")
    
    # Rate and availability
    rate: Optional[str] = Field(default=None, description="Hourly rate range")
    availability: Optional[str] = Field(default=None, description="Weekly availability")
    
    # Location
    location: Optional[str] = Field(default=None, description="Location")
    timezone: Optional[str] = Field(default=None, description="Timezone")
    
    # Style
    tone: str = Field(default="professional", description="Writing tone preference")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    
    @classmethod
    def from_yaml(cls, path: str | Path) -> "UserProfile":
        """Load profile from YAML file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Profile file not found: {path}")
        
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        return cls(**data)
    
    @classmethod
    def from_txt(cls, path: str | Path) -> "UserProfile":
        """
        Load profile from plain text file.
        Expects a simple format with key: value pairs.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Profile file not found: {path}")
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse simple key: value format or treat as bio
        lines = content.strip().split("\n")
        data = {"name": "User", "title": "Developer", "bio": content}
        
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower().replace(" ", "_")
                value = value.strip()
                if key in ["name", "title", "bio", "rate", "location"]:
                    data[key] = value
                elif key == "skills":
                    data["skills"] = [s.strip() for s in value.split(",")]
        
        return cls(**data)
    
    @classmethod
    def load(cls, path: str | Path) -> "UserProfile":
        """Auto-detect format and load profile."""
        path = Path(path)
        if path.suffix.lower() in [".yaml", ".yml"]:
            return cls.from_yaml(path)
        elif path.suffix.lower() == ".txt":
            return cls.from_txt(path)
        else:
            # Try YAML first, then txt
            try:
                return cls.from_yaml(path)
            except Exception:
                return cls.from_txt(path)
    
    def get_skills_str(self) -> str:
        """Get skills as comma-separated string."""
        return ", ".join(self.skills)
    
    def get_achievements_str(self) -> str:
        """Get achievements as bullet points."""
        return "\n".join(f"• {a}" for a in self.achievements)
    
    def to_prompt_context(self) -> str:
        """Generate context string for LLM prompts."""
        parts = [
            f"Name: {self.name}",
            f"Title: {self.title}",
            f"Experience: {self.years_experience} years",
            f"Skills: {self.get_skills_str()}",
            f"\nProfessional Bio:\n{self.bio}",
        ]
        
        if self.achievements:
            parts.append(f"\nKey Achievements:\n{self.get_achievements_str()}")
        
        if self.rate:
            parts.append(f"\nRate: {self.rate}")
        
        if self.availability:
            parts.append(f"Availability: {self.availability}")
        
        if self.portfolio_url:
            parts.append(f"Portfolio: {self.portfolio_url}")
        
        if self.notes:
            parts.append(f"\nAdditional Notes:\n{self.notes}")
        
        return "\n".join(parts)
