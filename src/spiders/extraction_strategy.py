"""
Extraction strategies for Upwork job listings.
Defines CSS selectors and LLM extraction schemas.
"""

from crawl4ai.extraction_strategy import (
    JsonCssExtractionStrategy,
    LLMExtractionStrategy,
)

# CSS selectors for Upwork job cards
# Note: These selectors may need updates if Upwork changes their HTML structure
UPWORK_JOB_CARD_SCHEMA = {
    "name": "Upwork Job Listings",
    "baseSelector": "article[data-test='job-tile'], section.job-tile, div[data-test='JobTile']",
    "fields": [
        {
            "name": "title",
            "selector": "h2 a, h3 a, [data-test='job-title-link'], .job-title-link",
            "type": "text"
        },
        {
            "name": "description",
            "selector": "[data-test='job-description-text'], .job-description, p.mb-0",
            "type": "text"
        },
        {
            "name": "budget",
            "selector": "[data-test='budget'], .job-budget, [data-test='is-fixed-price'] + span",
            "type": "text"
        },
        {
            "name": "hourly_rate",
            "selector": "[data-test='hourly-rate'], [data-test='is-hourly'] + span",
            "type": "text"
        },
        {
            "name": "client_location",
            "selector": "[data-test='client-location'], .client-location, [data-test='location']",
            "type": "text"
        },
        {
            "name": "posted_time",
            "selector": "[data-test='posted-on'], .job-posted-on, time, [data-test='job-pubished-date']",
            "type": "text"
        },
        {
            "name": "job_url",
            "selector": "h2 a, h3 a, [data-test='job-title-link'], a.job-title-link",
            "type": "attribute",
            "attribute": "href"
        },
        {
            "name": "skills",
            "selector": "[data-test='token'], .skill-tag, .air3-token, span.skill",
            "type": "list"
        }
    ]
}


def create_css_extraction_strategy() -> JsonCssExtractionStrategy:
    """
    Create CSS-based extraction strategy for Upwork jobs.
    
    This is the primary extraction method - faster and more reliable
    when selectors match.
    
    Returns:
        Configured JsonCssExtractionStrategy
    """
    return JsonCssExtractionStrategy(
        schema=UPWORK_JOB_CARD_SCHEMA,
        verbose=False
    )


def create_llm_extraction_strategy(
    api_key: str,
    model: str = "gpt-4o-mini"
) -> LLMExtractionStrategy:
    """
    Create LLM-based extraction strategy for Upwork jobs.
    
    Use this as fallback when CSS selectors fail (e.g., after
    Upwork updates their HTML structure).
    
    Args:
        api_key: OpenAI API key
        model: LLM model to use
    
    Returns:
        Configured LLMExtractionStrategy
    """
    extraction_schema = {
        "type": "object",
        "properties": {
            "jobs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Job title"},
                        "description": {"type": "string", "description": "Job description"},
                        "budget": {"type": "string", "description": "Fixed price budget if any"},
                        "hourly_rate": {"type": "string", "description": "Hourly rate range if any"},
                        "client_location": {"type": "string", "description": "Client location/country"},
                        "posted_time": {"type": "string", "description": "When the job was posted"},
                        "job_url": {"type": "string", "description": "URL to the job posting"},
                        "skills": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Required skills"
                        }
                    },
                    "required": ["title", "description"]
                }
            }
        }
    }
    
    return LLMExtractionStrategy(
        provider="openai",
        api_token=api_key,
        model=model,
        schema=extraction_schema,
        instruction="""
        Extract all job listings from this Upwork search results page.
        For each job, extract:
        - title: The job title
        - description: Full job description text
        - budget: Fixed price budget (e.g., "$500") or null if hourly
        - hourly_rate: Hourly rate range (e.g., "$25-$50/hr") or null if fixed
        - client_location: The client's country/location
        - posted_time: When posted (e.g., "2 hours ago")
        - job_url: The URL/link to the job posting
        - skills: List of required skills/tags
        
        Return all jobs found on the page.
        """,
        verbose=False
    )
