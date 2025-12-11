"""
Cover letter generator using LangChain.
Generates personalized cover letters for Upwork job applications.
Supports both OpenAI and Google Gemini models.
"""

import asyncio
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

from src.models.job import JobListing
from src.models.profile import UserProfile
from src.ai.prompts import get_cover_letter_prompt, format_job_for_prompt
from src.utils.logging import get_logger

logger = get_logger(__name__)


class CoverLetterGenerator:
    """
    Generates personalized cover letters using LangChain and LLMs.
    
    Supports both OpenAI (GPT) and Google Gemini models.
    Uses the user's profile and job details to create tailored
    cover letters for each job application.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-flash",
        profile: Optional[UserProfile] = None,
        provider: str = "gemini",  # "openai" or "gemini"
    ):
        """
        Initialize the generator.
        
        Args:
            api_key: API key (OpenAI or Google)
            model: LLM model to use
            profile: User profile for personalization
            provider: "openai" or "gemini"
        """
        self.profile = profile
        self.model = model
        self.provider = provider.lower()
        
        # Initialize LangChain components based on provider
        if self.provider == "gemini":
            self.llm = ChatGoogleGenerativeAI(
                google_api_key=api_key,
                model=model,
                temperature=0.7,  # Some creativity for personalization
                max_output_tokens=500,  # Keep responses concise
            )
            logger.info(f"CoverLetterGenerator initialized with Google Gemini: {model}")
        elif self.provider == "openai":
            self.llm = ChatOpenAI(
                api_key=api_key,
                model=model,
                temperature=0.7,
                max_tokens=500,
            )
            logger.info(f"CoverLetterGenerator initialized with OpenAI: {model}")
        else:
            raise ValueError(f"Unsupported provider: {provider}. Use 'openai' or 'gemini'")
        
        self.prompt = get_cover_letter_prompt()
        self.chain = self.prompt | self.llm | StrOutputParser()

    
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
    api_key: str,
    profile_path: str,
    model: str = "gemini-1.5-flash",
    provider: str = "gemini",
) -> CoverLetterGenerator:
    """
    Factory function to create a configured generator.
    
    Args:
        api_key: API key (OpenAI or Google Gemini)
        profile_path: Path to user profile YAML/TXT file
        model: LLM model to use
        provider: "openai" or "gemini"
    
    Returns:
        Configured CoverLetterGenerator
    """
    # Load profile
    profile = UserProfile.load(profile_path)
    logger.info(f"Loaded profile for: {profile.name}")
    
    # Create generator
    generator = CoverLetterGenerator(
        api_key=api_key,
        model=model,
        profile=profile,
        provider=provider,
    )
    
    return generator
