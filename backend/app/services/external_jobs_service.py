"""
External Jobs Service — Adzuna API (Primary) + Fallback chain
"""

import os
import json
import requests
from groq import Groq


class ExternalJobsConfigError(Exception):
    pass


class ExternalJobsRequestError(Exception):
    pass


def search_adzuna_jobs(query: str, location: str = "india", max_results: int = 20):
    app_id = os.environ.get("ADZUNA_APP_ID")
    app_key = os.environ.get("ADZUNA_APP_KEY")

    if not app_id or not app_key:
        raise ExternalJobsConfigError("ADZUNA_APP_ID and ADZUNA_APP_KEY not set in .env")

    try:
        response = requests.get(
            "https://api.adzuna.com/v1/api/jobs/in/search/1",
            params={
                "app_id": app_id,
                "app_key": app_key,
                "results_per_page": max_results,
                "what": query,
                "content-type": "application/json",
            },
            timeout=30,
        )
    except requests.RequestException as e:
        raise ExternalJobsRequestError(f"Could not reach Adzuna API: {e}")

    if response.status_code != 200:
        raise ExternalJobsRequestError(
            f"Adzuna API returned status {response.status_code}: {response.text[:200]}"
        )

    payload = response.json()
    listings = payload.get("results", [])

    return [
        {
            "job_id": str(listing.get("id", "")),
            "title": listing.get("title", ""),
            "company": listing.get("company", {}).get("display_name", "Unknown"),
            "location": listing.get("location", {}).get("display_name", "India"),
            "apply_link": listing.get("redirect_url", ""),
            "posted_at": listing.get("created", ""),
            "is_remote": False,
            "employment_type": listing.get("contract_time", "Full-time"),
            "description": listing.get("description", ""),
            "source": "adzuna",
        }
        for listing in listings
        if isinstance(listing, dict)
    ]


def search_remotive_jobs(query: str, max_results: int = 20):
    try:
        response = requests.get(
            "https://remotive.com/api/remote-jobs",
            params={"search": query, "limit": max_results},
            timeout=30,
        )
        if response.status_code != 200:
            return []
        jobs = response.json().get("jobs", [])
        return [
            {
                "job_id": str(job.get("id", "")),
                "title": job.get("title", ""),
                "company": job.get("company_name", "Unknown"),
                "location": job.get("candidate_required_location", "Remote"),
                "apply_link": job.get("url", ""),
                "posted_at": job.get("publication_date", ""),
                "is_remote": True,
                "employment_type": job.get("job_type", "Full-time"),
                "description": job.get("description", ""),
                "source": "remotive",
            }
            for job in jobs
            if isinstance(job, dict)
        ]
    except Exception as e:
        print(f"Remotive fetch failed: {e}")
        return []


def search_external_jobs(query: str, location: str = "India", max_results: int = 20):
    try:
        listings = search_adzuna_jobs(query, location, max_results)
        if listings:
            print(f"Adzuna returned {len(listings)} jobs")
            return listings
    except Exception as e:
        print(f"Adzuna failed: {e}")

    print("Falling back to Remotive...")
    listings = search_remotive_jobs(query, max_results)
    print(f"Remotive returned {len(listings)} jobs")
    return listings


def extract_skills_from_text(text: str, target_role: str = "software engineer"):
    """
    Use Groq LLM to extract ONLY technical skills from job description.
    target_role helps LLM focus on relevant skills for that role.
    Temperature=0 prevents hallucination.
    """
    if not text or len(text.strip()) < 20:
        return []

    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0,
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"""Extract ONLY technical and programming skills from this job description.
Target role: {target_role}

Include ONLY:
- Programming languages (Python, Java, JavaScript, etc.)
- Frameworks and libraries (React, FastAPI, TensorFlow, etc.)
- Databases (SQL, MongoDB, PostgreSQL, etc.)
- Cloud platforms (AWS, Azure, GCP, etc.)
- DevOps tools (Docker, Kubernetes, CI/CD, etc.)
- AI/ML tools (PyTorch, scikit-learn, LangChain, etc.)
- Development tools (Git, Linux, REST APIs, etc.)

Exclude completely:
- Soft skills (communication, leadership, teamwork)
- Business skills (sales, marketing, accounting)
- Domain knowledge (finance, healthcare, education)
- Any non-technical skill

Return ONLY a JSON array of lowercase skill strings. No markdown. No explanation.

Job text:
{text[:1000]}

JSON array only:"""
            }]
        )
        skills = json.loads(response.choices[0].message.content)
        return [s.lower() for s in skills if isinstance(s, str)]
    except Exception as e:
        print(f"Skill extraction failed: {e}")
        return []


def fetch_market_skill_frequency(target_role: str, location: str = "India", max_postings: int = 25):
    """
    Full pipeline:
    1. Search jobs from Adzuna for target_role + location
    2. Extract ONLY technical skills from job descriptions using Groq
    3. Return frequency map for market cache
    """
    try:
        listings = search_external_jobs(
            query=target_role,
            location=location,
            max_results=max_postings
        )
    except Exception as e:
        print(f"Job fetch error: {e}")
        return {}, 0

    from app.data import seed_data
    skill_frequency = {}

    for listing in listings:
        job_id = listing.get("job_id")
        title = listing.get("title", "")
        company = listing.get("company", "")
        description = listing.get("description", "")

        # Check DB cache first
        cached = seed_data.get_cached_job_description(job_id) if job_id else None

        if cached:
            print(f"Cache hit for job {job_id}")
            skills = cached["skills_extracted"]
        else:
            # Extract ONLY technical skills using Groq LLM
            full_text = f"{title} {description}".strip()
            skills = extract_skills_from_text(full_text, target_role=target_role)  # ← pass role

            # Save to DB cache
            if job_id:
                seed_data.cache_job_description(
                    job_id=job_id,
                    title=title,
                    company=company,
                    description=description,
                    skills=skills
                )

        for skill in skills:
            skill_frequency[skill] = skill_frequency.get(skill, 0) + 1

    return skill_frequency, len(listings)