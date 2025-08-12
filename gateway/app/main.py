# Gateway API - Auth Service로 요청 전달하는 프록시
import os
import sys
import logging
import json
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator, Dict, Any

import httpx
from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse

# Railway 환경 확인
IS_RAILWAY = os.getenv("RAILWAY_ENVIRONMENT") == "true" or os.getenv("PORT") is not None

# 로깅 설정
if IS_RAILWAY:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    print("🚂 Gateway - Railway 환경에서 실행 중 - Auth Service로 요청 전달")
else:
    logging.basicConfig(level=logging.INFO)
    print("🏠 Gateway - 로컬 환경에서 실행 중")

logger = logging.getLogger("gateway_api")

# Auth Service URL 설정
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "https://auth-service-production-aabc.up.railway.app")

# 허용된 도메인 목록
ALLOWED_DOMAINS = [
    "jhyang.info",
    "www.jhyang.info",
    "localhost",
    "127.0.0.1",
    "frontend"
]

# 비동기 HTTP 클라이언트 (싱글톤 패턴)
_http_client: Optional[httpx.AsyncClient] = None

async def get_http_client() -> httpx.AsyncClient:
    """비동기 HTTP 클라이언트 싱글톤 반환"""
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
    return _http_client

async def close_http_client():
    """HTTP 클라이언트 정리"""
    global _http_client
    if _http_client:
        await _http_client.aclose()
        _http_client = None

# Auth Service 연결 함수들
async def call_auth_service(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Auth Service 호출 함수 (동기 응답)"""
    client = await get_http_client()
    url = f"{AUTH_SERVICE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = await client.get(url)
        elif method.upper() == "POST":
            response = await client.post(url, json=data)
        else:
            raise HTTPException(status_code=400, detail=f"지원하지 않는 HTTP 메서드: {method}")
        
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException:
        logger.error(f"⏰ Auth Service 타임아웃: {url}")
        raise HTTPException(status_code=504, detail="Auth Service 응답 시간 초과")
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ Auth Service 오류: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Auth Service 오류: {e.response.text}")
    except Exception as e:
        logger.error(f"❌ Auth Service 연결 실패: {str(e)}")
        raise HTTPException(status_code=503, detail="Auth Service 연결 실패")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 서비스 시작")
    # HTTP 클라이언트 초기화
    await get_http_client()
    yield
    # HTTP 클라이언트 정리
    await close_http_client()
    logger.info("🛑 Gateway API 서비스 종료")

app = FastAPI(
    title="Gateway API",
    description="Gateway API for ausikor.com - Auth Service 프록시",
    version="0.3.0",
    docs_url="/docs",
    lifespan=lifespan
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jhyang.info",
        "https://www.jhyang.info",
        "http://jhyang.info",
        "http://www.jhyang.info",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://frontend:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 메인 라우터 생성
gateway_router = APIRouter(prefix="/api/v1", tags=["Gateway API"])

# 헬스 체크 엔드포인트
@gateway_router.get("/health", summary="테스트 엔드포인트")
async def health_check():
    return {"status": "healthy!", "message": "Gateway API is running", "service": "gateway"}

# 회원가입 요청을 Auth Service로 전달 (프록시 역할)
@gateway_router.post("/signup", summary="회원가입 - Auth Service로 전달")
async def signup_proxy(request: Request):
    """회원가입 요청을 Auth Service로 전달하는 프록시"""
    try:
        body = await request.json()
        
        # Gateway 로그에 요청 정보 출력
        gateway_log = {
            "event": "signup_proxy_request",
            "timestamp": datetime.now().isoformat(),
            "request_data": body,
            "source": "gateway_api",
            "target_service": "auth_service",
            "environment": "railway"
        }
        print(f"🚂 GATEWAY PROXY LOG: {json.dumps(gateway_log, indent=2, ensure_ascii=False)}")
        logger.info(f"GATEWAY_PROXY_LOG: {json.dumps(gateway_log, ensure_ascii=False)}")
        
        # Auth Service로 요청 전달
        response_data = await call_auth_service("/signup", "POST", body)
        
        # Gateway 로그에 응답 정보 출력
        response_log = {
            "event": "signup_proxy_response",
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data,
            "source": "gateway_api",
            "target_service": "auth_service",
            "environment": "railway"
        }
        print(f"🚂 GATEWAY RESPONSE LOG: {json.dumps(response_log, indent=2, ensure_ascii=False)}")
        logger.info(f"GATEWAY_RESPONSE_LOG: {json.dumps(response_log, ensure_ascii=False)}")
        
        return response_data
        
    except Exception as e:
        error_msg = f"회원가입 프록시 오류: {str(e)}"
        print(f"❌ GATEWAY PROXY ERROR: {error_msg}")
        logger.error(error_msg)
        
        # 에러도 Gateway 로그에 출력
        error_log = {
            "event": "signup_proxy_error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "source": "gateway_api",
            "target_service": "auth_service",
            "railway_status": "error"
        }
        print(f"🚂 GATEWAY ERROR LOG: {json.dumps(error_log, indent=2, ensure_ascii=False)}")
        logger.error(f"GATEWAY_ERROR_LOG: {json.dumps(error_log, ensure_ascii=False)}")
        
        raise HTTPException(status_code=500, detail=f"회원가입 실패: {str(e)}")

# 첫 화면 (회원가입 버튼이 있는 페이지)
@app.get("/", summary="첫 화면 - 회원가입 버튼")
async def main_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>메인 페이지</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div class="w-full max-w-md">
            <div class="bg-white rounded-3xl shadow-2xl px-8 py-12">
                <div class="text-center mb-12">
                    <h1 class="text-5xl font-bold text-gray-900 tracking-tight">
                        Welcome
                    </h1>
                    <p class="text-gray-600 mt-4">
                        회원가입을 진행하세요
                    </p>
                </div>
                
                <form id="signupForm" method="POST" action="/signup" class="space-y-8">
                    <button
                        type="submit"
                        class="w-full py-4 bg-blue-600 text-white font-semibold rounded-2xl hover:bg-blue-700 transition-all duration-300 transform hover:scale-105"
                    >
                        🚀 회원가입 페이지로 이동
                    </button>
                </form>
                
                <div class="mt-8 text-center">
                    <p class="text-gray-600 text-sm">
                        회원가입 버튼을 누르면 POST 방식으로 /signup 페이지로 이동합니다
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# 라우터를 앱에 포함
app.include_router(gateway_router)

if __name__ == "__main__":
    import uvicorn
    
    # Railway 환경변수에서 PORT 가져오기, 없으면 8000 사용
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
