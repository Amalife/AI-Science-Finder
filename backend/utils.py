from typing import List
from config.config import configuration
from backend.external import giga, hf_model


def get_embedding(text: str) -> List[float]:
    if configuration.use_hf_embedder:
        return hf_model.encode(text).tolist()
    else:
        embeddings = giga.embeddings(texts=[text])
        return embeddings.data[0].embedding