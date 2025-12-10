"""
Job filtering engine.
Filters scraped jobs based on various criteria.
"""

import re
from typing import Optional
from src.models.job import JobListing
from src.models.filters import JobFilter
from src.utils.logging import get_logger

logger = get_logger(__name__)


class JobFilterEngine:
    """
    Engine for filtering job listings based on criteria.
    
    Supports filtering by:
    - Budget range
    - Required skills
    - Keywords (include/exclude)
    - Client location
    - Job age
    """
    
    def __init__(self, filter_config: JobFilter):
        """
        Initialize filter engine.
        
        Args:
            filter_config: Filter criteria configuration
        """
        self.config = filter_config
    
    def _parse_time_to_hours(self, time_str: str) -> Optional[float]:
        """
        Parse posted time string to hours.
        
        Args:
            time_str: Time string like "2 hours ago", "1 day ago"
        
        Returns:
            Number of hours or None if parsing fails
        """
        if not time_str:
            return None
        
        time_str = time_str.lower().strip()
        
        patterns = [
            (r"(\d+)\s*minute", 1/60),
            (r"(\d+)\s*hour", 1),
            (r"(\d+)\s*day", 24),
            (r"(\d+)\s*week", 24 * 7),
            (r"(\d+)\s*month", 24 * 30),
        ]
        
        for pattern, multiplier in patterns:
            match = re.search(pattern, time_str)
            if match:
                return float(match.group(1)) * multiplier
        
        return None
    
    def filter_by_budget(
        self,
        jobs: list[JobListing],
        min_budget: Optional[float] = None,
        max_budget: Optional[float] = None,
    ) -> list[JobListing]:
        """
        Filter jobs by budget range.
        
        Args:
            jobs: List of jobs to filter
            min_budget: Minimum budget (inclusive)
            max_budget: Maximum budget (inclusive)
        
        Returns:
            Filtered list of jobs
        """
        if min_budget is None and max_budget is None:
            return jobs
        
        filtered = []
        for job in jobs:
            budget_value = job.budget_value
            
            # Include jobs without budget info (don't exclude them)
            if budget_value is None:
                filtered.append(job)
                continue
            
            # Apply range filter
            if min_budget is not None and budget_value < min_budget:
                continue
            if max_budget is not None and budget_value > max_budget:
                continue
            
            filtered.append(job)
        
        logger.debug(f"Budget filter: {len(jobs)} -> {len(filtered)} jobs")
        return filtered
    
    def filter_by_skills(
        self,
        jobs: list[JobListing],
        required_skills: list[str],
        min_match: int = 1,
    ) -> list[JobListing]:
        """
        Filter jobs by required skills.
        
        Args:
            jobs: List of jobs to filter
            required_skills: List of skills to look for
            min_match: Minimum number of skills that must match
        
        Returns:
            Filtered list of jobs
        """
        if not required_skills:
            return jobs
        
        # Normalize required skills for comparison
        required_lower = [s.lower().strip() for s in required_skills]
        
        filtered = []
        for job in jobs:
            # Normalize job skills
            job_skills_lower = [s.lower().strip() for s in job.skills]
            
            # Also check description for skills
            desc_lower = job.description.lower()
            title_lower = job.title.lower()
            
            matches = 0
            for skill in required_lower:
                if (
                    skill in job_skills_lower
                    or skill in desc_lower
                    or skill in title_lower
                ):
                    matches += 1
            
            if matches >= min_match:
                filtered.append(job)
        
        logger.debug(f"Skills filter: {len(jobs)} -> {len(filtered)} jobs")
        return filtered
    
    def filter_by_keywords(
        self,
        jobs: list[JobListing],
        include: list[str],
        exclude: list[str],
    ) -> list[JobListing]:
        """
        Filter jobs by keywords in title/description.
        
        Args:
            jobs: List of jobs to filter
            include: Keywords that must be present (any match)
            exclude: Keywords that must NOT be present (all excluded)
        
        Returns:
            Filtered list of jobs
        """
        filtered = []
        
        for job in jobs:
            text = f"{job.title} {job.description}".lower()
            
            # Check exclude keywords first
            excluded = False
            for keyword in exclude:
                if keyword.lower() in text:
                    excluded = True
                    break
            
            if excluded:
                continue
            
            # Check include keywords (if any specified)
            if include:
                included = False
                for keyword in include:
                    if keyword.lower() in text:
                        included = True
                        break
                
                if not included:
                    continue
            
            filtered.append(job)
        
        logger.debug(f"Keyword filter: {len(jobs)} -> {len(filtered)} jobs")
        return filtered
    
    def filter_by_location(
        self,
        jobs: list[JobListing],
        whitelist: list[str],
        blacklist: list[str],
    ) -> list[JobListing]:
        """
        Filter jobs by client location.
        
        Args:
            jobs: List of jobs to filter
            whitelist: Allowed locations (if empty, all allowed)
            blacklist: Excluded locations
        
        Returns:
            Filtered list of jobs
        """
        filtered = []
        
        for job in jobs:
            location = (job.client_location or "").lower()
            
            # Check blacklist
            blacklisted = False
            for loc in blacklist:
                if loc.lower() in location:
                    blacklisted = True
                    break
            
            if blacklisted:
                continue
            
            # Check whitelist (if specified)
            if whitelist:
                whitelisted = False
                for loc in whitelist:
                    if loc.lower() in location:
                        whitelisted = True
                        break
                
                # If whitelist exists but location doesn't match, exclude
                # unless location is unknown
                if not whitelisted and location:
                    continue
            
            filtered.append(job)
        
        logger.debug(f"Location filter: {len(jobs)} -> {len(filtered)} jobs")
        return filtered
    
    def filter_by_age(
        self,
        jobs: list[JobListing],
        max_age_hours: Optional[int],
    ) -> list[JobListing]:
        """
        Filter jobs by posting age.
        
        Args:
            jobs: List of jobs to filter
            max_age_hours: Maximum age in hours
        
        Returns:
            Filtered list of jobs
        """
        if max_age_hours is None:
            return jobs
        
        filtered = []
        for job in jobs:
            age_hours = self._parse_time_to_hours(job.posted_time)
            
            # Include if age unknown or within range
            if age_hours is None or age_hours <= max_age_hours:
                filtered.append(job)
        
        logger.debug(f"Age filter: {len(jobs)} -> {len(filtered)} jobs")
        return filtered
    
    def apply_all_filters(self, jobs: list[JobListing]) -> list[JobListing]:
        """
        Apply all configured filters in sequence.
        
        Args:
            jobs: List of jobs to filter
        
        Returns:
            Filtered list of jobs
        """
        if not self.config.has_any_filter():
            logger.info("No filters configured, returning all jobs")
            return jobs
        
        logger.info(f"Applying filters to {len(jobs)} jobs")
        
        result = jobs
        
        # Apply each filter
        result = self.filter_by_budget(
            result,
            self.config.min_budget,
            self.config.max_budget,
        )
        
        result = self.filter_by_skills(
            result,
            self.config.required_skills,
            self.config.min_skill_match,
        )
        
        result = self.filter_by_keywords(
            result,
            self.config.include_keywords,
            self.config.exclude_keywords,
        )
        
        result = self.filter_by_location(
            result,
            self.config.location_whitelist,
            self.config.location_blacklist,
        )
        
        result = self.filter_by_age(
            result,
            self.config.max_age_hours,
        )
        
        logger.info(f"Filtering complete: {len(jobs)} -> {len(result)} jobs")
        return result
