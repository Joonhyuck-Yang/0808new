from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import structlog
from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime

# 로깅 설정
logger = structlog.get_logger()

# Pydantic 모델 정의
class ChatMessage(BaseModel):
    id: int
    text: str
    timestamp: str

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="MSA API Gateway",
    description="Microservice Architecture API Gateway",
    version="1.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "MSA API Gateway",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/v1/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "API Gateway"
    }

@app.post("/api/v1/auth/login")
async def login():
    """로그인 엔드포인트"""
    return {
        "status": "success",
        "message": "Login endpoint ready"
    }

@app.post("/api/v1/auth/register")
async def register():
    """회원가입 엔드포인트"""
    return {
        "status": "success",
        "message": "Register endpoint ready"
    }

@app.get("/api/v1/auth/me")
async def get_user_info():
    """사용자 정보 조회 엔드포인트"""
    return {
        "status": "success",
        "message": "User info endpoint ready"
    }

@app.post("/api/chat", response_model=Dict[str, Any])
async def receive_chat_message(message: ChatMessage):
    """채팅 메시지 수신 엔드포인트"""
    try:
        logger.info(
            "Received chat message",
            message_id=message.id,
            text=message.text,
            timestamp=message.timestamp
        )
        
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
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )