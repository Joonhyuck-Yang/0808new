# 🚀 Railway 배포 가이드

## 개요
이 프로젝트는 FastAPI 기반의 Flow Master 등록 시스템으로, Railway에서 배포하여 프론트엔드에서 입력한 값이 JSON 형태로 출력되는 시스템입니다.

## 🏗️ 시스템 구조

```
프론트엔드 (HTML) → Gateway API (FastAPI) → 데이터 저장 (JSON)
     ↓                    ↓                    ↓
  사용자 입력        API 처리 및 검증      Railway 서버에 저장
```

## 📋 주요 기능

1. **프론트엔드**: Flow Master 등록 폼 (`/frontend`)
2. **API 엔드포인트**: 
   - `POST /api/v1/signup` - Flow Master 생성
   - `GET /api/v1/signup/data` - 저장된 데이터 조회
   - `GET /api/v1/health` - 헬스체크
3. **데이터 저장**: JSON 형태로 Railway 서버에 저장
4. **데이터 히스토리**: 저장된 데이터 조회 및 표시

## 🐳 로컬 Docker 실행

### 1. Docker Compose로 실행
```bash
# 프로젝트 루트 디렉토리에서
docker-compose up --build
```

### 2. 개별 서비스 실행
```bash
# Gateway 서비스만 실행
cd gateway
docker build -f Dockerfile.railway -t flow-master-gateway .
docker run -p 8080:8080 -e PORT=8080 flow-master-gateway
```

## 🚂 Railway 배포

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

### 4. 환경변수 설정
Railway 대시보드에서 다음 환경변수를 설정:

```env
PORT=8080
AUTH_SERVICE_URL=http://localhost:8000
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://your-domain.com,http://localhost:3000
```

### 5. 배포
```bash
railway up
```

### 6. 도메인 설정
```bash
railway domain
```

## 🌐 Vercel 배포 (선택사항)

### 1. Vercel CLI 설치
```bash
npm install -g vercel
```

### 2. 프로젝트 배포
```bash
vercel --prod
```

## 📱 사용 방법

### 1. 프론트엔드 접속
- 로컬: `http://localhost:8080/frontend`
- Railway: `https://your-railway-domain.railway.app/frontend`

### 2. Flow Master 등록
1. 이름 입력 (필수)
2. 타입 선택 (선택)
3. 카테고리 선택 (선택)
4. 설명 입력 (선택)
5. "Flow Master 생성" 버튼 클릭

### 3. 데이터 확인
- 생성된 데이터는 자동으로 JSON 형태로 표시
- "히스토리 새로고침" 버튼으로 저장된 데이터 조회

## 🔧 API 테스트

### 1. 헬스체크
```bash
curl http://localhost:8080/api/v1/health
```

### 2. Flow Master 생성
```bash
curl -X POST http://localhost:8080/api/v1/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "테스트 Flow",
    "type": "process",
    "category": "business",
    "description": "테스트 설명"
  }'
```

### 3. 데이터 조회
```bash
curl http://localhost:8080/api/v1/signup/data
```

## 📊 데이터 구조

### 입력 데이터
```json
{
  "id": "uuid-string",
  "name": "Flow Master 이름",
  "type": "process|workflow|automation|manual",
  "category": "business|technical|operational|management",
  "description": "설명",
  "unit_id": "uuid-string",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 저장된 데이터
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "uuid-string",
    "name": "Flow Master 이름",
    "type": "process",
    "category": "business",
    "description": "설명",
    "unit_id": "uuid-string",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

## 🐛 문제 해결

### 1. 포트 충돌
```bash
# 포트 사용 확인
netstat -tulpn | grep :8080

# 다른 포트 사용
PORT=8081 docker-compose up
```

### 2. 권한 문제
```bash
# Docker 권한 설정
sudo usermod -aG docker $USER
```

### 3. 로그 확인
```bash
# Docker 로그
docker-compose logs gateway

# 개별 컨테이너 로그
docker logs <container_id>
```

## 📁 파일 구조

```
educated/
├── gateway/
│   ├── main.py              # FastAPI 메인 앱
│   ├── frontend.html        # 프론트엔드 페이지
│   ├── Dockerfile.railway   # Railway용 Dockerfile
│   ├── requirements.txt     # Python 의존성
│   └── railway.env         # Railway 환경변수
├── docker-compose.yml       # Docker Compose 설정
├── RAILWAY_DEPLOYMENT.md    # 이 문서
└── data/                    # 데이터 저장 디렉토리
```

## 🎯 다음 단계

1. **데이터베이스 연동**: PostgreSQL, MySQL 등
2. **인증 시스템**: JWT 토큰 기반
3. **API 문서화**: Swagger/OpenAPI
4. **모니터링**: Prometheus, Grafana
5. **CI/CD**: GitHub Actions, GitLab CI

## 📞 지원

문제가 발생하거나 질문이 있으시면:
1. GitHub Issues 생성
2. 로그 파일 확인
3. Railway 대시보드에서 상태 확인
