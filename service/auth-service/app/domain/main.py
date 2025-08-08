import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

# auth-service 로거 생성
logger = logging.getLogger("auth-service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Auth Service Domain 시작")
    yield
    logger.info("🛑 Auth Service Domain 종료")

app = FastAPI(
    title="Auth Service Domain",
    description="Auth Service Domain for authentication",
    version="0.1.0",
    docs_url="/docs",
    lifespan=lifespan
)

logger.info("🔐 Auth Service Domain 앱 초기화 완료")