# MSA API Gateway Project

이 프로젝트는 마이크로서비스 아키텍처(MSA) 기반의 API Gateway와 관련 서비스들을 포함합니다.

## 🏗️ 프로젝트 구조

```
├── gateway/           # API Gateway 서비스
│   ├── app/          # FastAPI 애플리케이션
│   ├── Dockerfile    # Docker 설정
│   └── requirements.txt
├── service/          # 마이크로서비스들
├── frontend/         # Next.js 프론트엔드
└── document/         # 프로젝트 문서
```

## 🚀 빠른 시작

### API Gateway 실행

```bash
cd gateway
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

## 📚 API 문서

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🐳 Docker 배포

```bash
cd gateway
docker build -t msa-gateway .
docker run -p 8000:8000 msa-gateway
```

## ☁️ Railway 배포

자세한 배포 가이드는 [gateway/RAILWAY_DEPLOY.md](gateway/RAILWAY_DEPLOY.md)를 참조하세요.

## 🔧 기술 스택

- **Backend**: FastAPI, Python
- **Frontend**: Next.js, TypeScript
- **Deployment**: Railway, Docker
- **Monitoring**: Prometheus, Grafana

## 📝 라이선스

MIT License 