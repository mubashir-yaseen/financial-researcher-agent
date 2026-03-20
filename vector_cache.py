import os
import json
import numpy as np
import faiss
from typing import Optional, Dict

class VectorCache:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.index_path = os.path.join(cache_dir, "index.faiss")
        self.metadata_path = os.path.join(cache_dir, "metadata.json")
        self.model = None
        self.index = None
        self.metadata = []
        self.dimension = 384
        self.enabled = False

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        # Lazy load the model to avoid crashing on init if offline
        self._init_resources()

    def _init_resources(self):
        try:
            from sentence_transformers import SentenceTransformer
            # Using a very small model as requested
            self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, 'r') as f:
                    self.metadata = json.load(f)
            else:
                # Use Inner Product for cosine similarity (requires normalization)
                self.index = faiss.IndexFlatIP(self.dimension)
            
            self.enabled = True
        except Exception as e:
            print(f"Warning: Semantic cache disabled: {e}")
            self.enabled = False

    def add(self, query: str, response: Dict):
        if not self.enabled:
            return
            
        try:
            vector = self.model.encode([query])[0]
            # Normalize vector for cosine similarity
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
                
            self.index.add(np.array([vector]).astype('float32'))
            self.metadata.append(response)
            
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f)
        except Exception as e:
            print(f"Cache write error: {e}")

    def get_similar(self, query: str, threshold: float = 0.95) -> Optional[Dict]:
        """
        Returns cached response if cosine similarity > threshold.
        """
        if not self.enabled or self.index.ntotal == 0:
            return None
            
        try:
            vector = self.model.encode([query])[0]
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
                
            D, I = self.index.search(np.array([vector]).astype('float32'), 1)
            
            # IndexFlatIP distance is dot product. With normalized vectors, it's cosine similarity.
            if D[0][0] > threshold:
                print(f"Cache hit! Similarity: {D[0][0]:.4f}")
                return self.metadata[I[0][0]]
        except Exception as e:
            print(f"Cache read error: {e}")
            
        return None
