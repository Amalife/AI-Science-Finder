from config.config import configuration
from elasticsearch import AsyncElasticsearch
from gigachat import GigaChat
from logger.logger import back_logger

if not configuration.gigachat_credentials and not configuration.use_hf_embedder:
    raise ValueError("GIGACHAT_CREDENTIALS не установлены или USE_HF_EMBEDDER=true")

giga = None
if not configuration.use_hf_embedder:
    giga = GigaChat(credentials=configuration.gigachat_credentials,
                    verify_ssl_certs=configuration.gigachat_verify_ssl)
    back_logger.info("Using GigaChat API for embeddings")
else:
    back_logger.info("Using HF embedder for embeddings")

hf_model = None
if configuration.use_hf_embedder:
    from sentence_transformers import SentenceTransformer
    hf_model = SentenceTransformer(configuration.hf_model_name, cache_folder=configuration.hf_cache_dir)
    back_logger.info(f"Loaded HF model: {configuration.hf_model_name}")

es_client = AsyncElasticsearch(
    hosts="http://localhost:9200"
)

def get_index_name():
    embedder = 'hf' if configuration.use_hf_embedder else 'gigachat'
    return f"scientific_articles_{embedder}"

def get_embedding_dimension():
    if configuration.use_hf_embedder:
        return hf_model.get_sentence_embedding_dimension()
    else:
        return 1024  # GigaChat embedding dimension