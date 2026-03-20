from urllib.parse import urlparse
import re
from datetime import datetime

DOMAINS = {
    'psx.com.pk': {"score": 0.95, "auth": "PSX Official"},
    'secp.gov.pk': {"score": 0.94, "auth": "SECP Official"},
    'dawn.com': {"score": 0.85, "auth": "Major News Source"},
    'tribune.com.pk': {"score": 0.82, "auth": "Major News Source"},
    'wsj.com': {"score": 0.85, "auth": "Global Financial News"},
    'bloomberg.com': {"score": 0.88, "auth": "Global Financial News"},
    'reuters.com': {"score": 0.88, "auth": "Global News Wire"},
    'brecorder.com': {"score": 0.85, "auth": "Financial News Domain"},
    'bloomberg.com.pk': {"score": 0.85, "auth": "Financial News Domain"},
    'twitter.com': {"score": 0.40, "auth": "Social Media"},
    'x.com': {"score": 0.40, "auth": "Social Media"},
    'facebook.com': {"score": 0.30, "auth": "Social Media"},
    'reddit.com': {"score": 0.40, "auth": "Social Media"}
}

class CredibilityScorer:
    @staticmethod
    def score_domain(url: str) -> dict:
        try:
            domain = urlparse(url).netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            
            # Check exact match First
            if domain in DOMAINS:
                return DOMAINS[domain]
            
            # Check ends with (for subdomains)
            for k, dict_val in DOMAINS.items():
                if domain.endswith(k):
                    return dict_val
                    
            # Default fallback for unknown domains
            if domain.endswith('.gov') or domain.endswith('.gov.pk') or domain.endswith('.edu'):
                return {"score": 0.90, "auth": "Government/Educational"}
            
            return {"score": 0.60, "auth": "General Domain"}
        except Exception:
            return {"score": 0.50, "auth": "Unknown Domain"}

    @staticmethod
    def score_recency(snippet: str) -> float:
        # Very basic mock recency scoring based on matching current year or recent dates 
        current_year = str(datetime.now().year)
        if current_year in snippet:
            return 0.90
        
        # Look for things like "2 days ago", "Mar 15, 2026", etc.
        recent_patterns = [r'\b(today|yesterday|just now|hours ago)\b', r'\b\d{1,2}\s+(days|hours|minutes)\s+ago\b']
        for pattern in recent_patterns:
            if re.search(pattern, snippet, re.IGNORECASE):
                return 0.98
                
        return 0.70 # Default recency if no dates are obvious

    @classmethod
    def score_source(cls, url: str, snippet: str) -> dict:
        d_res = cls.score_domain(url)
        r_score = cls.score_recency(snippet)
        return {
            "credibility_score": d_res["score"],
            "recency_score": r_score,
            "domain_authority": d_res["auth"]
        }
