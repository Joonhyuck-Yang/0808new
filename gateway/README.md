# MSA API Gateway

FastAPI 기반의 마이크로서비스 아키텍처 API Gateway입니다. 프록시 패턴을 사용하여 서비스 디스커버리와 로드 밸런싱을 제공합니다.

## 주요 기능

- **프록시 패턴**: 모든 서비스 요청을 적절한 마이크로서비스로 라우팅
- **서비스 디스커버리**: Consul, Redis, 정적 설정을 통한 서비스 발견
- **로드 밸런싱**: 라운드 로빈 방식의 로드 밸런싱
- **헬스체크**: 서비스 인스턴스 상태 모니터링
- **메트릭 수집**: Prometheus 메트릭 수집
- **구조화된 로깅**: JSON 형태의 구조화된 로그

## 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client        │    │   API Gateway   │    │   Microservice  │
│                 │───▶│                 │───▶│                 │
│                 │    │  - Proxy        │    │                 │
│                 │    │  - Discovery    │    │                 │
│                 │    │  - Load Balance │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Service Registry│
                       │ (Consul/Redis)  │
                       └─────────────────┘
```

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 필요한 설정을 추가하세요:

```env
# 기본 설정
HOST=0.0.0.0
PORT=8000
DEBUG=false

# 서비스 디스커버리 설정
SERVICE_DISCOVERY_TYPE=static  # consul, redis, static

# Consul 설정 (SERVICE_DISCOVERY_TYPE=consul인 경우)
CONSUL_HOST=localhost
CONSUL_PORT=8500

# Redis 설정 (SERVICE_DISCOVERY_TYPE=redis인 경우)
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 3. 애플리케이션 실행

```bash
# 개발 모드
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 모드
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Docker 실행

```bash
# 이미지 빌드
docker build -t msa-gateway .

# 컨테이너 실행
docker run -p 8000:8000 msa-gateway
```

## API 엔드포인트

### 게이트웨이 정보
- `GET /` - 게이트웨이 상태 확인
- `GET /health/` - 헬스체크
- `GET /health/ready` - 준비 상태 확인
- `GET /health/live` - 생존 상태 확인
- `GET /metrics/` - Prometheus 메트릭

### 서비스 관리
- `GET /services` - 등록된 서비스 목록
- `GET /services/{service_name}/health` - 서비스 헬스체크
- `GET /services/{service_name}/info` - 서비스 정보

### 프록시 요청
- `GET /{service_name}/{path}` - 서비스로 요청 프록시
- `POST /{service_name}/{path}` - 서비스로 요청 프록시
- `PUT /{service_name}/{path}` - 서비스로 요청 프록시
- `DELETE /{service_name}/{path}` - 서비스로 요청 프록시

## 서비스 디스커버리

### 1. 정적 설정 (기본값)

`app/common/config.py`의 `SERVICE_MAPPINGS`에서 서비스 정보를 설정:

```python
SERVICE_MAPPINGS = {
    "user-service": {
        "host": "localhost",
        "port": 8001,
        "health_check": "/health"
    },
    "order-service": {
        "host": "localhost", 
        "port": 8002,
        "health_check": "/health"
    }
}
```

### 2. Consul 사용

Consul 서버를 실행하고 환경 변수를 설정:

```env
SERVICE_DISCOVERY_TYPE=consul
CONSUL_HOST=localhost
CONSUL_PORT=8500
```

### 3. Redis 사용

Redis 서버를 실행하고 환경 변수를 설정:

```env
SERVICE_DISCOVERY_TYPE=redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 사용 예시

### 1. 사용자 서비스 호출

```bash
# 사용자 목록 조회
curl http://localhost:8000/user-service/users

# 사용자 생성
curl -X POST http://localhost:8000/user-service/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

### 2. 주문 서비스 호출

```bash
# 주문 목록 조회
curl http://localhost:8000/order-service/orders

# 주문 생성
curl -X POST http://localhost:8000/order-service/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "items": [{"product_id": 1, "quantity": 2}]}'
```

### 3. 서비스 상태 확인

```bash
# 모든 서비스 목록
curl http://localhost:8000/services

# 특정 서비스 헬스체크
curl http://localhost:8000/services/user-service/health

# 게이트웨이 헬스체크
curl http://localhost:8000/health/
```

## 모니터링

### 메트릭 확인

```bash
curl http://localhost:8000/metrics/
```

### 로그 확인

애플리케이션은 JSON 형태의 구조화된 로그를 출력합니다:

```json
{
  "timestamp": "2024-01-01T00:00:00.000Z",
  "level": "info",
  "logger": "gateway.request",
  "event": "Incoming request",
  "method": "GET",
  "url": "http://localhost:8000/user-service/users"
}
```

## 개발

### 프로젝트 구조

```
gateway/
├── app/
│   ├── common/
│   │   ├── config.py          # 설정 관리
│   │   └── logging.py         # 로깅 설정
│   ├── domain/
│   │   ├── service_discovery.py  # 서비스 디스커버리
│   │   └── proxy_service.py      # 프록시 서비스
│   ├── router/
│   │   ├── proxy_router.py    # 프록시 라우터
│   │   ├── health_router.py   # 헬스체크 라우터
│   │   └── metrics_router.py  # 메트릭 라우터
│   └── main.py                # 메인 애플리케이션
├── requirements.txt           # Python 의존성
├── Dockerfile                 # Docker 설정
└── README.md                  # 프로젝트 문서
```

### 테스트

```bash
# 단위 테스트 실행
pytest

# 통합 테스트 실행
pytest tests/integration/
```

## 라이센스

MIT License 