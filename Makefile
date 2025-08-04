# 🚀 GreenSteel MSA 프로젝트 Makefile

.PHONY: help up down logs restart ps clean

# 기본 명령어
help: ## 도움말 보기
	@echo "🚀 GreenSteel MSA 프로젝트 명령어"
	@echo ""
	@echo "📋 전체 시스템 명령어:"
	@echo "  make up          - 전체 서비스 시작 (백그라운드)"
	@echo "  make down        - 전체 서비스 중지"
	@echo "  make logs        - 전체 로그 확인"
	@echo "  make restart     - 전체 서비스 재시작"
	@echo "  make ps          - 실행 중인 컨테이너 확인"
	@echo "  make clean       - 모든 컨테이너와 이미지 정리"
	@echo ""
	@echo "🔧 개별 서비스 명령어:"
	@echo "  make up-gateway      - Gateway 서비스만 시작"
	@echo "  make up-auth         - Auth 서비스만 시작"
	@echo "  make up-cbam         - CBAM 서비스만 시작"
	@echo "  make up-chatbot      - Chatbot 서비스만 시작"
	@echo "  make up-report       - Report 서비스만 시작"
	@echo "  make up-redis        - Redis만 시작"
	@echo "  make up-n8n          - N8N만 시작"
	@echo ""
	@echo "📝 로그 확인:"
	@echo "  make logs-gateway    - Gateway 로그"
	@echo "  make logs-auth       - Auth 로그"
	@echo "  make logs-cbam       - CBAM 로그"
	@echo "  make logs-chatbot    - Chatbot 로그"
	@echo "  make logs-report     - Report 로그"
	@echo "  make logs-redis      - Redis 로그"
	@echo "  make logs-n8n        - N8N 로그"

# 전체 시스템 명령어
up: ## 전체 서비스 시작 (백그라운드)
	docker-compose up -d --build

down: ## 전체 서비스 중지
	docker-compose down

logs: ## 전체 로그 확인
	docker-compose logs -f

restart: ## 전체 서비스 재시작
	docker-compose down && docker-compose up -d --build

ps: ## 실행 중인 컨테이너 확인
	docker-compose ps

clean: ## 모든 컨테이너와 이미지 정리
	docker-compose down -v --rmi all
	docker system prune -f

# 🚀 마이크로서비스별 명령어

## Gateway
build-gateway: ## Gateway 빌드
	docker-compose build gateway

up-gateway: ## Gateway 서비스만 시작
	docker-compose up -d gateway

down-gateway: ## Gateway 서비스만 중지
	docker-compose stop gateway

logs-gateway: ## Gateway 로그 확인
	docker-compose logs -f gateway

restart-gateway: ## Gateway 재시작
	docker-compose stop gateway && docker-compose up -d gateway

## Auth Service
build-auth: ## Auth Service 빌드
	docker-compose build auth-service

up-auth: ## Auth Service만 시작
	docker-compose up -d auth-service

down-auth: ## Auth Service만 중지
	docker-compose stop auth-service

logs-auth: ## Auth Service 로그 확인
	docker-compose logs -f auth-service

restart-auth: ## Auth Service 재시작
	docker-compose stop auth-service && docker-compose up -d auth-service

## CBAM Service
build-cbam: ## CBAM Service 빌드
	docker-compose build cbam-service

up-cbam: ## CBAM Service만 시작
	docker-compose up -d cbam-service

down-cbam: ## CBAM Service만 중지
	docker-compose stop cbam-service

logs-cbam: ## CBAM Service 로그 확인
	docker-compose logs -f cbam-service

restart-cbam: ## CBAM Service 재시작
	docker-compose stop cbam-service && docker-compose up -d cbam-service

## Chatbot Service
build-chatbot: ## Chatbot Service 빌드
	docker-compose build chatbot-service

up-chatbot: ## Chatbot Service만 시작
	docker-compose up -d chatbot-service

down-chatbot: ## Chatbot Service만 중지
	docker-compose stop chatbot-service

logs-chatbot: ## Chatbot Service 로그 확인
	docker-compose logs -f chatbot-service

restart-chatbot: ## Chatbot Service 재시작
	docker-compose stop chatbot-service && docker-compose up -d chatbot-service

## Report Service
build-report: ## Report Service 빌드
	docker-compose build report-service

up-report: ## Report Service만 시작
	docker-compose up -d report-service

down-report: ## Report Service만 중지
	docker-compose stop report-service

logs-report: ## Report Service 로그 확인
	docker-compose logs -f report-service

restart-report: ## Report Service 재시작
	docker-compose stop report-service && docker-compose up -d report-service

## Redis
up-redis: ## Redis만 시작
	docker-compose up -d redis

down-redis: ## Redis만 중지
	docker-compose stop redis

logs-redis: ## Redis 로그 확인
	docker-compose logs -f redis

restart-redis: ## Redis 재시작
	docker-compose stop redis && docker-compose up -d redis

## N8N
build-n8n: ## N8N 빌드
	docker-compose build n8n

up-n8n: ## N8N만 시작
	docker-compose up -d n8n

down-n8n: ## N8N만 중지
	docker-compose stop n8n

logs-n8n: ## N8N 로그 확인
	docker-compose logs -f n8n

restart-n8n: ## N8N 재시작
	docker-compose stop n8n && docker-compose up -d n8n

# 🔧 개발 도구 명령어
shell-gateway: ## Gateway 컨테이너에 접속
	docker-compose exec gateway /bin/bash

shell-auth: ## Auth Service 컨테이너에 접속
	docker-compose exec auth-service /bin/bash

shell-cbam: ## CBAM Service 컨테이너에 접속
	docker-compose exec cbam-service /bin/bash

shell-chatbot: ## Chatbot Service 컨테이너에 접속
	docker-compose exec chatbot-service /bin/bash

shell-report: ## Report Service 컨테이너에 접속
	docker-compose exec report-service /bin/bash

shell-redis: ## Redis 컨테이너에 접속
	docker-compose exec redis redis-cli

# 📊 모니터링 명령어
status: ## 모든 서비스 상태 확인
	@echo "🔍 서비스 상태 확인 중..."
	docker-compose ps
	@echo ""
	@echo "🌐 서비스 엔드포인트:"
	@echo "  Gateway:     http://localhost:8080"
	@echo "  Auth:        http://localhost:8001"
	@echo "  CBAM:        http://localhost:8002"
	@echo "  Chatbot:     http://localhost:8003"
	@echo "  Report:      http://localhost:8004"
	@echo "  Redis:       localhost:6379"
	@echo "  N8N:         http://localhost:5678"

health: ## 모든 서비스 헬스체크
	@echo "🏥 서비스 헬스체크 중..."
	@curl -s http://localhost:8080/health || echo "Gateway: ❌"
	@curl -s http://localhost:8001/health || echo "Auth: ❌"
	@curl -s http://localhost:8002/health || echo "CBAM: ❌"
	@curl -s http://localhost:8003/health || echo "Chatbot: ❌"
	@curl -s http://localhost:8004/health || echo "Report: ❌" 