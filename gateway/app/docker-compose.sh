#!/bin/bash

# MSA API Gateway Docker Compose 실행 스크립트

set -e

echo "🚀 MSA API Gateway Docker Compose 시작..."

# 필요한 디렉토리 생성
mkdir -p nginx/ssl
mkdir -p grafana/dashboards
mkdir -p grafana/datasources

# SSL 인증서 생성 (자체 서명)
if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
    echo "🔐 SSL 인증서 생성 중..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=KR/ST=Seoul/L=Seoul/O=MSA/OU=IT/CN=localhost"
fi

# Docker Compose 실행
echo "🐳 Docker Compose 실행 중..."
docker-compose up -d

# 서비스 상태 확인
echo "📊 서비스 상태 확인 중..."
sleep 10

echo "✅ 모든 서비스가 시작되었습니다!"
echo ""
echo "🌐 접속 정보:"
echo "  - API Gateway: http://localhost:8000"
echo "  - Nginx (HTTPS): https://localhost"
echo "  - Consul UI: http://localhost:8500"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "📋 서비스 목록:"
docker-compose ps
echo ""
echo "📝 로그 확인:"
echo "  - 전체 로그: docker-compose logs -f"
echo "  - API Gateway 로그: docker-compose logs -f api-gateway"
echo ""
echo "🛑 중지하려면: docker-compose down" 