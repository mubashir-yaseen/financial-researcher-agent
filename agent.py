import os
import json
from openai import OpenAI
from typing import Dict, Any
from models import ResearchOutput, Source, Metrics
from free_search import FreeSearch
from scorer import CredibilityScorer
from vector_cache import VectorCache

class ResearcherAgent:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.searcher = FreeSearch()
        self.cache = VectorCache()
        
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1"
            )
        else:
            self.client = None
            
        self.model = os.getenv("LLM_MODEL", "meta-llama/llama-3.3-70b-instruct:free")

    def run(self, query: str) -> dict:
        """
        Execute full research workflow: Cache -> Search -> Score -> LLM.
        """
        # 1. Check Cache
        cached = self.cache.get_similar(query)
        if cached:
            return cached
            
        # 2. Search
        raw_results = self.searcher.search(query, max_results=8)
        
        sources = []
        context_texts = []
        high_conf_count = 0
        
        for r in raw_results:
            scores = CredibilityScorer.score_source(r['url'], r['snippet'])
            source_obj = Source(
                title=r['title'],
                url=r['url'],
                domain_authority=scores['domain_authority'],
                credibility_score=scores['credibility_score'],
                recency_score=scores['recency_score']
            )
            sources.append(source_obj)
            
            if scores['credibility_score'] >= 0.8:
                high_conf_count += 1
                
            context_texts.append(f"Title: {r['title']}\nSnippet: {r['snippet']}\nURL: {r['url']}")
            
        # If no results found
        if not sources:
            return ResearchOutput(
                query=query,
                key_facts=["No relevant sources found for this query."],
                metrics=Metrics(total_sources=0, confidence_score=0.0),
                next_action="human_review"
            ).model_dump(mode='json')

        # 3. Call LLM for fact extraction
        context_str = "\n\n".join(context_texts)
        prompt = f"""
        Analyze these search results for the query: "{query}"
        
        Search Results:
        {context_str}
        
        Extract:
        1. 3-5 key facts (concise, data-driven)
        2. Overall confidence score (0-1) based on source credibility and agreement.
        
        Respond ONLY with raw JSON in this format:
        {{
            "key_facts": ["fact1", "fact2", ...],
            "confidence_score": 0.92
        }}
        """
        
        try:
            analysis = self._call_llm(prompt)
            
            metrics = Metrics(
                total_sources=len(sources),
                high_confidence_sources=high_conf_count,
                confidence_score=analysis.get("confidence_score", 0.0)
            )
            
            output = ResearchOutput(
                query=query,
                sources=sources,
                key_facts=analysis.get("key_facts", []),
                metrics=metrics,
                next_action="complete"
            )
            
            final_dict = output.model_dump(mode='json')
            
            # 4. Cache result
            self.cache.add(query, final_dict)
            
            return final_dict
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                error_msg = "OpenRouter Free Tier rate-limited. Please retry in 60s or switch to a different free model in .env."
            
            print(f"Agent Error: {error_msg}")
            return ResearchOutput(
                query=query,
                sources=sources,
                key_facts=[f"Error during analysis: {error_msg}"],
                metrics=Metrics(total_sources=len(sources), confidence_score=0.0),
                next_action="retry"
            ).model_dump(mode='json')

    def _call_llm(self, prompt: str) -> dict:
        if not self.client:
            raise Exception("OpenRouter API key not configured.")
            
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean potential markdown code blocks
        if content.startswith("```"):
            import re
            content = re.sub(r"```json\s?|\s?```", "", content, flags=re.MULTILINE)
            
        return json.loads(content)
