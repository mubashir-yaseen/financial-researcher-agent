from typing import List
from pydantic import BaseModel, Field
from datetime import datetime

class Source(BaseModel):
    title: str
    url: str
    domain_authority: str = "Unknown"
    credibility_score: float = 0.0
    recency_score: float = 0.0

class Metrics(BaseModel):
    total_sources: int = 0
    high_confidence_sources: int = 0
    confidence_score: float = 0.0

class ResearchOutput(BaseModel):
    query: str
    timestamp: datetime = Field(default_factory=datetime.now)
    sources: List[Source] = []
    key_facts: List[str] = []
    metrics: Metrics = Metrics()
    next_action: str = "complete"
