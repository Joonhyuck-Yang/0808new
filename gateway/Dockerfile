# Python 3.11 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 포트 노출 (고정 포트)
EXPOSE 8080

# 환경변수 설정
ENV PYTHONPATH=/app
ENV RAILWAY_ENVIRONMENT=true
ENV PORT=8080

# FastAPI 서버 실행 (Railway 환경변수 $PORT 사용)
CMD python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
