"""
LangChain prompt templates for cover letter generation.
"""

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate


SYSTEM_PROMPT = """You are an expert freelance proposal writer. Your job is to write compelling, 
personalized cover letters for Upwork job applications.

Guidelines:
1. Be professional but personable - show genuine interest in the project
2. Open with a hook that shows you understand the client's needs
3. Briefly highlight 2-3 most relevant skills/experiences for THIS specific job
4. Include a concrete example or achievement when relevant
5. End with a clear call to action
6. Keep it concise (150-200 words max)
7. Avoid generic phrases like "I am the perfect candidate"
8. Match the tone specified: {tone}

DO NOT:
- Start with "Dear Hiring Manager" or similar generic greetings
- List all skills - only mention what's relevant
- Make the letter too long
- Sound like a template - personalize for each job"""

HUMAN_PROMPT = """Write a cover letter for this Upwork job application.

## JOB DETAILS
Title: {job_title}
Description: {job_description}
Required Skills: {job_skills}
Budget: {job_budget}

## MY PROFILE
{profile_context}

## INSTRUCTIONS
Write a compelling cover letter that:
1. Shows I understand the client's needs based on the job description
2. Highlights my most relevant experience from my profile
3. Is tailored specifically to this job, not generic
4. Uses a {tone} tone

Cover Letter:"""


def get_cover_letter_prompt() -> ChatPromptTemplate:
    """
    Get the ChatPromptTemplate for cover letter generation.
    
    Returns:
        Configured ChatPromptTemplate
    """
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(HUMAN_PROMPT),
    ])


def format_job_for_prompt(job) -> dict:
    """
    Format job listing for prompt template.
    
    Args:
        job: JobListing object
    
    Returns:
        Dictionary with formatted job fields
    """
    return {
        "job_title": job.title,
        "job_description": job.description[:1500],  # Limit description length
        "job_skills": ", ".join(job.skills) if job.skills else "Not specified",
        "job_budget": job.budget or job.hourly_rate or "Not specified",
    }
