# Auth Service Dockerfile - Railway 배포용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사 (전체 app 폴더를 복사)
COPY app/ ./app/

# 포트 노출 (Railway 환경변수 사용)
EXPOSE ${PORT:-8001}

# 환경변수 설정
ENV PYTHONPATH=/app
ENV RAILWAY_ENVIRONMENT=true

# 간단하고 확실한 실행 명령어
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
