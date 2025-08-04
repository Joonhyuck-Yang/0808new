from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import structlog
from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.common.config import settings
from app.common.logging import setup_logging
from app.router import proxy_router, health_router, metrics_router
from app.domain.service_discovery import ServiceDiscovery
from app.domain.proxy_service import ProxyService


# 로깅 설정
setup_logging()
logger = structlog.get_logger()


# Pydantic 모델 정의
class ChatMessage(BaseModel):
    id: int
    text: str
    timestamp: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시
    logger.info("Starting API Gateway...")
    
    # 서비스 디스커버리 초기화
    service_discovery = ServiceDiscovery()
    await service_discovery.initialize()
    
    # 프록시 서비스 초기화
    proxy_service = ProxyService(service_discovery)
    
    # 전역 변수로 설정
    app.state.service_discovery = service_discovery
    app.state.proxy_service = proxy_service
    
    logger.info("API Gateway started successfully")
    
    yield
    
    # 종료 시
    logger.info("Shutting down API Gateway...")
    await service_discovery.cleanup()


# FastAPI 애플리케이션 생성
app = FastAPI(
    title="MSA API Gateway",
    description="Microservice Architecture API Gateway with Service Discovery",
    version="1.0.0",
    lifespan=lifespan
)

# 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """요청/응답 로깅 미들웨어"""
    logger.info(
        "Incoming request",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else None
    )
    
    response = await call_next(request)
    
    logger.info(
        "Response sent",
        status_code=response.status_code,
        method=request.method,
        url=str(request.url)
    )
    
    return response


@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    """에러 처리 미들웨어"""
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(
            "Unhandled exception",
            error=str(e),
            method=request.method,
            url=str(request.url)
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# 라우터 등록
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(metrics_router, prefix="/metrics", tags=["Metrics"])
app.include_router(proxy_router, tags=["Proxy"])


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "MSA API Gateway",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/chat", response_model=Dict[str, Any])
async def receive_chat_message(message: ChatMessage):
    """
    프론트엔드에서 보내는 채팅 메시지를 받는 POST 엔드포인트
    
    Args:
        message: ChatMessage 모델 (id, text, timestamp 포함)
    
    Returns:
        Dict: 처리 결과와 받은 데이터
    """
    try:
        logger.info(
            "Received chat message",
            message_id=message.id,
            text=message.text,
            timestamp=message.timestamp
        )
        
        # 여기에 실제 메시지 처리 로직을 추가할 수 있습니다
        # 예: 데이터베이스 저장, AI 처리, 다른 서비스로 전달 등
        
        return {
            "status": "success",
            "message": "메시지가 성공적으로 수신되었습니다",
            "received_data": {
                "id": message.id,
                "text": message.text,
                "timestamp": message.timestamp,
                "processed_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(
            "Error processing chat message",
            error=str(e),
            message_id=message.id
        )
        raise HTTPException(status_code=500, detail="메시지 처리 중 오류가 발생했습니다")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
