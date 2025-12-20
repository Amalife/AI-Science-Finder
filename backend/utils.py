from typing import List
from backend.external import giga


def get_embedding(text: str) -> List[float]:    
    embeddings = giga.embeddings(texts=[text])
    return embeddings.data[0].embedding