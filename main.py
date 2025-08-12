from typing import Optional, List, AsyncGenerator
from fastapi import APIRouter, FastAPI, Request, UploadFile, File, Query, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
import os
import logging
import sys
import json
import httpx
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager

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
    # Railway에서는 JSON 형태로 로그 출력
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    print("🚂 Railway 환경에서 실행 중 - JSON 로그 출력 활성화")
else:
    # 로컬 환경에서는 일반 로그
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
        logger.error(f"❌ Auth Service 스트림 오류: {e.response.status_code}")
        yield json.dumps({"error": f"Auth Service 오류: {e.response.status_code}"})
    except Exception as e:
        logger.error(f"❌ Auth Service 스트림 연결 실패: {str(e)}")
        yield json.dumps({"error": "Auth Service 연결 실패"})

async def call_auth_service_with_retry(endpoint: str, method: str = "GET", data: dict = None, max_retries: int = 3) -> dict:
    """Auth Service 호출 함수 (재시도 로직 포함)"""
    for attempt in range(max_retries):
        try:
            return await call_auth_service(endpoint, method, data)
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"🔄 Auth Service 재시도 {attempt + 1}/{max_retries}: {str(e)}")
            await asyncio.sleep(1 * (attempt + 1))  # 지수 백오프
    raise HTTPException(status_code=503, detail="Auth Service 연결 실패")

# 도메인 검증 함수
def is_allowed_domain(host: str) -> bool:
    """허용된 도메인인지 확인"""
    if not host:
        return False
    
    # 포트 번호 제거
    host = host.split(':')[0]
    
    # 허용된 도메인 목록 확인
    for allowed_domain in ALLOWED_DOMAINS:
        if host == allowed_domain or host.endswith(f".{allowed_domain}"):
            return True
    
    return False

# 회원가입 데이터를 저장할 파일 경로 (Vercel에서는 메모리 사용)
SIGNUP_DATA_FILE = "data/signup_data.json" if not IS_VERCEL else None

# 메모리 기반 데이터 저장 (Vercel용)
_signup_data_memory = []

# 회원가입 데이터를 파일에 저장하는 함수
def save_signup_data(data):
    try:
        if IS_VERCEL:
            # Vercel에서는 메모리에 저장
            new_entry = {
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            _signup_data_memory.append(new_entry)
            logger.info("회원가입 데이터가 메모리에 저장되었습니다.")
            return True
        else:
            # 로컬에서는 파일에 저장
            os.makedirs(os.path.dirname(SIGNUP_DATA_FILE), exist_ok=True)
            
            existing_data = []
            if os.path.exists(SIGNUP_DATA_FILE):
                with open(SIGNUP_DATA_FILE, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            new_entry = {
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            existing_data.append(new_entry)
            
            with open(SIGNUP_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"회원가입 데이터가 {SIGNUP_DATA_FILE}에 저장되었습니다.")
            return True
    except Exception as e:
        logger.error(f"데이터 저장 실패: {str(e)}")
        return False

# 회원가입 데이터를 읽는 함수
def load_signup_data():
    try:
        if IS_VERCEL:
            # Vercel에서는 메모리에서 읽기
            return _signup_data_memory
        else:
            # 로컬에서는 파일에서 읽기
            if os.path.exists(SIGNUP_DATA_FILE):
                with open(SIGNUP_DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
    except Exception as e:
        logger.error(f"데이터 읽기 실패: {str(e)}")
        return []

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

# 로그인 페이지 (HTML)
@app.get("/", summary="로그인 페이지")
async def login_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>로그인</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center p-4">
        <div class="w-full max-w-sm">
            <div class="bg-white rounded-3xl shadow-2xl px-8 py-12">
                <!-- Login Title -->
                <div class="text-center mb-12">
                    <h1 class="text-5xl font-bold text-gray-900 tracking-tight">
                        Login
                    </h1>
                </div>

                <!-- Login Form -->
                <form id="loginForm" class="space-y-8">
                    <!-- Username Input -->
                    <div class="relative">
                        <input
                            type="text"
                            id="id"
                            name="id"
                            placeholder="Username"
                            class="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                            required
                        />
                    </div>

                    <!-- Password Input -->
                    <div class="relative">
                        <input
                            type="password"
                            id="password"
                            name="password"
                            placeholder="Password"
                            class="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                            required
                        />
                    </div>

                    <!-- Login Button -->
                    <button
                        type="submit"
                        class="w-full bg-blue-600 text-white py-4 rounded-2xl hover:bg-blue-700 transition-all duration-200 font-medium text-lg shadow-sm"
                    >
                        Login
                    </button>
                </form>

                <!-- Divider -->
                <div class="mt-8">
                    <div class="relative">
                        <div class="absolute inset-0 flex items-center">
                            <div class="w-full border-t border-gray-300" />
                        </div>
                        <div class="relative flex justify-center text-sm">
                            <span class="px-2 bg-white text-gray-500">또는</span>
                        </div>
                    </div>
                </div>

                <!-- Sign Up Button -->
                <div class="mt-6">
                    <button onclick="window.location.href='/signup'" class="w-full bg-green-600 text-white py-4 rounded-2xl hover:bg-green-700 transition-all duration-200 font-medium text-lg shadow-sm">
                        회원가입
                    </button>
                </div>
            </div>
        </div>

        <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                id: document.getElementById('id').value,
                password: document.getElementById('password').value
            };

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const result = await response.json();
                
                if (response.ok) {
                    alert('로그인 성공!\\n' + JSON.stringify(result, null, 2));
                    // 로그인 성공 후 대시보드로 이동
                    window.location.href = '/dashboard';
                } else {
                    alert('로그인 실패: ' + result.detail);
                }
            } catch (error) {
                alert('로그인 실패: ' + error.message);
            }
        });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/login", summary="로그인")
async def login(request: Request):
    try:
        body = await request.json()
        id = body.get("id")
        password = body.get("password")
        
        logger.info(f"🔐 Gateway에서 로그인 요청: {id}")
        
        # Auth Service 호출
        auth_response = await call_auth_service("/auth/login", "POST", {
            "id": id,
            "password": password
        })
        
        logger.info(f"✅ Auth Service 로그인 성공: {auth_response}")
        
        return {
            "status": "success",
            "message": "로그인 성공",
            "access_token": auth_response.get("token", "dummy_token_12345"),
            "user": {
                "id": auth_response.get("user_id", id),
                "name": "사용자"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 로그인 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"로그인 실패: {str(e)}")

# API v1 로그인 엔드포인트 (기존 경로 유지)
@gateway_router.post("/login", summary="로그인 API v1")
async def login_api_v1(request: Request):
    try:
        body = await request.json()
        id = body.get("id")
        password = body.get("password")
        
        logger.info(f"🔐 Gateway API v1에서 로그인 요청: {id}")
        
        # 간단한 검증
        if not id or not password:
            raise HTTPException(status_code=400, detail="ID와 비밀번호를 입력해주세요")
        
        # Auth Service 호출 (재시도 로직 포함)
        auth_response = await call_auth_service_with_retry("/auth/login", "POST", {
            "id": id,
            "password": password
        })
        
        logger.info(f"✅ Auth Service 로그인 성공: {auth_response}")
        
        return {
            "status": "success",
            "message": "로그인 성공",
            "access_token": auth_response.get("token", "dummy_token_12345"),
            "user": {
                "id": auth_response.get("user_id", id),
                "name": "사용자"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 로그인 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"로그인 실패: {str(e)}")

# 회원가입 엔드포인트
@gateway_router.post("/signup", summary="회원가입")
async def signup_api_v1(request: Request):
    try:
        body = await request.json()
        print("=" * 50)
        print("🎯 회원가입 요청 받음!")
        print("=" * 50)
        
        # 요청 데이터 로깅
        print(f"📦 받은 데이터: {json.dumps(body, indent=2, ensure_ascii=False)}")
        logger.info(f"회원가입 요청: {body}")
        
        # Railway 로그에 JSON 형태로 출력 (중요!)
        railway_log_data = {
            "event": "user_signup",
            "timestamp": datetime.now().isoformat(),
            "user_data": body,
            "source": "gateway_api",
            "environment": "railway"
        }
        print(f"🚂 RAILWAY LOG JSON: {json.dumps(railway_log_data, indent=2, ensure_ascii=False)}")
        logger.info(f"RAILWAY_LOG_JSON: {json.dumps(railway_log_data, ensure_ascii=False)}")
        
        # 간단한 검증
        if not body:
            raise HTTPException(status_code=400, detail="데이터가 없습니다.")
        
        # 데이터를 파일에 저장
        save_success = save_signup_data(body)
        
        # 성공 응답
        response_data = {
            "status": "success",
            "message": "회원가입됨!",
            "data": body,
            "saved_to_file": save_success,
            "railway_logged": True
        }
        
        print(f"✅ 회원가입 완료: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        logger.info(f"회원가입 완료: {response_data}")
        
        # Railway 로그에 최종 결과도 출력
        final_log = {
            "event": "signup_completed",
            "timestamp": datetime.now().isoformat(),
            "result": response_data,
            "railway_status": "success"
        }
        print(f"🚂 RAILWAY FINAL LOG: {json.dumps(final_log, indent=2, ensure_ascii=False)}")
        logger.info(f"RAILWAY_FINAL_LOG: {json.dumps(final_log, ensure_ascii=False)}")
        
        print("=" * 50)
        
        return response_data
        
    except HTTPException:
        raise
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

# 회원가입 데이터 조회 엔드포인트
@gateway_router.get("/signup/data", summary="회원가입 데이터 조회")
async def get_signup_data():
    try:
        data = load_signup_data()
        print("=" * 50)
        print(f"📊 회원가입 데이터 조회: {len(data)}개 항목")
        print("=" * 50)
        
        # Railway 로그에 데이터 조회 정보 출력
        railway_query_log = {
            "event": "data_query",
            "timestamp": datetime.now().isoformat(),
            "query_type": "signup_data",
            "data_count": len(data),
            "source": "gateway_api",
            "environment": "railway"
        }
        print(f"🚂 RAILWAY QUERY LOG: {json.dumps(railway_query_log, indent=2, ensure_ascii=False)}")
        logger.info(f"RAILWAY_QUERY_LOG: {json.dumps(railway_query_log, ensure_ascii=False)}")
        
        if data:
            for i, item in enumerate(data, 1):
                print(f"📝 항목 {i}:")
                print(f"   시간: {item.get('timestamp', 'N/A')}")
                print(f"   데이터: {json.dumps(item.get('data', {}), indent=4, ensure_ascii=False)}")
                print("-" * 30)
        else:
            print("📭 저장된 데이터가 없습니다.")
        
        print("=" * 50)
        logger.info(f"회원가입 데이터 조회: {len(data)}개 항목")
        
        response_data = {
            "status": "success",
            "message": f"총 {len(data)}개의 회원가입 데이터",
            "data": data,
            "count": len(data),
            "railway_logged": True
        }
        
        # Railway 로그에 조회 결과도 출력
        final_query_log = {
            "event": "query_completed",
            "timestamp": datetime.now().isoformat(),
            "result": response_data,
            "railway_status": "success"
        }
        print(f"🚂 RAILWAY QUERY RESULT LOG: {json.dumps(final_query_log, indent=2, ensure_ascii=False)}")
        logger.info(f"RAILWAY_QUERY_RESULT_LOG: {json.dumps(final_query_log, ensure_ascii=False)}")
        
        return response_data
    except Exception as e:
        error_msg = f"데이터 조회 오류: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        
        # 에러도 Railway 로그에 출력
        error_log = {
            "event": "query_error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "railway_status": "error"
        }
        print(f"🚂 RAILWAY QUERY ERROR LOG: {json.dumps(error_log, indent=2, ensure_ascii=False)}")
        logger.error(f"RAILWAY_QUERY_ERROR_LOG: {json.dumps(error_log, ensure_ascii=False)}")
        
        raise HTTPException(status_code=500, detail=error_msg)

# 사용자 정보 엔드포인트
@gateway_router.get("/auth/me", summary="사용자 정보 조회")
async def get_user_info(request: Request):
    # 실제로는 JWT 토큰을 검증해야 함
    return {
        "status": "success",
        "user": {
            "id": "user123",
            "name": "테스트 사용자",
            "email": "test@example.com"
        }
    }

# 회원가입 페이지 (HTML)
@app.get("/signup", summary="회원가입 페이지")
async def signup_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>회원가입</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div class="w-full max-w-md">
            <div class="bg-white rounded-3xl shadow-2xl px-8 py-12">
                <!-- Signup Title -->
                <div class="text-center mb-12">
                    <h1 class="text-4xl font-bold text-gray-900 tracking-tight mb-2">
                        Flow Master 등록
                    </h1>
                    <p class="text-gray-600">
                        새로운 flow_master 데이터를 생성하세요
                    </p>
                </div>

                <!-- Signup Form -->
                <form id="signupForm" class="space-y-6">
                    <!-- Name Input - 필수 -->
                    <div class="relative">
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                            이름 <span class="text-red-500">*</span>
                        </label>
                        <input
                            type="text"
                            id="name"
                            name="name"
                            placeholder="이름을 입력하세요"
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
                            required
                        />
                    </div>

                    <!-- Type Input - 선택 -->
                    <div class="relative">
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                            타입
                        </label>
                        <select
                            id="type"
                            name="type"
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
                        >
                            <option value="">타입을 선택하세요</option>
                            <option value="process">Process</option>
                            <option value="workflow">Workflow</option>
                            <option value="automation">Automation</option>
                            <option value="manual">Manual</option>
                        </select>
                    </div>

                    <!-- Category Input - 선택 -->
                    <div class="relative">
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                            카테고리
                        </label>
                        <select
                            id="category"
                            name="category"
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
                        >
                            <option value="">카테고리를 선택하세요</option>
                            <option value="business">Business</option>
                            <option value="technical">Technical</option>
                            <option value="operational">Operational</option>
                            <option value="management">Management</option>
                        </select>
                    </div>

                    <!-- Unit ID Input - 선택 -->
                    <div class="relative">
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                            Unit ID
                        </label>
                        <input
                            type="text"
                            id="unit_id"
                            name="unit_id"
                            placeholder="Unit ID (자동 생성됨)"
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200 bg-gray-50"
                            readonly
                        />
                        <p class="text-xs text-gray-500 mt-1">Unit ID는 자동으로 생성됩니다.</p>
                    </div>

                    <!-- Error Message -->
                    <div id="errorMessage" class="bg-red-50 border border-red-200 rounded-lg p-3 hidden">
                        <p class="text-red-600 text-sm"></p>
                    </div>

                    <!-- Signup Button -->
                    <button
                        type="submit"
                        id="signupButton"
                        class="w-full bg-blue-600 text-white py-4 rounded-2xl hover:bg-blue-700 transition-all duration-200 font-medium text-lg shadow-sm"
                    >
                        Flow Master 생성 (axios 전송)
                    </button>
                </form>

                <!-- Divider -->
                <div class="mt-8">
                    <div class="relative">
                        <div class="absolute inset-0 flex items-center">
                            <div class="w-full border-t border-gray-300" />
                        </div>
                        <div class="relative flex justify-center text-sm">
                            <span class="px-2 bg-white text-gray-500">또는</span>
                        </div>
                    </div>
                </div>

                <!-- Login Link -->
                <div class="mt-6 text-center">
                    <p class="text-gray-600 text-sm">
                        이미 계정이 있으신가요? 
                        <button onclick="window.location.href='/'" class="text-blue-600 hover:text-blue-700 font-medium">
                            로그인
                        </button>
                    </p>
                </div>
            </div>
        </div>

        <script>
        // UUID 생성 함수
        function generateUUID() {
            return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                const r = Math.random() * 16 | 0;
                const v = c === 'x' ? r : (r & 0x3 | 0x8);
                return v.toString(16);
            });
        }

        // Unit ID 자동 생성
        document.getElementById('unit_id').value = generateUUID();

        document.getElementById('signupForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const signupButton = document.getElementById('signupButton');
            const errorMessage = document.getElementById('errorMessage');
            
            // 필수 필드 확인
            const name = document.getElementById('name').value.trim();
            if (!name) {
                errorMessage.querySelector('p').textContent = '이름은 필수 입력 항목입니다.';
                errorMessage.classList.remove('hidden');
                return;
            }

            // 버튼 비활성화
            signupButton.disabled = true;
            signupButton.textContent = '생성 중...';
            errorMessage.classList.add('hidden');

            // flow_master 테이블 구조에 맞는 데이터 생성
            const signupData = {
                id: generateUUID(),
                name: name,
                type: document.getElementById('type').value || null,
                category: document.getElementById('category').value || null,
                unit_id: document.getElementById('unit_id').value || generateUUID()
            };

            try {
                console.log('🚀 회원가입 데이터 전송 시작...');
                const response = await fetch('/api/v1/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(signupData)
                });

                const result = await response.json();
                console.log('✅ 회원가입 성공:', result);

                if (response.ok) {
                    // 성공 메시지 - JSON 형태로 alert 표시
                    const inputData = {
                        name: {
                            name: name,
                            type: document.getElementById('type').value || null,
                            category: document.getElementById('category').value || null,
                            unit_id: document.getElementById('unit_id').value || generateUUID()
                        },
                        value: {
                            name: name,
                            type: document.getElementById('type').value || null,
                            category: document.getElementById('category').value || null,
                            unit_id: document.getElementById('unit_id').value || generateUUID()
                        }
                    };

                    alert('flow_master 데이터가 생성되었습니다!\\n\\n' + JSON.stringify(inputData, null, 2) + '\\n\\n서버 응답: ' + result.message);
                    
                    // 로그인 페이지로 이동
                    window.location.href = '/?message=flow_master 데이터가 생성되었습니다.';
                } else {
                    throw new Error(result.detail || '회원가입 실패');
                }
            } catch (error) {
                console.error('❌ 회원가입 실패:', error);
                errorMessage.querySelector('p').textContent = '회원가입 실패: ' + error.message;
                errorMessage.classList.remove('hidden');
            } finally {
                // 버튼 활성화
                signupButton.disabled = false;
                signupButton.textContent = 'Flow Master 생성 (axios 전송)';
            }
        });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# 새로운 프론트엔드 페이지 (Flow Master 등록 시스템)
@app.get("/frontend", summary="Flow Master 등록 시스템 프론트엔드")
async def frontend_page():
    """Flow Master 등록 시스템의 메인 프론트엔드 페이지"""
    try:
        with open("frontend.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        # 파일이 없을 경우 기본 HTML 반환
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Flow Master 등록 시스템</title>
        </head>
        <body>
            <h1>Flow Master 등록 시스템</h1>
            <p>프론트엔드 파일을 찾을 수 없습니다.</p>
            <p>frontend.html 파일이 gateway 디렉토리에 있는지 확인해주세요.</p>
        </body>
        </html>
        """)

# 대시보드 페이지 (HTML)
@app.get("/dashboard", summary="대시보드 페이지")
async def dashboard_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>대시보드</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="min-h-screen bg-gray-900 flex flex-col items-center justify-center p-4">
        <!-- Main Content -->
        <div class="w-full max-w-2xl">
            <!-- Title -->
            <div class="text-center mb-8">
                <h1 class="text-2xl font-medium text-white mb-4">
                    준비되면 얘기해 주세요.
                </h1>

                <!-- 로그인 데이터 표시 -->
                <div id="loginDataDisplay" class="bg-gray-800 rounded-lg p-4 mb-6 hidden">
                    <h2 class="text-lg font-medium text-white mb-3">저장된 로그인 데이터</h2>
                    <div class="bg-gray-700 rounded p-3 mb-4">
                        <pre id="loginDataJson" class="text-green-400 text-sm overflow-x-auto"></pre>
                    </div>

                    <!-- 전송 버튼 -->
                    <button
                        id="sendDataButton"
                        class="w-full bg-green-600 text-white py-4 px-6 rounded-lg font-bold text-lg hover:bg-green-700 focus:ring-4 focus:ring-green-500 focus:ring-offset-2 transition-all duration-200 shadow-lg"
                    >
                        🚀 JSON 데이터 전송 (axios)
                    </button>

                    <!-- 메시지 표시 -->
                    <div id="messageDisplay" class="mt-3 p-3 rounded-lg text-sm hidden"></div>
                </div>
            </div>

            <!-- Input Container -->
            <div class="relative">
                <form id="chatForm">
                    <div class="relative bg-gray-800 rounded-2xl shadow-lg border border-gray-700">
                        <div class="flex items-center px-4 py-3">
                            <!-- Plus Icon -->
                            <div class="flex items-center mr-3">
                                <button
                                    type="button"
                                    class="flex items-center text-gray-400 hover:text-gray-300 transition-colors duration-200"
                                >
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                                    </svg>
                                </button>
                            </div>

                            <!-- Input Field -->
                            <div class="flex-1">
                                <input
                                    type="text"
                                    id="chatInput"
                                    placeholder="무엇이든 물어보세요"
                                    class="w-full bg-transparent border-none outline-none text-white placeholder-gray-400 text-lg"
                                    required
                                />
                            </div>

                            <!-- Right Side Icons -->
                            <div class="flex items-center space-x-3 ml-3">
                                <!-- Microphone Icon -->
                                <button
                                    type="button"
                                    class="p-2 text-gray-400 hover:text-gray-300 transition-colors duration-200 rounded-full hover:bg-gray-700"
                                >
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                                    </svg>
                                </button>

                                <!-- Send Button -->
                                <button
                                    type="submit"
                                    class="p-2 text-gray-400 hover:text-gray-300 transition-colors duration-200 rounded-full hover:bg-gray-700"
                                >
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
        </div>

        <script>
        // 페이지 로드 시 localStorage에서 로그인 데이터 가져오기
        window.addEventListener('load', function() {
            const loginData = localStorage.getItem('loginData');
            if (loginData) {
                try {
                    const parsedData = JSON.parse(loginData);
                    document.getElementById('loginDataJson').textContent = JSON.stringify(parsedData, null, 2);
                    document.getElementById('loginDataDisplay').classList.remove('hidden');
                    console.log('저장된 로그인 데이터:', parsedData);
                } catch (error) {
                    console.error('로그인 데이터 파싱 오류:', error);
                }
            }
        });

        // JSON 데이터를 전송하는 함수
        document.getElementById('sendDataButton').addEventListener('click', async function() {
            const loginData = localStorage.getItem('loginData');
            const messageDisplay = document.getElementById('messageDisplay');
            const sendDataButton = document.getElementById('sendDataButton');

            if (!loginData) {
                messageDisplay.textContent = '전송할 로그인 데이터가 없습니다.';
                messageDisplay.className = 'mt-3 p-3 rounded-lg text-sm bg-red-900 text-red-300';
                messageDisplay.classList.remove('hidden');
                return;
            }

            try {
                const parsedData = JSON.parse(loginData);
                console.log('📤 전송할 데이터:', parsedData);
                
                sendDataButton.disabled = true;
                sendDataButton.textContent = '🔄 전송 중...';
                messageDisplay.classList.add('hidden');

                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(parsedData)
                });

                const result = await response.json();
                console.log('✅ 전송 성공!', result);

                messageDisplay.textContent = '✅ JSON 데이터가 성공적으로 전송되었습니다!';
                messageDisplay.className = 'mt-3 p-3 rounded-lg text-sm bg-green-900 text-green-300';
                messageDisplay.classList.remove('hidden');

            } catch (error) {
                console.error('❌ 전송 실패:', error);
                messageDisplay.textContent = '❌ 전송 실패: ' + error.message;
                messageDisplay.className = 'mt-3 p-3 rounded-lg text-sm bg-red-900 text-red-300';
                messageDisplay.classList.remove('hidden');
            } finally {
                sendDataButton.disabled = false;
                sendDataButton.textContent = '🚀 JSON 데이터 전송 (axios)';
            }
        });

        // 채팅 폼 제출
        document.getElementById('chatForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const inputValue = document.getElementById('chatInput').value;
            if (inputValue.trim()) {
                console.log('입력된 메시지:', inputValue);
                document.getElementById('chatInput').value = '';
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
    import os
    
    # Railway 환경변수에서 PORT 가져오기, 없으면 8080 사용
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)