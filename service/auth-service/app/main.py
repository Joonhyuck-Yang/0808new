# Auth Service - 회원가입 및 인증 처리
import os
import sys
import logging
import json
import httpx
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Railway 환경 확인 (Gateway와 동일)
IS_RAILWAY = os.getenv("RAILWAY_ENVIRONMENT") == "true" or os.getenv("PORT") is not None

# 로깅 설정 (Gateway와 동일)
if IS_RAILWAY:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    print("🚂 Auth Service - Railway 환경에서 실행 중 - 포트 8001")
else:
    logging.basicConfig(level=logging.INFO)
    print("🏠 Auth Service - 로컬 환경에서 실행 중")

logger = logging.getLogger("auth_service")

# 비동기 HTTP 클라이언트 (싱글톤 패턴 - Gateway와 동일)
_http_client: httpx.AsyncClient = None

async def get_http_client() -> httpx.AsyncClient:
    """비동기 HTTP 클라이언트 싱글톤 반환 (Gateway와 동일)"""
    global _http_client
    if _http_client is None:
        timeout = int(os.getenv("HTTP_TIMEOUT", "30"))
        max_keepalive = int(os.getenv("HTTP_MAX_KEEPALIVE", "20"))
        max_connections = int(os.getenv("HTTP_MAX_CONNECTIONS", "100"))
        
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=max_keepalive, max_connections=max_connections)
        )
    return _http_client

async def close_http_client():
    """HTTP 클라이언트 정리 (Gateway와 동일)"""
    global _http_client
    if _http_client:
        await _http_client.aclose()
        _http_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Auth Service 시작 (포트 8001)")
    # HTTP 클라이언트 초기화 (Gateway와 동일)
    await get_http_client()
    yield
    # HTTP 클라이언트 정리 (Gateway와 동일)
    await close_http_client()
    logger.info("🛑 Auth Service 종료")

app = FastAPI(
    title="Auth Service",
    description="Authentication and Authorization Service (포트 8001)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/signup")
async def signup(request: Request):
    """회원가입 처리 - name과 pass만 저장"""
    try:
        # 요청 시작 로그
        start_time = datetime.now()
        print(f"🚂 AUTH SERVICE SIGNUP START: {start_time.isoformat()}")
        logger.info(f"AUTH_SERVICE_SIGNUP_START: {start_time.isoformat()}")
        
        body = await request.json()
        
        # name과 pass만 추출
        user_name = body.get("name", "")
        user_pass = body.get("pass", "")
        
        # 입력 데이터 검증 로그
        validation_log = {
            "event": "signup_validation",
            "timestamp": datetime.now().isoformat(),
            "input_data": {
                "name": user_name,
                "pass": user_pass
            },
            "validation": {
                "name_length": len(user_name),
                "pass_length": len(user_pass),
                "name_empty": not user_name,
                "pass_empty": not user_pass
            },
            "source": "auth_service",
            "environment": "railway"
        }
        print(f"🚂 AUTH SERVICE VALIDATION LOG: {json.dumps(validation_log, indent=2, ensure_ascii=False)}")
        logger.info(f"AUTH_SERVICE_VALIDATION_LOG: {json.dumps(validation_log, ensure_ascii=False)}")
        
        # 입력 검증
        if not user_name or not user_pass:
            error_msg = "아이디와 비밀번호를 모두 입력해주세요"
            print(f"❌ AUTH SERVICE VALIDATION ERROR: {error_msg}")
            logger.error(f"AUTH_SERVICE_VALIDATION_ERROR: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Railway 로그에 JSON 형태로 출력 (name과 pass만)
        railway_log_data = {
            "event": "user_signup",
            "timestamp": datetime.now().isoformat(),
            "user_data": {
                "name": user_name,
                "pass": user_pass
            },
            "source": "auth_service",
            "environment": "railway",
            "request_id": f"signup_{start_time.strftime('%Y%m%d_%H%M%S')}"
        }
        
        # Railway 로그에 출력 (중요!)
        print(f"🚂 AUTH SERVICE RAILWAY LOG: {json.dumps(railway_log_data, indent=2, ensure_ascii=False)}")
        logger.info(f"AUTH_SERVICE_RAILWAY_LOG: {json.dumps(railway_log_data, ensure_ascii=False)}")
        
        # 성공 응답 (name과 pass만)
        response_data = {
            "status": "success",
            "message": "회원가입 성공!",
            "data": {
                "name": user_name,
                "pass": user_pass
            },
            "railway_logged": True,
            "service": "auth-service",
            "request_id": railway_log_data["request_id"]
        }
        
        # Railway 로그에 최종 결과도 출력
        final_log = {
            "event": "signup_completed",
            "timestamp": datetime.now().isoformat(),
            "result": response_data,
            "railway_status": "success",
            "service": "auth-service",
            "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000
        }
        print(f"🚂 AUTH SERVICE FINAL LOG: {json.dumps(final_log, indent=2, ensure_ascii=False)}")
        logger.info(f"AUTH_SERVICE_FINAL_LOG: {json.dumps(final_log, ensure_ascii=False)}")
        
        return response_data
        
    except Exception as e:
        error_msg = f"회원가입 오류: {str(e)}"
        print(f"❌ AUTH SERVICE ERROR: {error_msg}")
        logger.error(error_msg)
        
        # 에러도 Railway 로그에 출력
        error_log = {
            "event": "signup_error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "railway_status": "error",
            "service": "auth-service",
            "request_id": f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        print(f"🚂 AUTH SERVICE ERROR LOG: {json.dumps(error_log, indent=2, ensure_ascii=False)}")
        logger.error(f"AUTH_SERVICE_ERROR_LOG: {json.dumps(error_log, ensure_ascii=False)}")
        
        raise HTTPException(status_code=500, detail=f"회원가입 실패: {str(e)}")

@app.post("/login")
async def login(request: Request):
    """로그인 처리"""
    try:
        start_time = datetime.now()
        print(f"🚂 AUTH SERVICE LOGIN START: {start_time.isoformat()}")
        logger.info(f"AUTH_SERVICE_LOGIN_START: {start_time.isoformat()}")
        
        body = await request.json()
        user_name = body.get("name", "")
        user_pass = body.get("pass", "")
        
        # 로그인 시도 로그
        login_attempt_log = {
            "event": "login_attempt",
            "timestamp": datetime.now().isoformat(),
            "user_name": user_name,
            "source": "auth_service",
            "environment": "railway"
        }
        print(f"🚂 AUTH SERVICE LOGIN ATTEMPT: {json.dumps(login_attempt_log, indent=2, ensure_ascii=False)}")
        logger.info(f"AUTH_SERVICE_LOGIN_ATTEMPT: {json.dumps(login_attempt_log, ensure_ascii=False)}")
        
        # 간단한 로그인 검증 (실제로는 데이터베이스 확인 필요)
        if user_name and user_pass:
            success_log = {
                "event": "login_success",
                "timestamp": datetime.now().isoformat(),
                "user_name": user_name,
                "source": "auth_service",
                "environment": "railway",
                "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000
            }
            print(f"🚂 AUTH SERVICE LOGIN SUCCESS: {json.dumps(success_log, indent=2, ensure_ascii=False)}")
            logger.info(f"AUTH_SERVICE_LOGIN_SUCCESS: {json.dumps(success_log, ensure_ascii=False)}")
            
            return {
                "status": "success",
                "message": "로그인 성공!",
                "user": {"name": user_name},
                "service": "auth-service"
            }
        else:
            error_msg = "아이디와 비밀번호를 입력해주세요"
            print(f"❌ AUTH SERVICE LOGIN ERROR: {error_msg}")
            logger.error(f"AUTH_SERVICE_LOGIN_ERROR: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
            
    except Exception as e:
        logger.error(f"로그인 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"로그인 실패: {str(e)}")

@app.get("/status")
async def service_status():
    """서비스 상태 확인"""
    status_data = {
        "service": "auth-service",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "environment": "railway" if IS_RAILWAY else "local",
        "endpoints": [
            "/signup",
            "/login",
            "/status"
        ]
    }
    
    if IS_RAILWAY:
        print(f"🚂 AUTH SERVICE STATUS: {json.dumps(status_data, indent=2, ensure_ascii=False)}")
        logger.info(f"AUTH_SERVICE_STATUS: {json.dumps(status_data, ensure_ascii=False)}")
    
    return status_data

# 외부 API 호출 테스트 엔드포인트
@app.get("/test-external")
async def test_external_api():
    """외부 API 호출 테스트"""
    try:
        client = await get_http_client()
        
        # Gateway 서비스 호출 테스트
        gateway_url = os.getenv("GATEWAY_URL", "https://gateway-production-be21.up.railway.app")
        response = await client.get(f"{gateway_url}/api/v1/health")
        
        test_result = {
            "status": "success",
            "gateway_health": response.json(),
            "timestamp": datetime.now().isoformat(),
            "service": "auth-service"
        }
        
        if IS_RAILWAY:
            print(f"🚂 AUTH SERVICE EXTERNAL TEST: {json.dumps(test_result, indent=2, ensure_ascii=False)}")
            logger.info(f"AUTH_SERVICE_EXTERNAL_TEST: {json.dumps(test_result, indent=2, ensure_ascii=False)}")
        
        return test_result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "service": "auth-service"
        }
        
        if IS_RAILWAY:
            print(f"❌ AUTH SERVICE EXTERNAL TEST ERROR: {json.dumps(error_result, indent=2, ensure_ascii=False)}")
            logger.error(f"AUTH_SERVICE_EXTERNAL_TEST_ERROR: {json.dumps(error_result, ensure_ascii=False)}")
        
        raise HTTPException(status_code=500, detail=f"외부 API 테스트 실패: {str(e)}")

# Docker에서 uvicorn으로 실행되므로 직접 실행 코드 제거 (Gateway와 완전히 동일)
