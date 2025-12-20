from pydantic import BaseModel
from typing import List, Optional


class ArticleMetadata(BaseModel):
    author: str
    published_date: str
    tags: List[str]

class Article(BaseModel):
    title: str
    url: str
    abstract: str
    metadata: ArticleMetadata

class SearchRequest(BaseModel):
    query: str
    author_filter: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    top_k: int = 5

class SearchResult(BaseModel):
    id: str
    title: str
    url: str
    abstract: str
    similarity_score: float
    metadata: ArticleMetadata