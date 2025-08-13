# Auth Service - 회원가입 처리 (간소화)
import os
import sys
import logging
import json
import asyncpg
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Railway 환경 확인
IS_RAILWAY = os.getenv("RAILWAY_ENVIRONMENT") == "true" or (os.getenv("PORT") is not None and os.getenv("PORT") != "")

# Railway 환경변수에서 PORT 가져오기, 없으면 8001 사용
# PORT가 None이거나 빈 문자열일 때 기본값 사용
def get_port():
    """안전하게 PORT 환경변수를 가져오는 함수"""
    port_str = os.getenv("PORT")
    if port_str is None or port_str == "":
        return 8001
    try:
        port = int(port_str)
        if port <= 0 or port > 65535:
            print(f"⚠️ 경고: PORT {port}가 유효하지 않습니다. 기본값 8001을 사용합니다.")
            return 8001
        return port
    except (ValueError, TypeError):
        print(f"⚠️ 경고: PORT '{port_str}'를 정수로 변환할 수 없습니다. 기본값 8001을 사용합니다.")
        return 8001

# 로깅 설정
if IS_RAILWAY:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    print("🚂 Auth Service - Railway 환경에서 실행 중")
    print("🚂 Auth Service - 배포 시작!")
else:
    logging.basicConfig(level=logging.INFO)
    print("🏠 Auth Service - 로컬 환경에서 실행 중")

logger = logging.getLogger("auth_service")

# Railway PostgreSQL 연결 설정
async def get_db_connection():
    """Railway PostgreSQL 데이터베이스 연결"""
    try:
        if IS_RAILWAY:
            # Railway 환경변수에서 DB 정보 가져오기
            database_url = os.getenv("DATABASE_URL")
            if database_url:
                conn = await asyncpg.connect(database_url)
                print(f"🚂 Auth Service - Railway DB 연결 성공")
                return conn
            else:
                print(f"⚠️ Auth Service - DATABASE_URL 환경변수 없음")
                return None
        else:
            # 로컬 환경에서는 연결하지 않음
            print(f"🏠 Auth Service - 로컬 환경, DB 연결 생략")
            return None
    except Exception as e:
        print(f"❌ Auth Service - DB 연결 실패: {str(e)}")
        logger.error(f"DB 연결 실패: {str(e)}")
        return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Auth Service 시작")
    # DB 연결 테스트
    db_conn = await get_db_connection()
    if db_conn:
        await db_conn.close()
        print("🚂 Auth Service - DB 연결 테스트 성공")
    yield
    logger.info("🛑 Auth Service 종료")

app = FastAPI(
    title="Auth Service",
    description="Authentication Service - 회원가입만 처리",
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
    """회원가입 처리 - Gateway에서 받은 id, pass를 그대로 DB에 저장"""
    try:
        # 요청 시작 로그
        start_time = datetime.now()
        print(f"🚂 AUTH SERVICE SIGNUP START: {start_time.isoformat()}")
        logger.info(f"AUTH_SERVICE_SIGNUP_START: {start_time.isoformat()}")
        
        body = await request.json()
        
        # Gateway에서 받은 id와 pass를 그대로 사용
        user_id = body.get("id", "")
        user_pass = body.get("pass", "")
        
        # 입력 데이터 검증 로그
        validation_log = {
            "event": "signup_validation",
            "timestamp": datetime.now().isoformat(),
            "input_data": {
                "id": user_id,
                "pass": user_pass
            },
            "validation": {
                "id_length": len(user_id),
                "pass_length": len(user_pass),
                "id_empty": not user_id,
                "pass_empty": not user_pass
            },
            "source": "auth_service",
            "environment": "railway",
            "message": "Gateway에서 받은 데이터를 그대로 사용"
        }
        print(f"🚂 AUTH SERVICE VALIDATION LOG: {json.dumps(validation_log, indent=2, ensure_ascii=False)}")
        logger.info(f"AUTH_SERVICE_VALIDATION_LOG: {json.dumps(validation_log, ensure_ascii=False)}")
        
        # 입력 검증
        if not user_id or not user_pass:
            error_msg = "아이디와 비밀번호를 모두 입력해주세요"
            print(f"❌ AUTH SERVICE VALIDATION ERROR: {error_msg}")
            logger.error(f"AUTH_SERVICE_VALIDATION_ERROR: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Railway DB에 사용자 정보 저장 (받은 데이터를 그대로 저장)
        db_saved = False
        try:
            if IS_RAILWAY:
                db_conn = await get_db_connection()
                if db_conn:
                    # users 테이블 생성 (없는 경우)
                    await db_conn.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            username VARCHAR(100) UNIQUE NOT NULL,
                            password VARCHAR(255) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Gateway에서 받은 id, pass를 그대로 DB에 저장
                    await db_conn.execute(
                        "INSERT INTO users (username, password) VALUES ($1, $2)",
                        user_id, user_pass
                    )
                    
                    await db_conn.close()
                    db_saved = True
                    print(f"🚂 AUTH SERVICE - DB 저장 성공: {user_id}")
                    
                    # Railway 로그에 DB 저장 성공 메시지 출력
                    db_success_log = {
                        "event": "db_save_success",
                        "timestamp": datetime.now().isoformat(),
                        "user_id": user_id,
                        "message": "Gateway에서 받은 사용자 정보가 Railway PostgreSQL DB에 성공적으로 저장되었습니다!",
                        "db_table": "users",
                        "db_columns": ["username", "password"],
                        "data_source": "Gateway 프록시",
                        "source": "auth_service",
                        "environment": "railway"
                    }
                    print(f"🚂 AUTH SERVICE DB SUCCESS: {json.dumps(db_success_log, indent=2, ensure_ascii=False)}")
                    logger.info(f"AUTH_SERVICE_DB_SUCCESS: {json.dumps(db_success_log, ensure_ascii=False)}")
                    
                else:
                    print(f"⚠️ AUTH SERVICE - DB 연결 실패, 저장 생략")
            else:
                print(f"🏠 AUTH SERVICE - 로컬 환경, DB 저장 생략")
        except Exception as db_error:
            print(f"❌ AUTH SERVICE - DB 저장 실패: {str(db_error)}")
            logger.error(f"DB 저장 실패: {str(db_error)}")
            # DB 저장 실패해도 계속 진행 (로깅만)
        
        # Railway 로그에 JSON 형태로 출력 (id와 pass만)
        railway_log_data = {
            "event": "user_signup",
            "timestamp": datetime.now().isoformat(),
            "user_data": {
                "id": user_id,
                "pass": user_pass
            },
            "db_saved": db_saved,
            "data_flow": "프론트엔드 → Gateway → Auth Service → Railway DB",
            "source": "auth_service",
            "environment": "railway",
            "request_id": f"signup_{start_time.strftime('%Y%m%d_%H%M%S')}"
        }
        
        # Railway 로그에 출력 (중요!)
        print(f"🚂 AUTH SERVICE RAILWAY LOG: {json.dumps(railway_log_data, indent=2, ensure_ascii=False)}")
        logger.info(f"AUTH_SERVICE_RAILWAY_LOG: {json.dumps(railway_log_data, ensure_ascii=False)}")
        
        # 성공 응답 (id와 pass만)
        response_data = {
            "status": "success",
            "message": "회원가입 성공!",
            "data": {
                "id": user_id,
                "pass": user_pass
            },
            "db_saved": db_saved,
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

@app.get("/status")
async def service_status():
    """서비스 상태 확인"""
    status_data = {
        "service": "auth-service",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "environment": "railway" if IS_RAILWAY else "local",
        "endpoints": [
            "/signup"
        ],
        "description": "회원가입만 처리하는 간소화된 Auth Service - Gateway에서 받은 데이터를 DB에 저장"
    }
    
    if IS_RAILWAY:
        print(f"🚂 AUTH SERVICE STATUS: {json.dumps(status_data, indent=2, ensure_ascii=False)}")
        logger.info(f"AUTH_SERVICE_STATUS: {json.dumps(status_data, ensure_ascii=False)}")
    
    return status_data

# Docker에서 uvicorn으로 실행되므로 직접 실행 코드 제거
