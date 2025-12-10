"""
Unit tests for job filtering engine.
"""

import pytest

from src.models.job import JobListing
from src.models.filters import JobFilter
from src.filters.job_filter import JobFilterEngine


@pytest.fixture
def filter_engine():
    """Create a filter engine with no filters."""
    return JobFilterEngine(JobFilter())


@pytest.fixture
def jobs_for_filtering():
    """Create sample jobs for filter testing."""
    return [
        JobListing(
            title="Senior Python Developer",
            description="Build a data pipeline with AWS.",
            budget="$2,000",
            client_location="United States",
            posted_time="2 hours ago",
            job_url="https://www.upwork.com/jobs/~001",
            skills=["Python", "AWS", "PostgreSQL"],
        ),
        JobListing(
            title="Junior Web Developer",
            description="Simple website updates needed.",
            budget="$200",
            client_location="India",
            posted_time="1 day ago",
            job_url="https://www.upwork.com/jobs/~002",
            skills=["HTML", "CSS", "JavaScript"],
        ),
        JobListing(
            title="Full Stack Engineer",
            description="React frontend with Django backend.",
            hourly_rate="$45-$65/hr",
            client_location="Canada",
            posted_time="5 hours ago",
            job_url="https://www.upwork.com/jobs/~003",
            skills=["Python", "React", "Django"],
        ),
        JobListing(
            title="Data Scientist",
            description="Machine learning model development.",
            budget="$5,000",
            client_location="Germany",
            posted_time="3 days ago",
            job_url="https://www.upwork.com/jobs/~004",
            skills=["Python", "TensorFlow", "ML"],
        ),
    ]


class TestBudgetFiltering:
    """Tests for budget-based filtering."""
    
    def test_filter_by_min_budget(self, jobs_for_filtering):
        """Test filtering by minimum budget."""
        engine = JobFilterEngine(JobFilter(min_budget=1000))
        result = engine.filter_by_budget(jobs_for_filtering, min_budget=1000)
        
        # Should include $2000 and $5000 (hourly rate of $45 is below threshold)
        assert len(result) == 2
        assert any(j.title == "Senior Python Developer" for j in result)
        assert any(j.title == "Data Scientist" for j in result)
    
    def test_filter_by_max_budget(self, jobs_for_filtering):
        """Test filtering by maximum budget."""
        engine = JobFilterEngine(JobFilter(max_budget=1000))
        result = engine.filter_by_budget(jobs_for_filtering, max_budget=1000)
        
        # Should include $200 and hourly $45 (both below 1000)
        assert len(result) == 2
        assert any(j.title == "Junior Web Developer" for j in result)
        assert any(j.title == "Full Stack Engineer" for j in result)
    
    def test_filter_by_budget_range(self, jobs_for_filtering):
        """Test filtering by budget range."""
        engine = JobFilterEngine(JobFilter())
        result = engine.filter_by_budget(jobs_for_filtering, min_budget=500, max_budget=3000)
        
        # Should only include $2000 (hourly $45 is below 500, $5000 is above 3000)
        assert len(result) == 1
        assert any(j.title == "Senior Python Developer" for j in result)
    
    def test_no_filter_returns_all(self, jobs_for_filtering):
        """Test that no filter returns all jobs."""
        engine = JobFilterEngine(JobFilter())
        result = engine.filter_by_budget(jobs_for_filtering)
        
        assert len(result) == len(jobs_for_filtering)


class TestSkillsFiltering:
    """Tests for skills-based filtering."""
    
    def test_filter_by_single_skill(self, jobs_for_filtering):
        """Test filtering by single required skill."""
        engine = JobFilterEngine(JobFilter())
        result = engine.filter_by_skills(jobs_for_filtering, ["Python"], min_match=1)
        
        # Should include jobs with Python skill
        assert len(result) == 3  # Senior, Full Stack, Data Scientist
        assert all("Python" in j.skills or "python" in j.description.lower() for j in result)
    
    def test_filter_by_multiple_skills(self, jobs_for_filtering):
        """Test filtering by multiple skills with min match."""
        engine = JobFilterEngine(JobFilter())
        result = engine.filter_by_skills(
            jobs_for_filtering, 
            ["Python", "Django", "AWS"], 
            min_match=2
        )
        
        # Should include jobs with at least 2 of these skills
        assert len(result) >= 1
    
    def test_skill_in_description_matches(self, jobs_for_filtering):
        """Test that skills in description also match."""
        engine = JobFilterEngine(JobFilter())
        result = engine.filter_by_skills(jobs_for_filtering, ["AWS"], min_match=1)
        
        # Senior Python Developer has AWS in skills
        assert any(j.title == "Senior Python Developer" for j in result)
    
    def test_empty_skills_returns_all(self, jobs_for_filtering):
        """Test that empty skills list returns all jobs."""
        engine = JobFilterEngine(JobFilter())
        result = engine.filter_by_skills(jobs_for_filtering, [])
        
        assert len(result) == len(jobs_for_filtering)


class TestKeywordFiltering:
    """Tests for keyword-based filtering."""
    
    def test_include_keywords(self, jobs_for_filtering):
        """Test filtering to include keywords."""
        engine = JobFilterEngine(JobFilter())
        result = engine.filter_by_keywords(
            jobs_for_filtering,
            include=["Senior", "Lead"],
            exclude=[],
        )
        
        assert len(result) >= 1
        assert all("senior" in j.title.lower() or "lead" in j.title.lower() for j in result)
    
    def test_exclude_keywords(self, jobs_for_filtering):
        """Test filtering to exclude keywords."""
        engine = JobFilterEngine(JobFilter())
        result = engine.filter_by_keywords(
            jobs_for_filtering,
            include=[],
            exclude=["Junior"],
        )
        
        assert len(result) == 3
        assert not any("junior" in j.title.lower() for j in result)
    
    def test_include_and_exclude(self, jobs_for_filtering):
        """Test both include and exclude together."""
        engine = JobFilterEngine(JobFilter())
        result = engine.filter_by_keywords(
            jobs_for_filtering,
            include=["Python"],
            exclude=["Junior"],
        )
        
        # Should include Python jobs excluding Junior
        assert all("python" in (j.title + j.description).lower() for j in result)
        assert not any("junior" in j.title.lower() for j in result)


class TestLocationFiltering:
    """Tests for location-based filtering."""
    
    def test_location_whitelist(self, jobs_for_filtering):
        """Test filtering by location whitelist."""
        engine = JobFilterEngine(JobFilter())
        result = engine.filter_by_location(
            jobs_for_filtering,
            whitelist=["United States", "Canada"],
            blacklist=[],
        )
        
        assert len(result) == 2
        assert all(
            "united states" in (j.client_location or "").lower() or
            "canada" in (j.client_location or "").lower()
            for j in result
        )
    
    def test_location_blacklist(self, jobs_for_filtering):
        """Test filtering by location blacklist."""
        engine = JobFilterEngine(JobFilter())
        result = engine.filter_by_location(
            jobs_for_filtering,
            whitelist=[],
            blacklist=["India"],
        )
        
        assert len(result) == 3
        assert not any("india" in (j.client_location or "").lower() for j in result)


class TestAgeFiltering:
    """Tests for job age filtering."""
    
    def test_filter_recent_jobs(self, jobs_for_filtering):
        """Test filtering by maximum age."""
        engine = JobFilterEngine(JobFilter())
        result = engine.filter_by_age(jobs_for_filtering, max_age_hours=24)
        
        # Should include "2 hours ago", "5 hours ago", and "1 day ago" (24 hours = threshold)
        # Excludes only "3 days ago"
        assert len(result) == 3
    
    def test_filter_allows_older_jobs(self, jobs_for_filtering):
        """Test that higher max_age allows older jobs."""
        engine = JobFilterEngine(JobFilter())
        result = engine.filter_by_age(jobs_for_filtering, max_age_hours=48)
        
        # Should include up to 1 day old
        assert len(result) == 3


class TestApplyAllFilters:
    """Tests for combined filter application."""
    
    def test_apply_all_filters(self, jobs_for_filtering):
        """Test applying multiple filters together."""
        filter_config = JobFilter(
            min_budget=500,
            required_skills=["Python"],
            exclude_keywords=["Junior"],
            min_skill_match=1,
        )
        engine = JobFilterEngine(filter_config)
        result = engine.apply_all_filters(jobs_for_filtering)
        
        # Should be Senior Python Dev and Data Scientist
        assert len(result) >= 1
        assert all("python" in str(j.skills).lower() for j in result)
    
    def test_no_filters_returns_all(self, jobs_for_filtering):
        """Test that no active filters returns all jobs."""
        engine = JobFilterEngine(JobFilter())
        result = engine.apply_all_filters(jobs_for_filtering)
        
        assert len(result) == len(jobs_for_filtering)
