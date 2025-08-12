# CACHE BUSTER - Force Railway to use new version
# Build ID: 2024-08-12-17-30-00
# Cache Version: v2.0

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
IS_RAILWAY = os.getenv("RAILWAY_ENVIRONMENT") == "true" or os.getenv("PORT") is not None

# 로깅 설정 (Railway 환경에 최적화)
if IS_RAILWAY:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    print("🚂 Railway 환경에서 실행 중 - JSON 로그 출력 활성화")
    print("🔄 CACHE BUSTER: v2.0 - Force new build")
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    print("🏠 로컬 환경에서 실행 중")

logger = logging.getLogger("gateway_api")

# Auth Service URL 설정
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")

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
    description="Gateway API for ausikor.com",
    version="0.1.0",
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
    return {"status": "healthy!", "message": "Gateway API is running"}

# 회원가입 데이터를 받는 엔드포인트
@gateway_router.post("/signup", summary="회원가입")
async def signup(request: Request):
    """회원가입 처리 - 아이디와 비밀번호를 name, value 형태의 JSON으로 받아서 Railway 로그에 출력"""
    try:
        body = await request.json()
        
        # Railway 로그에 JSON 형태로 출력
        railway_log_data = {
            "event": "user_signup",
            "timestamp": datetime.now().isoformat(),
            "user_data": {
                "name": body.get("id", "unknown"),
                "value": body.get("password", "unknown")
            },
            "source": "gateway_api",
            "environment": "railway"
        }
        
        # Railway 로그에 출력 (중요!)
        print(f"🚂 RAILWAY LOG JSON: {json.dumps(railway_log_data, indent=2, ensure_ascii=False)}")
        logger.info(f"RAILWAY_LOG_JSON: {json.dumps(railway_log_data, ensure_ascii=False)}")
        
        # 성공 응답
        response_data = {
            "status": "success",
            "message": "회원가입 성공!",
            "data": {
                "name": body.get("id", "unknown"),
                "value": body.get("password", "unknown")
            },
            "railway_logged": True
        }
        
        # Railway 로그에 최종 결과도 출력
        final_log = {
            "event": "signup_completed",
            "timestamp": datetime.now().isoformat(),
            "result": response_data,
            "railway_status": "success"
        }
        print(f"🚂 RAILWAY FINAL LOG: {json.dumps(final_log, indent=2, ensure_ascii=False)}")
        logger.info(f"RAILWAY_FINAL_LOG: {json.dumps(final_log, ensure_ascii=False)}")
        
        return response_data
        
    except Exception as e:
        error_msg = f"회원가입 오류: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        
        # 에러도 Railway 로그에 출력
        error_log = {
            "event": "signup_error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "railway_status": "error"
        }
        print(f"🚂 RAILWAY ERROR LOG: {json.dumps(error_log, indent=2, ensure_ascii=False)}")
        logger.error(f"RAILWAY_ERROR_LOG: {json.dumps(error_log, ensure_ascii=False)}")
        
        raise HTTPException(status_code=500, detail=f"회원가입 실패: {str(e)}")

# 로그인 페이지 (HTML) - 회원가입 기능 포함
@app.get("/", summary="로그인 및 회원가입 페이지")
async def login_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>로그인 및 회원가입</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center p-4">
        <div class="w-full max-w-sm">
            <div class="bg-white rounded-3xl shadow-2xl px-8 py-12">
                <div class="text-center mb-12">
                    <h1 class="text-5xl font-bold text-gray-900 tracking-tight">
                        Sign Up
                    </h1>
                </div>
                <form id="signupForm" class="space-y-8">
                    <div class="relative">
                        <input
                            type="text"
                            id="id"
                            name="id"
                            placeholder="아이디 (Username)"
                            class="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                            required
                        />
                    </div>
                    <div class="relative">
                        <input
                            type="password"
                            id="password"
                            name="password"
                            placeholder="비밀번호 (Password)"
                            class="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        class="w-full py-4 bg-blue-600 text-white font-semibold rounded-2xl hover:bg-blue-700 transition-all duration-300 transform hover:scale-105"
                    >
                        회원가입 (Sign Up)
                    </button>
                </form>
                
                <div class="mt-8 text-center">
                    <p class="text-gray-600 text-sm">
                        회원가입 버튼을 누르면 아이디와 비밀번호가 Railway 로그에 출력됩니다
                    </p>
                </div>
            </div>
        </div>

        <script>
        document.getElementById('signupForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                id: document.getElementById('id').value,
                password: document.getElementById('password').value
            };

            try {
                console.log('🚀 회원가입 데이터 전송 시작...');
                console.log('📦 전송할 데이터:', formData);
                
                const response = await fetch('/api/v1/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const result = await response.json();
                console.log('✅ 회원가입 성공:', result);
                
                if (response.ok) {
                    alert('회원가입 성공!\\n\\n아이디: ' + formData.id + '\\n비밀번호: ' + formData.password + '\\n\\nRailway 로그를 확인하세요!');
                    
                    // 폼 초기화
                    document.getElementById('id').value = '';
                    document.getElementById('password').value = '';
                } else {
                    throw new Error(result.detail || '회원가입 실패');
                }
            } catch (error) {
                console.error('❌ 회원가입 실패:', error);
                alert('회원가입 실패: ' + error.message);
            }
        });
        </script>
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
        logger.info(f"🌊 Auth Service 로그인 스트림 시작: {body.get('id', 'unknown')}")
        
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
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)