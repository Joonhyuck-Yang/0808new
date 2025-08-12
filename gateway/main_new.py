from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
import json
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway_api")

app = FastAPI(title="Gateway API", description="Gateway API for ausikor.com")

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (테스트용)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 헬스 체크 엔드포인트
@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy!", "message": "Gateway API is running"}

# 회원가입 엔드포인트
@app.post("/api/v1/signup")
async def signup(request: Request):
    try:
        body = await request.json()
        
        # Railway 로그에 JSON 형태로 출력
        railway_log_data = {
            "event": "user_signup",
            "timestamp": datetime.now().isoformat(),
            "user_data": body,
            "source": "gateway_api",
            "environment": "railway"
        }
        print(f"🚂 RAILWAY LOG JSON: {json.dumps(railway_log_data, indent=2, ensure_ascii=False)}")
        logger.info(f"RAILWAY_LOG_JSON: {json.dumps(railway_log_data, ensure_ascii=False)}")
        
        # 성공 응답
        response_data = {
            "status": "success",
            "message": "회원가입됨!",
            "data": body,
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
        
        return JSONResponse(
            status_code=500,
            content={"error": error_msg}
        )

# 회원가입 데이터 조회 엔드포인트
@app.get("/api/v1/signup/data")
async def get_signup_data():
    try:
        # Railway 로그에 데이터 조회 정보 출력
        railway_query_log = {
            "event": "data_query",
            "timestamp": datetime.now().isoformat(),
            "query_type": "signup_data",
            "source": "gateway_api",
            "environment": "railway"
        }
        print(f"🚂 RAILWAY QUERY LOG: {json.dumps(railway_query_log, indent=2, ensure_ascii=False)}")
        logger.info(f"RAILWAY_QUERY_LOG: {json.dumps(railway_query_log, ensure_ascii=False)}")
        
        # 임시 데이터 반환 (실제로는 데이터베이스에서 조회)
        sample_data = [
            {
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "name": "테스트 사용자",
                    "type": "manual",
                    "category": "business"
                }
            }
        ]
        
        response_data = {
            "status": "success",
            "message": "데이터 조회 완료",
            "data": sample_data,
            "count": len(sample_data),
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
        
        return JSONResponse(
            status_code=500,
            content={"error": error_msg}
        )

# 루트 엔드포인트
@app.get("/")
async def root():
    return {"message": "Gateway API is running!"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
