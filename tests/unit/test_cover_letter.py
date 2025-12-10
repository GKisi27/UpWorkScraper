"""
Unit tests for cover letter generation.
Tests prompt construction and generator initialization (mocked LLM responses).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.models.job import JobListing
from src.models.profile import UserProfile
from src.ai.prompts import get_cover_letter_prompt, format_job_for_prompt
from src.ai.cover_letter_generator import CoverLetterGenerator


class TestPrompts:
    """Tests for prompt template construction."""
    
    def test_get_prompt_template(self):
        """Test getting the cover letter prompt template."""
        prompt = get_cover_letter_prompt()
        
        assert prompt is not None
        # Should have system and human messages
        assert len(prompt.messages) == 2
    
    def test_format_job_for_prompt(self, sample_jobs):
        """Test formatting job data for prompt."""
        job = sample_jobs[0]
        formatted = format_job_for_prompt(job)
        
        assert "job_title" in formatted
        assert "job_description" in formatted
        assert "job_skills" in formatted
        assert "job_budget" in formatted
        
        assert formatted["job_title"] == job.title
    
    def test_format_job_truncates_long_description(self):
        """Test that long descriptions are truncated."""
        job = JobListing(
            title="Test Job",
            description="A" * 2000,  # Very long description
            posted_time="1 hour ago",
            job_url="https://www.upwork.com/jobs/~012345",
        )
        formatted = format_job_for_prompt(job)
        
        assert len(formatted["job_description"]) <= 1500
    
    def test_format_job_handles_missing_budget(self):
        """Test formatting when budget is not specified."""
        job = JobListing(
            title="Test Job",
            description="Test",
            posted_time="1 hour ago",
            job_url="https://www.upwork.com/jobs/~012345",
            # No budget or hourly_rate
        )
        formatted = format_job_for_prompt(job)
        
        assert formatted["job_budget"] == "Not specified"
    
    def test_format_job_skills_as_string(self, sample_jobs):
        """Test that skills are formatted as comma-separated string."""
        job = sample_jobs[0]
        formatted = format_job_for_prompt(job)
        
        assert ", " in formatted["job_skills"]


class TestCoverLetterGenerator:
    """Tests for cover letter generator."""
    
    def test_initialization(self):
        """Test generator initialization."""
        generator = CoverLetterGenerator(
            openai_api_key="test-key",
            model="gpt-4o-mini",
        )
        
        assert generator.model == "gpt-4o-mini"
        assert generator.profile is None
    
    def test_set_profile(self, sample_profile_yaml):
        """Test setting user profile."""
        profile = UserProfile.from_yaml(sample_profile_yaml)
        
        generator = CoverLetterGenerator(
            openai_api_key="test-key",
            model="gpt-4o-mini",
        )
        generator.set_profile(profile)
        
        assert generator.profile is not None
        assert generator.profile.name == "Test User"
    
    @pytest.mark.asyncio
    async def test_generate_requires_profile(self, sample_jobs):
        """Test that generate raises error without profile."""
        generator = CoverLetterGenerator(
            openai_api_key="test-key",
            model="gpt-4o-mini",
        )
        
        with pytest.raises(ValueError, match="profile must be set"):
            await generator.generate(sample_jobs[0])
    
    @pytest.mark.asyncio
    async def test_generate_with_mocked_llm(self, sample_jobs, sample_profile_yaml):
        """Test generation with mocked LLM response."""
        profile = UserProfile.from_yaml(sample_profile_yaml)
        
        # Create generator with mocked chain
        generator = CoverLetterGenerator(
            openai_api_key="test-key",
            model="gpt-4o-mini",
            profile=profile,
        )
        
        # Mock the chain's ainvoke method
        mock_response = "Dear Hiring Manager, I am excited about this opportunity..."
        generator.chain = MagicMock()
        generator.chain.ainvoke = AsyncMock(return_value=mock_response)
        
        result = await generator.generate(sample_jobs[0])
        
        assert result == mock_response.strip()
        generator.chain.ainvoke.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_batch_with_mocked_llm(self, sample_jobs, sample_profile_yaml):
        """Test batch generation with mocked LLM."""
        profile = UserProfile.from_yaml(sample_profile_yaml)
        
        generator = CoverLetterGenerator(
            openai_api_key="test-key",
            model="gpt-4o-mini",
            profile=profile,
        )
        
        # Mock chain
        generator.chain = MagicMock()
        generator.chain.ainvoke = AsyncMock(return_value="Cover letter content")
        
        # Use short delay for testing
        result = await generator.generate_batch(sample_jobs[:2], delay_between=0.01)
        
        assert len(result) == 2
        # Each job should have a cover letter
        assert all(j.cover_letter is not None for j in result)
    
    @pytest.mark.asyncio
    async def test_generate_handles_errors_gracefully(self, sample_jobs, sample_profile_yaml):
        """Test that errors don't stop batch processing."""
        profile = UserProfile.from_yaml(sample_profile_yaml)
        
        generator = CoverLetterGenerator(
            openai_api_key="test-key",
            model="gpt-4o-mini",
            profile=profile,
        )
        
        # Mock chain to fail on first call, succeed on second
        generator.chain = MagicMock()
        generator.chain.ainvoke = AsyncMock(
            side_effect=[
                Exception("API Error"),
                "Success cover letter",
            ]
        )
        
        result = await generator.generate_batch(sample_jobs[:2], delay_between=0.01)
        
        # Should still return 2 jobs, but first might not have cover letter
        assert len(result) == 2


class TestProfileContext:
    """Tests for profile context generation."""
    
    def test_full_profile_context(self, sample_profile_yaml):
        """Test profile context includes all relevant info."""
        profile = UserProfile.from_yaml(sample_profile_yaml)
        context = profile.to_prompt_context()
        
        assert profile.name in context
        assert profile.title in context
        assert str(profile.years_experience) in context
        assert "Python" in context  # One of the skills
    
    def test_profile_with_achievements(self, sample_profile_yaml):
        """Test that achievements are included in context."""
        profile = UserProfile.from_yaml(sample_profile_yaml)
        context = profile.to_prompt_context()
        
        if profile.achievements:
            assert "•" in context  # Bullet points
