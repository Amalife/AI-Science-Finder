import os
import uuid
import json
from datetime import datetime
import pandas as pd
from tqdm.asyncio import tqdm
from elasticsearch import helpers, Elasticsearch
from gigachat import GigaChat
from config.config import configuration
import logging
from pathlib import Path

def prepare_logger(logger_name: str, log_path: Path):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter("%(levelname)s | %(asctime)s | %(name)s | %(message)s")
    stream_handler.setFormatter(formatter)

    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.touch(exist_ok=True)
    file_handler = logging.FileHandler(log_path, mode="a")
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

LOG_PATH = configuration.project_root / "logs" / "fill_vdb.log"

prepare_logger("fill_vdb", LOG_PATH)
script_logger = logging.getLogger("fill_vdb")

# --- Настройки ---
ES_HOST = "http://localhost:9200"
INDEX_NAME = "scientific_articles"

# --- Инициализация ---
if not configuration.gigachat_credentials:
    raise ValueError("Set GIGACHAT_CREDENTIALS")

es_client = Elasticsearch(hosts=ES_HOST)

try:
    info = es_client.info()
    script_logger.info(f"Elasticsearch info: {info}")
except Exception as e:
    script_logger.error(f"Error connecting to ES: {e}")
    exit(1)

# --- Утилиты ---
def clean_date(date_str):
    try:
        if pd.isna(date_str):
            return datetime.now().strftime("%d.%m.%Y")

        return str(pd.to_datetime(date_str).date())
    except:
        return datetime.now().strftime("%d.%m.%Y") # Fallback

# --- Основная логика ---

def process_dataset(csv_file_path: str):
    script_logger.info(f"Loading dataset from {csv_file_path}")
    df = pd.read_csv(csv_file_path)
    
    # Инициализация GigaChat
    giga = GigaChat(credentials=configuration.gigachat_credentials,
                    scope=configuration.gigachat_scope,
                    verify_ssl_certs=configuration.gigachat_verify_ssl)
    
    actions = []
    
    script_logger.info("Starting article processing...")
    
    # Проходимся по всем строкам датафрейма
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
        if not row["summary"]:
            continue
        
        # Извлечение и очистка полей
        original_id = str(row.get('id', uuid.uuid4()))
        title = str(row.get('title', 'Без названия')).lower()
        authors_raw = row.get('authors', 'Unknown')
        
        date_raw = row.get('date', None)
        pub_date = clean_date(date_raw)
        
        topics_raw = row.get('topics', '')
        if isinstance(topics_raw, str):
            tags = [t.strip() for t in topics_raw.replace(';', ',').split(',') if t.strip()]
        else:
            tags = []
            
        url = str(row.get('link', ''))
        full_text = str(row.get('text', ''))
        summ_text = str(row.get('summary', ''))
            
        # Текст для векторизации: Заголовок + краткое содержание
        text_to_embed = f"{title}. {summ_text}"
            
        try:
            # Получение эмбеддинга
            embedding_response = giga.embeddings(texts=[text_to_embed])
            vector = embedding_response.data[0].embedding
                
            doc = {
                "_index": INDEX_NAME,
                "_id": original_id,
                "_source": {
                    "title": title,
                    "url": url,
                    "abstract": summ_text,
                    "full_text": full_text,
                    "metadata": {
                        "author": str(authors_raw),
                        "published_date": pub_date,
                        "tags": tags
                    },
                    "vector": vector
                }
            }
            actions.append(doc)
                
        except Exception as e:
            script_logger.error(f"Ошибка при обработке ID {original_id} {e}")
            continue
        
        # Пакетная отправка в Elastic каждые 50 документов (чтобы не забить память)
        if len(actions) >= 50:
            helpers.bulk(es_client, actions)
            actions = []

    # Отправка оставшихся
    if actions:
        helpers.bulk(es_client, actions)

    # es_client.close()
    script_logger.info("Loading completed!")

if __name__ == "__main__":
    CSV_PATH = configuration.project_root / "data" / configuration.data_csv_filename
    MAPPING_PATH = configuration.project_root / "data" / configuration.data_mapping_filename

    with open(MAPPING_PATH, "r", encoding="utf-8") as json_mapfile:
        elastic_mappings = json.load(json_mapfile)
    if es_client.indices.exists(index=INDEX_NAME):
        script_logger.info(f"Index {INDEX_NAME} found, refilling data")
        es_client.indices.delete(index=INDEX_NAME)
    else:
        script_logger.info(f"Index {INDEX_NAME} not found, filling data")
        es_client.indices.create(index=INDEX_NAME, body=elastic_mappings)

    
    # Проверка наличия файла (для теста создадим dummy файл, если нет)
    if not os.path.exists(CSV_PATH):
        script_logger.info(f"File {CSV_PATH} not found. Creating a CSV file with columns: id, title, authors, date, topics, text, link, summary")
    else:
        process_dataset(CSV_PATH)