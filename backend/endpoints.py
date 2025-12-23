from fastapi import APIRouter, HTTPException, UploadFile, File
from backend.utils import get_embedding
from backend.external import es_client, get_index_name
from backend.model import SearchRequest, SearchResult, Article
from typing import List
from logger.logger import back_logger
from datetime import datetime
import pdfplumber


router = APIRouter()


@router.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Загрузка PDF файла с arXiv и добавление в базу"""
    try:
        
        # Чтение PDF
        with pdfplumber.open(file.file) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        # Парсинг текста (простой подход для arXiv PDF)
        lines = text.split('\n')
        title = ""
        authors = ""
        abstract = ""
        in_abstract = False
        
        for line in lines:
            line = line.strip()
            if line.lower().startswith("title:") or line.lower().startswith("title"):
                title = line.split(":", 1)[-1].strip()
            elif line.lower().startswith("authors:") or line.lower().startswith("author"):
                authors = line.split(":", 1)[-1].strip()
            elif line.lower().startswith("abstract:") or line.lower().startswith("abstract"):
                abstract = line.split(":", 1)[-1].strip()
                in_abstract = True
            elif in_abstract and line:
                # Продолжение абстракта
                if not line.lower().startswith(("introduction", "1.", "i.")):  # Простая эвристика окончания абстракта
                    abstract += " " + line
                else:
                    break
        
        # Очистка
        title = title.replace('\n', ' ').strip()
        authors = authors.replace('\n', ' ').strip()
        abstract = abstract.replace('\n', ' ').strip()
        
        # Предполагаем, что filename - это arXiv ID
        arxiv_id = file.filename.replace('.pdf', '')
        url = f"https://arxiv.org/pdf/{arxiv_id}"
        
        # Создание Article
        article = Article(
            title=title,
            url=url,
            abstract=abstract,
            metadata={
                "author": authors,
                "published_date": datetime.now().strftime("%Y-%m-%d"),
                "tags": []  # Можно добавить извлечение тегов позже
            }
        )
        
        # Векторизация абстракта
        vector = get_embedding(abstract)
        
        doc = article.model_dump()
        doc["vector"] = vector
        
        # Индексация в ES
        await es_client.index(index=get_index_name(), document=doc)
        
        back_logger.info(f"Uploaded and indexed PDF: {title}")
        return {"status": "success", "message": f"PDF '{file.filename}' обработан и добавлен в базу."}
    
    except Exception as e:
        back_logger.error(f"Error uploading PDF: {e}")
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
            index=get_index_name(),
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