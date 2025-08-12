# Auth Service - 회원가입 및 인증 처리
import os
import sys
import logging
import json
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Railway 환경 확인
IS_RAILWAY = os.getenv("RAILWAY_ENVIRONMENT") == "true" or os.getenv("PORT") is not None

# 로깅 설정
if IS_RAILWAY:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    print("🚂 Auth Service - Railway 환경에서 실행 중")
else:
    logging.basicConfig(level=logging.INFO)
    print("🏠 Auth Service - 로컬 환경에서 실행 중")

logger = logging.getLogger("auth_service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Auth Service 시작")
    yield
    logger.info("🛑 Auth Service 종료")

app = FastAPI(
    title="Auth Service",
    description="Authentication and Authorization Service",
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

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "service": "auth-service"}

@app.post("/signup")
async def signup(request: Request):
    """회원가입 처리 - name과 pass만 저장"""
    try:
        body = await request.json()
        
        # name과 pass만 추출
        user_name = body.get("name", "")
        user_pass = body.get("pass", "")
        
        # Railway 로그에 JSON 형태로 출력 (name과 pass만)
        railway_log_data = {
            "event": "user_signup",
            "timestamp": datetime.now().isoformat(),
            "user_data": {
                "name": user_name,
                "pass": user_pass
            },
            "source": "auth_service",
            "environment": "railway"
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
            "service": "auth-service"
        }
        
        # Railway 로그에 최종 결과도 출력
        final_log = {
            "event": "signup_completed",
            "timestamp": datetime.now().isoformat(),
            "result": response_data,
            "railway_status": "success",
            "service": "auth-service"
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
            "service": "auth-service"
        }
        print(f"🚂 AUTH SERVICE ERROR LOG: {json.dumps(error_log, indent=2, ensure_ascii=False)}")
        logger.error(f"AUTH_SERVICE_ERROR_LOG: {json.dumps(error_log, ensure_ascii=False)}")
        
        raise HTTPException(status_code=500, detail=f"회원가입 실패: {str(e)}")

@app.post("/login")
async def login(request: Request):
    """로그인 처리"""
    try:
        body = await request.json()
        user_name = body.get("name", "")
        user_pass = body.get("pass", "")
        
        # 간단한 로그인 검증 (실제로는 데이터베이스 확인 필요)
        if user_name and user_pass:
            return {
                "status": "success",
                "message": "로그인 성공!",
                "user": {"name": user_name},
                "service": "auth-service"
            }
        else:
            raise HTTPException(status_code=400, detail="아이디와 비밀번호를 입력해주세요")
            
    except Exception as e:
        logger.error(f"로그인 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"로그인 실패: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Railway 환경변수에서 PORT 가져오기, 없으면 8000 사용
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
