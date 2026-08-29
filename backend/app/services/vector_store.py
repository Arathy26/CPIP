"""
CPIP Vector Store
ChromaDB for semantic job search
"""

import chromadb
from chromadb.utils import embedding_functions
import os
import json

# Setup ChromaDB
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, "..", "..", "chroma_db")

client = chromadb.PersistentClient(path=CHROMA_PATH)

# Use sentence-transformers for embeddings (free, no API needed)
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Job collection
job_collection = client.get_or_create_collection(
    name="cpip_jobs",
    embedding_function=embedding_fn,
)


def add_job_to_vector_store(job: dict):
    """Add a job to ChromaDB for semantic search."""
    job_text = f"""
    {job['job_title']} at {job['company_name']} in {job['location']}.
    Required skills: {', '.join(job.get('required_skills', []))}.
    Preferred skills: {', '.join(job.get('preferred_skills', []))}.
    Experience: {job.get('experience_level', 'Not specified')}.
    """

    job_collection.upsert(
        ids=[str(job["id"])],
        documents=[job_text],
        metadatas=[{
            "job_id": job["id"],
            "job_title": job["job_title"],
            "company_name": job["company_name"],
            "location": job["location"],
            "required_skills": json.dumps(job.get("required_skills", [])),
            "preferred_skills": json.dumps(job.get("preferred_skills", [])),
            "experience_level": job.get("experience_level", ""),
        }]
    )


def semantic_search_jobs(query: str, n_results: int = 5):
    """Search jobs by meaning, not just keywords."""
    try:
        results = job_collection.query(
            query_texts=[query],
            n_results=min(n_results, job_collection.count()),
        )

        if not results or not results["ids"][0]:
            return []

        jobs = []
        for i, job_id in enumerate(results["ids"][0]):
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i]
            similarity = round((1 - distance) * 100, 1)

            jobs.append({
                "job_id": int(job_id),
                "job_title": metadata["job_title"],
                "company_name": metadata["company_name"],
                "location": metadata["location"],
                "required_skills": json.loads(metadata["required_skills"]),
                "preferred_skills": json.loads(metadata["preferred_skills"]),
                "experience_level": metadata["experience_level"],
                "semantic_similarity": similarity,
            })

        return jobs

    except Exception as e:
        print(f"Semantic search error: {e}")
        return []


def get_job_count():
    """Returns number of jobs in vector store."""
    return job_collection.count()