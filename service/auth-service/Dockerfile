# Auth Service Dockerfile (포트 8001 사용)
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출 (환경변수로 설정)
EXPOSE ${PORT:-8001}

# 환경변수 설정
ENV PORT=${PORT:-8001}
ENV PYTHONPATH=/app

# uvicorn으로 실행 (환경변수 PORT 사용)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}"]
