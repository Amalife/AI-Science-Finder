from fastapi import APIRouter, HTTPException
from backend.utils import get_embedding
from backend.external import es_client
from backend.model import SearchRequest, SearchResult, Article
from typing import List
from logger.logger import back_logger


router = APIRouter()


@router.post("/ingest")
async def ingest_article(article: Article):
    """Добавление статьи в базу (для наполнения)"""
    try:
        # Векторизуем объединение заголовка и аннотации
        text_to_embed = f"{article.title} {article.abstract}"
        vector = get_embedding(text_to_embed)
        
        doc = article.model_dump()
        doc["vector"] = vector
        
        await es_client.index(index="scientific_articles", document=doc)
        return {"status": "success", "message": f"Статья '{article.title}' добавлена."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=List[SearchResult])
async def search_articles(request: SearchRequest):
    try:
        # Перевод запроса в эмбеддинг
        back_logger.info(f"Received search query: {request.query}")
        query_vector = get_embedding(request.query)
        
        # Формирование запроса к ES
        filter_clauses = []

        # Фильтры
        if request.author_filter:
            filter_clauses.append({"wildcard": {"metadata.author": f"*{request.author_filter.strip().lower()}*"}})
            back_logger.info(f"Applying author filter: {request.author_filter}")
        
        if request.date_from or request.date_to:
            range_query = {}
            if request.date_from:
                range_query["gte"] = request.date_from
            if request.date_to:
                range_query["lte"] = request.date_to
            filter_clauses.append({"range": {"metadata.published_date": range_query}})
            back_logger.info(f"Applying date range filter: {range_query}")

        if request.tags_filter:
            filter_clauses.append({"term": {"metadata.tags": f"{request.tags_filter.strip().lower()}"}})
            back_logger.info(f"Applying tags filter: {request.tags_filter}")

        # Построение KNN запроса
        knn_query = {
            "field": "vector",
            "query_vector": query_vector,
            "k": request.top_k,
            "num_candidates": 100
        }
        
        if filter_clauses:
            knn_query["filter"] = filter_clauses

        # Выполнение запроса
        response = await es_client.search(
            index="scientific_articles",
            knn=knn_query,
            source=["title", "url", "abstract", "metadata"] # Исключаем вектор из выдачи
        )
        
        # Формирование ответа
        results = []
        for hit in response['hits']['hits']:
            results.append(SearchResult(
                id=hit['_id'],
                title=hit['_source']['title'],
                url=hit['_source']['url'],
                abstract=hit['_source']['abstract'],
                similarity_score=hit['_score'],
                metadata=hit['_source']['metadata']
            ))
        back_logger.info(f"Search returned results: {[r.model_dump(exclude={'abstract'}) for r in results]}")
            
        return results

    except Exception as e:
        back_logger.error(f"Error during search operation {e}")
        raise HTTPException(status_code=500, detail=str(e))