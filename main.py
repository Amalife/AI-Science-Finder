from logger.logger import setup_logging, back_logger
from config.config import configuration

logger_config_path = configuration.project_root / "logger_config.json"
setup_logging(
    config_path=logger_config_path
)

import time
import uvicorn
from fastapi import FastAPI, Request
import backend.endpoints as endpoints

from backend.external import es_client
from contextlib import asynccontextmanager



@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await es_client.close()

app = FastAPI(title="AI Science Finder Backend", lifespan=lifespan)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_body = await request.body()
    back_logger.info(f"Request body: {request_body.decode('utf-8', errors='ignore')[:500]}")
    
    async def receive():
        return {"type": "http.request", "body": request_body, "more_body": False}
    
    request = Request(request.scope, receive=receive)
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    back_logger.info(f"{request.method} {request.url} | {response.status_code} | {response.headers.get('content-type', 'N/A')} | {response.headers.get('content-length', 'N/A')} | {process_time:.4f}s")
    return response

app.include_router(endpoints.router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)