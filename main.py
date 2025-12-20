import uvicorn
from fastapi import FastAPI
import backend.endpoints as endpoints
from logger.logger import setup_logging, back_logger
from config.config import configuration

logger_config_path = configuration.project_root / "logger_config.json"
setup_logging(
    config_path=logger_config_path
)

app = FastAPI(title="AI Science Finder Backend")
app.include_router(endpoints.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)