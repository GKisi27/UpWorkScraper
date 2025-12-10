"""
Unit tests for Pydantic models.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.models.job import JobListing
from src.models.profile import UserProfile
from src.models.filters import JobFilter


class TestJobListing:
    """Tests for JobListing model."""
    
    def test_create_job_with_required_fields(self):
        """Test creating a job with minimum required fields."""
        job = JobListing(
            title="Python Developer",
            description="We need a Python developer.",
            posted_time="2 hours ago",
            job_url="https://www.upwork.com/jobs/~012345",
        )
        
        assert job.title == "Python Developer"
        assert job.description == "We need a Python developer."
        assert job.posted_time == "2 hours ago"
        assert str(job.job_url) == "https://www.upwork.com/jobs/~012345"
        assert job.budget is None
        assert job.skills == []
    
    def test_create_job_with_all_fields(self, sample_job_data):
        """Test creating a job with all fields."""
        job = JobListing(**sample_job_data)
        
        assert job.title == sample_job_data["title"]
        assert job.budget == sample_job_data["budget"]
        assert job.skills == sample_job_data["skills"]
        assert job.client_location == sample_job_data["client_location"]
    
    def test_budget_parsing(self):
        """Test budget value extraction from string."""
        job = JobListing(
            title="Test Job",
            description="Test",
            posted_time="1 hour ago",
            job_url="https://www.upwork.com/jobs/~012345",
            budget="$1,500",
        )
        
        assert job.budget_value == 1500.0
    
    def test_hourly_rate_parsing(self):
        """Test hourly rate parsing."""
        job = JobListing(
            title="Test Job",
            description="Test",
            posted_time="1 hour ago",
            job_url="https://www.upwork.com/jobs/~012345",
            hourly_rate="$35-$60/hr",
        )
        
        # Should extract first number
        assert job.budget_value == 35.0
    
    def test_to_dict(self, sample_job_data):
        """Test conversion to dictionary."""
        job = JobListing(**sample_job_data)
        data = job.to_dict()
        
        assert data["Title"] == sample_job_data["title"]
        assert data["Budget"] == sample_job_data["budget"]
        assert "Python" in data["Skills"]
        assert "Job URL" in data
    
    def test_invalid_url_raises_error(self):
        """Test that invalid URL raises validation error."""
        with pytest.raises(ValidationError):
            JobListing(
                title="Test",
                description="Test",
                posted_time="1 hour ago",
                job_url="not-a-valid-url",
            )
    
    def test_cover_letter_initially_none(self):
        """Test that cover_letter is None by default."""
        job = JobListing(
            title="Test",
            description="Test",
            posted_time="1 hour ago",
            job_url="https://www.upwork.com/jobs/~012345",
        )
        
        assert job.cover_letter is None
    
    def test_scraped_at_auto_set(self):
        """Test that scraped_at is automatically set."""
        job = JobListing(
            title="Test",
            description="Test",
            posted_time="1 hour ago",
            job_url="https://www.upwork.com/jobs/~012345",
        )
        
        assert job.scraped_at is not None
        assert isinstance(job.scraped_at, datetime)


class TestUserProfile:
    """Tests for UserProfile model."""
    
    def test_load_from_yaml(self, sample_profile_yaml):
        """Test loading profile from YAML file."""
        profile = UserProfile.from_yaml(sample_profile_yaml)
        
        assert profile.name == "Test User"
        assert profile.title == "Senior Python Developer"
        assert "Python" in profile.skills
        assert profile.years_experience == 5
    
    def test_load_from_txt(self, sample_profile_txt):
        """Test loading profile from TXT file."""
        profile = UserProfile.from_txt(sample_profile_txt)
        
        assert profile.name == "Test User"
        assert profile.title == "Python Developer"
    
    def test_auto_detect_format(self, sample_profile_yaml):
        """Test automatic format detection."""
        profile = UserProfile.load(sample_profile_yaml)
        
        assert profile.name == "Test User"
    
    def test_file_not_found(self, tmp_path):
        """Test error when file not found."""
        with pytest.raises(FileNotFoundError):
            UserProfile.from_yaml(tmp_path / "nonexistent.yaml")
    
    def test_to_prompt_context(self, sample_profile_yaml):
        """Test prompt context generation."""
        profile = UserProfile.from_yaml(sample_profile_yaml)
        context = profile.to_prompt_context()
        
        assert "Test User" in context
        assert "Senior Python Developer" in context
        assert "Python" in context
        assert "5 years" in context
    
    def test_get_skills_str(self, sample_profile_yaml):
        """Test skills string generation."""
        profile = UserProfile.from_yaml(sample_profile_yaml)
        skills_str = profile.get_skills_str()
        
        assert "Python" in skills_str
        assert ", " in skills_str  # Comma-separated


class TestJobFilter:
    """Tests for JobFilter model."""
    
    def test_empty_filter(self):
        """Test filter with no criteria."""
        filter_config = JobFilter()
        
        assert not filter_config.has_any_filter()
    
    def test_filter_with_budget(self):
        """Test filter with budget criteria."""
        filter_config = JobFilter(
            min_budget=500,
            max_budget=2000,
        )
        
        assert filter_config.has_any_filter()
        assert filter_config.min_budget == 500
        assert filter_config.max_budget == 2000
    
    def test_filter_with_skills(self):
        """Test filter with skills criteria."""
        filter_config = JobFilter(
            required_skills=["Python", "Django"],
            min_skill_match=1,
        )
        
        assert filter_config.has_any_filter()
        assert len(filter_config.required_skills) == 2
    
    def test_filter_with_keywords(self):
        """Test filter with keyword criteria."""
        filter_config = JobFilter(
            include_keywords=["senior", "lead"],
            exclude_keywords=["junior", "intern"],
        )
        
        assert filter_config.has_any_filter()
        assert "senior" in filter_config.include_keywords
        assert "junior" in filter_config.exclude_keywords
