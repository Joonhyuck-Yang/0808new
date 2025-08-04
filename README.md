# MSA 프로젝트

마이크로서비스 아키텍처 기반의 웹 애플리케이션입니다.

## 🚀 로컬 개발 환경 실행

### 방법 1: 자동 실행 스크립트 사용 (권장)

```powershell
# 프로젝트 루트에서 실행
.\start-local.ps1
```

### 방법 2: 수동 실행

#### 1. 백엔드 실행
```bash
cd gateway
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

#### 2. 프론트엔드 실행 (새 터미널에서)
```bash
cd frontend
pnpm install
pnpm dev
```

## 📱 접속 주소

- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8080
- **Swagger 문서**: http://localhost:8080/docs

## 🔧 환경 설정

### 프론트엔드 환경 변수 설정

`frontend/.env.local` 파일을 생성하고 다음 내용을 추가하세요:

```env
NEXT_PUBLIC_API_URL=http://localhost:8080
NEXT_PUBLIC_ENVIRONMENT=development
```

## 🛠️ 기술 스택

### 백엔드
- FastAPI
- Python 3.8+
- Uvicorn

### 프론트엔드
- Next.js 15
- React 19
- TypeScript
- Material-UI
- Tailwind CSS
- pnpm

## 📁 프로젝트 구조

```
├── frontend/          # Next.js 프론트엔드
├── gateway/           # FastAPI 백엔드 (API Gateway)
├── service/           # 마이크로서비스들
├── docker-compose.yml # 백엔드 도커 설정
└── start-local.ps1   # 로컬 실행 스크립트
```

## 🐳 도커 실행 (백엔드만)

```bash
docker-compose up backend
```

## 📝 개발 노트

- 프론트엔드는 로컬에서 직접 실행 (pnpm dev)
- 백엔드는 도커 또는 로컬에서 실행 가능
- API 통신은 환경 변수 `NEXT_PUBLIC_API_URL`을 통해 설정 