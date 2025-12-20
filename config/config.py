from pathlib import Path

from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings

# Настройка конфигурации из файла .env и валидация имен переменных окружения
class Config(BaseSettings):
    model_name: str = Field(validation_alias="MODEL_NAME")
    gigachat_credentials: str | None = Field(validation_alias="GIGACHAT_CREDENTIALS", default=None)
    gigachat_scope: str | None = Field(validation_alias="GIGACHAT_SCOPE", default=None)
    gigachat_verify_ssl: bool = Field(validation_alias="GIGACHAT_VERIFY_SSL", default=False)

    data_csv_filename: str = Field(validation_alias="DATA_CSV_FILENAME", default="data_sample_with_summaries.csv")
    data_mapping_filename: str = Field(validation_alias="DATA_MAPPING_FILENAME", default="mapping.json")

    project_root: Path = Path(__file__).resolve().parents[1]
    env_file_path: Path = project_root / ".env"

    if env_file_path.is_file():
        model_config = SettingsConfigDict(env_file=env_file_path, extra="ignore", validate_default=False)
    

configuration = Config()