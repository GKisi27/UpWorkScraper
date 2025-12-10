"""
Cover letter generator using LangChain.
Generates personalized cover letters for Upwork job applications.
"""

import asyncio
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from src.models.job import JobListing
from src.models.profile import UserProfile
from src.ai.prompts import get_cover_letter_prompt, format_job_for_prompt
from src.utils.logging import get_logger

logger = get_logger(__name__)


class CoverLetterGenerator:
    """
    Generates personalized cover letters using LangChain and OpenAI.
    
    Uses the user's profile and job details to create tailored
    cover letters for each job application.
    """
    
    def __init__(
        self,
        openai_api_key: str,
        model: str = "gpt-4o-mini",
        profile: Optional[UserProfile] = None,
    ):
        """
        Initialize the generator.
        
        Args:
            openai_api_key: OpenAI API key
            model: LLM model to use
            profile: User profile for personalization
        """
        self.profile = profile
        self.model = model
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model=model,
            temperature=0.7,  # Some creativity for personalization
            max_tokens=500,   # Keep responses concise
        )
        
        self.prompt = get_cover_letter_prompt()
        self.chain = self.prompt | self.llm | StrOutputParser()
        
        logger.info(f"CoverLetterGenerator initialized with model: {model}")
    
    def set_profile(self, profile: UserProfile) -> None:
        """
        Set or update the user profile.
        
        Args:
            profile: User profile for personalization
        """
        self.profile = profile
        logger.info(f"Profile set for: {profile.name}")
    
    async def generate(self, job: JobListing) -> str:
        """
        Generate a cover letter for a specific job.
        
        Args:
            job: Job listing to generate cover letter for
        
        Returns:
            Generated cover letter text
        
        Raises:
            ValueError: If profile is not set
        """
        if self.profile is None:
            raise ValueError("User profile must be set before generating cover letters")
        
        logger.debug(f"Generating cover letter for: {job.title}")
        
        # Format inputs for prompt
        job_data = format_job_for_prompt(job)
        
        inputs = {
            **job_data,
            "profile_context": self.profile.to_prompt_context(),
            "tone": self.profile.tone,
        }
        
        try:
            # Generate using LangChain
            cover_letter = await self.chain.ainvoke(inputs)
            
            # Clean up the response
            cover_letter = cover_letter.strip()
            
            logger.debug(f"Generated cover letter ({len(cover_letter)} chars)")
            return cover_letter
            
        except Exception as e:
            logger.error(f"Failed to generate cover letter: {e}")
            raise
    
    async def generate_batch(
        self,
        jobs: list[JobListing],
        delay_between: float = 1.0,
    ) -> list[JobListing]:
        """
        Generate cover letters for multiple jobs.
        
        Updates each job's cover_letter field in place.
        
        Args:
            jobs: List of job listings
            delay_between: Delay between API calls (rate limiting)
        
        Returns:
            List of jobs with cover letters populated
        """
        if not jobs:
            return jobs
        
        logger.info(f"Generating cover letters for {len(jobs)} jobs")
        
        for i, job in enumerate(jobs):
            try:
                cover_letter = await self.generate(job)
                # Update the job object (Pydantic model)
                object.__setattr__(job, 'cover_letter', cover_letter)
                
                logger.info(f"Generated cover letter {i+1}/{len(jobs)}: {job.title[:50]}...")
                
                # Rate limiting
                if i < len(jobs) - 1:
                    await asyncio.sleep(delay_between)
                    
            except Exception as e:
                logger.error(f"Failed to generate for job '{job.title}': {e}")
                continue
        
        # Count successful generations
        success_count = sum(1 for j in jobs if j.cover_letter)
        logger.info(f"Cover letter generation complete: {success_count}/{len(jobs)} successful")
        
        return jobs


async def create_cover_letter_generator(
    openai_api_key: str,
    profile_path: str,
    model: str = "gpt-4o-mini",
) -> CoverLetterGenerator:
    """
    Factory function to create a configured generator.
    
    Args:
        openai_api_key: OpenAI API key
        profile_path: Path to user profile YAML/TXT file
        model: LLM model to use
    
    Returns:
        Configured CoverLetterGenerator
    """
    # Load profile
    profile = UserProfile.load(profile_path)
    logger.info(f"Loaded profile for: {profile.name}")
    
    # Create generator
    generator = CoverLetterGenerator(
        openai_api_key=openai_api_key,
        model=model,
        profile=profile,
    )
    
    return generator
