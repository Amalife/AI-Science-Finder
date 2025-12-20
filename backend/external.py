from config.config import configuration
from elasticsearch import AsyncElasticsearch
from gigachat import GigaChat


if not configuration.gigachat_credentials:
    raise ValueError("GIGACHAT_CREDENTIALS не установлены")
giga = GigaChat(credentials=configuration.gigachat_credentials,
                verify_ssl_certs=configuration.gigachat_verify_ssl)

es_client = AsyncElasticsearch(
    hosts="http://localhost:9200"
)