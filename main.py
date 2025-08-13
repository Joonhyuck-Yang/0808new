# CACHE BUSTER - Force Railway to use new version
# Build ID: 2024-08-12-17-30-00
# Cache Version: v3.0 - Auth Service 분리

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

# Vercel 환경 확인
IS_VERCEL = os.getenv("VERCEL") == "1"

# 로컬 환경변수 로드 (Vercel이 아닐 때만)
if not IS_VERCEL:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

# Railway 환경 확인
IS_RAILWAY = os.getenv("RAILWAY_ENVIRONMENT") == "true" or (os.getenv("PORT") is not None and os.getenv("PORT") != "")

# Railway 환경변수에서 PORT 가져오기, 없으면 8080 사용
# PORT가 None이거나 빈 문자열일 때 기본값 사용
def get_port():
    """안전하게 PORT 환경변수를 가져오는 함수"""
    port_str = os.getenv("PORT")
    if port_str is None or port_str == "":
        return 8080
    try:
        port = int(port_str)
        if port <= 0 or port > 65535:
            print(f"⚠️ 경고: PORT {port}가 유효하지 않습니다. 기본값 8080을 사용합니다.")
            return 8080
        return port
    except (ValueError, TypeError):
        print(f"⚠️ 경고: PORT '{port_str}'를 정수로 변환할 수 없습니다. 기본값 8080을 사용합니다.")
        return 8080

# 로깅 설정 (Railway 환경에 최적화)
if IS_RAILWAY:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    print("🚂 Gateway - Railway 환경에서 실행 중 - Auth Service로 요청 전달")
    print("🔄 CACHE BUSTER: v3.0 - Auth Service 분리")
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
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

# Auth Service 연결 함수들 (비동기 스트림 지원)
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

async def stream_auth_service(endpoint: str, method: str = "GET", data: dict = None) -> AsyncGenerator[str, None]:
    """Auth Service 스트림 호출 함수 (비동기 스트림 응답)"""
    client = await get_http_client()
    url = f"{AUTH_SERVICE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                async for chunk in response.aiter_text():
                    yield chunk
        elif method.upper() == "POST":
            async with client.stream("POST", url, json=data) as response:
                response.raise_for_status()
                async for chunk in response.aiter_text():
                    yield chunk
        else:
            raise HTTPException(status_code=400, detail=f"지원하지 않는 HTTP 메서드: {method}")
    except httpx.TimeoutException:
        logger.error(f"⏰ Auth Service 스트림 타임아웃: {url}")
        yield json.dumps({"error": "Auth Service 응답 시간 초과"})
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ Auth Service 스트림 오류: {e.response.status_code} - {e.response.text}")
        yield json.dumps({"error": f"Auth Service 오류: {e.response.text}"})
    except Exception as e:
        logger.error(f"❌ Auth Service 스트림 연결 실패: {str(e)}")
        yield json.dumps({"error": "Auth Service 연결 실패"})

def is_allowed_domain(host: str) -> bool:
    """허용된 도메인인지 확인"""
    # 포트 번호 제거
    if ":" in host:
        host = host.split(":")[0]
    
    # localhost와 IP 주소 허용
    if host in ["localhost", "127.0.0.1"]:
        return True
    
    # 허용된 도메인 목록 확인
    for allowed_domain in ALLOWED_DOMAINS:
        if host == allowed_domain or host.endswith(f".{allowed_domain}"):
            return True
    
    return False

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
    description="Gateway API for ausikor.com - Auth Service 분리 버전",
    version="0.2.0",
    docs_url="/docs",
    lifespan=lifespan
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jhyang.info",        # 커스텀 도메인
        "https://www.jhyang.info",    # www 서브도메인
        "http://jhyang.info",         # HTTP 커스텀 도메인 (개발용)
        "http://www.jhyang.info",     # HTTP www 서브도메인 (개발용)
        "http://localhost:3000",      # 로컬 개발용
        "http://127.0.0.1:3000",      # 로컬 IP 개발용
        "http://frontend:3000",       # Docker 내부 네트워크
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 도메인 검증 미들웨어 추가
@app.middleware("http")
async def domain_validation_middleware(request: Request, call_next):
    """도메인 검증 미들웨어"""
    host = request.headers.get("host", "")
    
    # 헬스체크는 모든 도메인에서 허용
    if request.url.path == "/api/v1/health":
        return await call_next(request)
    
    # 허용된 도메인인지 확인
    if not is_allowed_domain(host):
        logger.warning(f"🚫 허용되지 않은 도메인 접근: {host}")
        return JSONResponse(
            status_code=403,
            content={"error": "Access denied", "message": "허용되지 않은 도메인입니다."}
        )
    
    logger.info(f"✅ 허용된 도메인 접근: {host}")
    return await call_next(request)

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

# 스트림 처리를 위한 엔드포인트들
@gateway_router.get("/auth/stream", summary="Auth Service 스트림 연결")
async def auth_stream():
    """Auth Service와의 스트림 연결"""
    logger.info("🌊 Auth Service 스트림 연결 시작")
    
    async def generate_stream():
        try:
            async for chunk in stream_auth_service("/auth/health"):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            error_msg = json.dumps({"error": str(e)})
            yield f"data: {error_msg}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

@gateway_router.post("/auth/stream/login", summary="Auth Service 로그인 스트림")
async def auth_login_stream(request: Request):
    """Auth Service 로그인 스트림 처리"""
    try:
        body = await request.json()
        logger.info(f"🌊 Auth Service 로그인 스트림 시작: {body.get('name', 'unknown')}")
        
        async def generate_login_stream():
            try:
                async for chunk in stream_auth_service("/auth/login", "POST", body):
                    yield f"data: {chunk}\n\n"
            except Exception as e:
                error_msg = json.dumps({"error": str(e)})
                yield f"data: {error_msg}\n\n"
        
        return StreamingResponse(
            generate_login_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
    except Exception as e:
        logger.error(f"❌ 로그인 스트림 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"로그인 스트림 실패: {str(e)}")

@gateway_router.post("/auth/stream/signup", summary="Auth Service 회원가입 스트림")
async def auth_signup_stream(request: Request):
    """Auth Service 회원가입 스트림 처리"""
    try:
        body = await request.json()
        logger.info(f"🌊 Auth Service 회원가입 스트림 시작: {body.get('name', 'unknown')}")
        
        async def generate_signup_stream():
            try:
                async for chunk in stream_auth_service("/auth/signup", "POST", body):
                    yield f"data: {chunk}\n\n"
            except Exception as e:
                error_msg = json.dumps({"error": str(e)})
                yield f"data: {error_msg}\n\n"
        
        return StreamingResponse(
            generate_signup_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
    except Exception as e:
        logger.error(f"❌ 회원가입 스트림 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"회원가입 스트림 실패: {str(e)}")

# 라우터를 앱에 포함
app.include_router(gateway_router)

# Vercel 서버리스 환경을 위한 핸들러 (Vercel에서만 사용)
def handler(request, context):
    """Vercel 서버리스 함수 핸들러"""
    return app(request, context)

# 로컬 개발용 (Vercel에서는 사용되지 않음)
if __name__ == "__main__":
    import uvicorn
    
    # Railway 환경변수에서 PORT 가져오기, 없으면 8080 사용
    # PORT가 None이거나 빈 문자열일 때 기본값 사용
    port = get_port()
    
    print(f"🚀 서버 시작 - 포트: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)