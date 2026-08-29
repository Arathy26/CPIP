"""
Semantic Query Builder for Smart Job Matching
Converts target role + resume skills into rich search queries
"""

import re
from typing import List, Set


def normalize_role(target_role: str) -> str:
    """
    Normalize role for cache lookup.
    
    Examples:
        "Junior Backend Developer" → "backend_developer"
        "backend engineer" → "backend_developer"  
        "BACKEND" → "backend_developer"
        
    Same role, different spellings = SAME CACHE KEY
    """
    
    # Lowercase and strip
    normalized = target_role.lower().strip()
    
    # Remove titles (junior, senior, etc)
    titles_to_remove = ['junior', 'senior', 'sr', 'jr', 'intern', 'fresher', 
                        'engineer', 'developer', 'specialist', 'associate']
    
    for title in titles_to_remove:
        normalized = re.sub(rf'\b{title}\b', '', normalized)
    
    # Remove special characters
    normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
    
    # Clean up multiple spaces
    normalized = ' '.join(normalized.split())
    
    # Replace spaces with underscore
    normalized = normalized.replace(' ', '_')
    
    # Remove empty result
    if not normalized or normalized == '_':
        normalized = target_role.lower().replace(' ', '_')
    
    return normalized


def extract_domain_keywords(text: str) -> Set[str]:
    """
    Extract technical keywords from resume text.
    
    Returns set of keywords found in the text.
    """
    
    # Common technical keywords to look for
    tech_keywords = {
        "api", "rest", "graphql", "database", "sql", "nosql",
        "cloud", "aws", "azure", "gcp", "docker", "kubernetes",
        "microservices", "distributed", "scaling", "cache", "redis",
        "authentication", "security", "testing", "ci", "cd", "devops",
        "frontend", "backend", "fullstack", "react", "angular", "vue",
        "nodejs", "python", "java", "golang", "rust", "typescript",
        "fastapi", "django", "flask", "spring", "express", "rails",
        "postgresql", "mongodb", "mysql", "elasticsearch", "rabbitmq"
    }
    
    text_lower = text.lower()
    found_keywords = set()
    
    for keyword in tech_keywords:
        if keyword in text_lower:
            found_keywords.add(keyword)
    
    return found_keywords


def build_semantic_query(
    target_role: str,
    resume_skills: List[str],
    resume_text: str = ""
) -> str:
    """
    Build rich semantic search query for Active Jobs DB API.
    
    Input:
        target_role = "Junior Backend Developer"
        resume_skills = ["Python", "FastAPI", "SQL"]
        resume_text = "Built REST APIs with FastAPI..."
    
    Output:
        "backend developer python fastapi sql rest api"
    
    Logic:
    1. Extract role keywords (remove Jr/Sr/Intern)
    2. Add technical skills from resume
    3. Extract domain keywords from resume text
    4. Combine all keywords
    5. Return unified query for API
    
    This query is used to fetch jobs from Active Jobs DB.
    """
    
    # Step 1: Extract role keywords
    role_clean = target_role.lower().strip()
    role_clean = re.sub(r'(junior|senior|sr|jr|intern|fresher|engineer|developer)', '', role_clean)
    role_words = set(role_clean.split())
    role_words = {w for w in role_words if len(w) > 1}  # Remove single chars
    
    # Step 2: Add resume skills
    skill_words = set(s.lower() for s in resume_skills if s.strip() and len(s.strip()) > 1)
    
    # Step 3: Extract domain keywords from resume text
    domain_words = extract_domain_keywords(resume_text)
    
    # Step 4: Combine all
    all_keywords = role_words | skill_words | domain_words
    
    # Step 5: Create final query string (sorted for consistency)
    final_query = " ".join(sorted(list(all_keywords)))
    
    # Fallback: if query is empty, use target role
    if not final_query or len(final_query.split()) < 2:
        final_query = target_role
    
    print(f"📝 Semantic Query Built: {final_query}")
    
    return final_query


# Test it
if __name__ == "__main__":
    print("Testing normalize_role:")
    print(normalize_role("Junior Backend Developer"))  # backend_developer
    print(normalize_role("FRONTEND Engineer"))          # frontend
    
    print("\nTesting build_semantic_query:")
    query = build_semantic_query(
        target_role="Junior Backend Developer",
        resume_skills=["Python", "FastAPI", "SQL"],
        resume_text="Built REST APIs with FastAPI and PostgreSQL"
    )
    print(query)