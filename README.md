# 🚀 Flow Master 등록 시스템

> 프론트엔드에서 입력한 값이 Railway에서 JSON 형태로 출력되는 FastAPI 기반 시스템

## ✨ 주요 기능

- 🎯 **Flow Master 등록**: 이름, 타입, 카테고리, 설명을 입력하여 Flow Master 생성
- 📊 **JSON 데이터 저장**: 입력된 데이터를 Railway 서버에 JSON 형태로 저장
- 🔄 **데이터 히스토리**: 저장된 데이터 조회 및 표시
- 🌐 **웹 인터페이스**: 모던하고 반응형인 웹 UI
- 🐳 **Docker 지원**: 로컬 및 클라우드 배포 지원
- 🚂 **Railway 배포**: 간편한 클라우드 배포

## 🏗️ 시스템 구조

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   프론트엔드    │───▶│   Gateway API   │───▶│   데이터 저장   │
│   (HTML/JS)    │    │   (FastAPI)     │    │   (JSON)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 빠른 시작

### 1. 로컬 실행 (Docker)

```bash
# 프로젝트 클론
git clone <repository-url>
cd educated

# Docker Compose로 실행
docker-compose up --build

# 브라우저에서 접속
open http://localhost:8080/frontend
```

### 2. 로컬 실행 (Python)

```bash
cd gateway

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python main.py

# 브라우저에서 접속
open http://localhost:8080/frontend
```

### 3. Railway 배포

```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인 및 배포
railway login
railway init
railway up
```

## 📱 사용 방법

### 1. 프론트엔드 접속
- **로컬**: `http://localhost:8080/frontend`
- **Railway**: `https://your-domain.railway.app/frontend`

### 2. Flow Master 등록
1. **이름 입력** (필수)
2. **타입 선택** (Process, Workflow, Automation, Manual)
3. **카테고리 선택** (Business, Technical, Operational, Management)
4. **설명 입력** (선택)
5. **"Flow Master 생성" 버튼 클릭**

### 3. 데이터 확인
- 생성된 데이터는 자동으로 JSON 형태로 표시
- "히스토리 새로고침" 버튼으로 저장된 데이터 조회

## 🔧 API 엔드포인트

| 메서드 | 엔드포인트 | 설명 |
|--------|------------|------|
| `GET` | `/api/v1/health` | 헬스체크 |
| `POST` | `/api/v1/signup` | Flow Master 생성 |
| `GET` | `/api/v1/signup/data` | 저장된 데이터 조회 |
| `GET` | `/frontend` | 프론트엔드 페이지 |

### API 테스트

```bash
# 헬스체크
curl http://localhost:8080/api/v1/health

# Flow Master 생성
curl -X POST http://localhost:8080/api/v1/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "테스트 Flow",
    "type": "process",
    "category": "business",
    "description": "테스트 설명"
  }'

# 데이터 조회
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

## 🐳 Docker

### Docker Compose
```yaml
version: '3.8'
services:
  gateway:
    build: ./gateway
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - AUTH_SERVICE_URL=http://auth-service:8000
```

### 개별 실행
```bash
# Gateway 서비스 빌드
cd gateway
docker build -f Dockerfile.railway -t flow-master-gateway .

# 실행
docker run -p 8080:8080 -e PORT=8080 flow-master-gateway
```

## 🚂 Railway 배포

### 1. 환경변수 설정
Railway 대시보드에서 다음 환경변수를 설정:

```env
PORT=8080
AUTH_SERVICE_URL=http://localhost:8000
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://your-domain.com,http://localhost:3000
```

### 2. 배포 명령어
```bash
railway up
railway domain
```

## 🌐 Vercel 배포 (선택사항)

```bash
# Vercel CLI 설치
npm install -g vercel

# 배포
vercel --prod
```

## 📁 프로젝트 구조

```
educated/
├── gateway/                 # Gateway API 서비스
│   ├── main.py            # FastAPI 메인 앱
│   ├── frontend.html      # 프론트엔드 페이지
│   ├── Dockerfile.railway # Railway용 Dockerfile
│   ├── requirements.txt   # Python 의존성
│   └── railway.env        # Railway 환경변수
├── service/                # 마이크로서비스들
│   ├── auth-service/      # 인증 서비스
│   ├── cbam-service/      # CBAM 서비스
│   └── ...
├── docker-compose.yml      # Docker Compose 설정
├── test_api.py            # API 테스트 스크립트
├── RAILWAY_DEPLOYMENT.md  # Railway 배포 가이드
└── README.md              # 이 파일
```

## 🧪 테스트

### 자동 테스트
```bash
# API 테스트 실행
python test_api.py
```

### 수동 테스트
1. 브라우저에서 `http://localhost:8080/frontend` 접속
2. Flow Master 등록 폼 작성
3. 데이터 전송 및 결과 확인
4. 히스토리에서 저장된 데이터 확인

## 🐛 문제 해결

### 포트 충돌
```bash
# 포트 사용 확인
netstat -tulpn | grep :8080

# 다른 포트 사용
PORT=8081 docker-compose up
```

### 권한 문제
```bash
# Docker 권한 설정
sudo usermod -aG docker $USER
```

### 로그 확인
```bash
# Docker 로그
docker-compose logs gateway

# 개별 컨테이너 로그
docker logs <container_id>
```

## 🔮 다음 단계

- [ ] **데이터베이스 연동**: PostgreSQL, MySQL 등
- [ ] **인증 시스템**: JWT 토큰 기반
- [ ] **API 문서화**: Swagger/OpenAPI
- [ ] **모니터링**: Prometheus, Grafana
- [ ] **CI/CD**: GitHub Actions, GitLab CI
- [ ] **로드 밸런싱**: Nginx, Traefik
- [ ] **캐싱**: Redis, Memcached

## 📞 지원

문제가 발생하거나 질문이 있으시면:

1. **GitHub Issues** 생성
2. **로그 파일** 확인
3. **Railway 대시보드**에서 상태 확인
4. **API 문서** 확인: `http://localhost:8080/docs`

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

**Made with ❤️ by [Your Name]** 