# Railway 배포 가이드

## 🚀 Railway로 MSA API Gateway 배포하기

### 1. Railway CLI 설치
```bash
npm install -g @railway/cli
```

### 2. Railway 로그인
```bash
railway login
```

### 3. 프로젝트 초기화
```bash
railway init
```

### 4. 환경 변수 설정
Railway 대시보드에서 다음 환경 변수를 설정하세요:

```env
HOST=0.0.0.0
DEBUG=false
SERVICE_DISCOVERY_TYPE=static
LOG_LEVEL=INFO
LOG_FORMAT=json
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENABLE_METRICS=true
PROXY_TIMEOUT=30
PROXY_MAX_RETRIES=3
PROXY_RETRY_DELAY=1.0
```

### 5. 배포
```bash
railway up
```

### 6. 도메인 확인
```bash
railway domain
```

## 📋 배포 후 확인사항

### API 엔드포인트
- **루트**: `https://your-app.railway.app/`
- **Swagger UI**: `https://your-app.railway.app/docs`
- **ReDoc**: `https://your-app.railway.app/redoc`
- **헬스체크**: `https://your-app.railway.app/health/`
- **서비스 목록**: `https://your-app.railway.app/services`

### 서비스 프록시
- **사용자 서비스**: `https://your-app.railway.app/user-service/`
- **주문 서비스**: `https://your-app.railway.app/order-service/`
- **상품 서비스**: `https://your-app.railway.app/product-service/`

## 🔧 문제 해결

### 로그 확인
```bash
railway logs
```

### 재배포
```bash
railway up --detach
```

### 환경 변수 업데이트
```bash
railway variables set KEY=VALUE
```

## 📊 모니터링

Railway 대시보드에서 다음을 확인할 수 있습니다:
- 실시간 로그
- 리소스 사용량
- 배포 상태
- 헬스체크 결과 