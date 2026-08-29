"""
Semantic Skill Matcher - LAZY LOADING FIX
"""

import logging

logger = logging.getLogger(__name__)

# Global instance - loaded on first use, not at import time
_matcher_instance = None


class SemanticSkillMatcher:
    def __init__(self):
        try:
            from sentence_transformers import SentenceTransformer
            # Fast, lightweight model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.threshold = 0.55
            self.cache = {}  # Cache embeddings
            logger.info("✅ SemanticSkillMatcher initialized")
        except Exception as e:
            logger.error(f"❌ Failed to load SemanticSkillMatcher: {e}")
            self.model = None
    
    def embed_skill(self, skill):
        """Convert skill text to vector"""
        if not self.model:
            return None
        
        if skill in self.cache:
            return self.cache[skill]
        try:
            embedding = self.model.encode(skill)
            self.cache[skill] = embedding
            return embedding
        except Exception as e:
            logger.error(f"Error embedding skill '{skill}': {e}")
            return None
    
    def semantic_match(self, resume_skill, job_skill):
        """Compare two skills semantically (0-1, where 1=exact match)"""
        if not self.model:
            return 0
        
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            resume_emb = self.embed_skill(resume_skill)
            job_emb = self.embed_skill(job_skill)
            
            if resume_emb is None or job_emb is None:
                return 0
            
            similarity = cosine_similarity([resume_emb], [job_emb])[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error in semantic_match: {e}")
            return 0
    
    def find_best_match(self, resume_skill, job_skills):
        """Find best matching job skill for a resume skill"""
        if not self.model or not job_skills:
            return None, 0
        
        try:
            import numpy as np
            scores = [self.semantic_match(resume_skill, js) for js in job_skills]
            best_idx = np.argmax(scores)
            best_score = scores[best_idx]
            
            if best_score >= self.threshold:
                return job_skills[best_idx], best_score
            return None, best_score
        except Exception as e:
            logger.error(f"Error in find_best_match: {e}")
            return None, 0


def get_matcher() -> SemanticSkillMatcher:
    """Get matcher instance (lazy load on first use)"""
    global _matcher_instance
    if _matcher_instance is None:
        _matcher_instance = SemanticSkillMatcher()
    return _matcher_instance


# For backward compatibility
matcher = None  # Will be loaded on first use


def __getattr__(name):
    """Lazy load matcher on first access"""
    global matcher
    if name == 'matcher':
        if matcher is None:
            matcher = get_matcher()
        return matcher
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")