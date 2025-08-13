# Railway 배포 환경변수 설정 가이드

## 필수 환경변수

### 1. PORT (자동 설정됨)
- Railway가 자동으로 설정
- 수동 설정 불필요

### 2. RAILWAY_ENVIRONMENT
- 값: `true`
- Railway 환경 감지용

### 3. DATABASE_URL (PostgreSQL 연결용)
- Railway PostgreSQL 서비스에서 제공하는 연결 문자열
- 형식: `postgresql://username:password@host:port/database`
- **이 값이 없으면 DB 저장 기능이 작동하지 않음**

### 4. 선택적 환경변수
```
GATEWAY_URL=https://gateway-production-be21.up.railway.app
HTTP_TIMEOUT=30
HTTP_MAX_KEEPALIVE=20
HTTP_MAX_CONNECTIONS=100
```

## Railway 대시보드에서 설정 방법

1. **서비스 선택** → **Variables** 탭
2. **New Variable** 클릭
3. **Key**: `RAILWAY_ENVIRONMENT`, **Value**: `true`
4. **Add** 클릭
5. **New Variable** 클릭
6. **Key**: `DATABASE_URL`, **Value**: PostgreSQL 연결 문자열
7. **Add** 클릭

## PostgreSQL 서비스 연결 방법

1. **Railway 대시보드**에서 **New Service** 클릭
2. **Database** → **PostgreSQL** 선택
3. **Deploy** 클릭
4. **Variables** 탭에서 `DATABASE_URL` 복사
5. **Auth Service**의 환경변수에 `DATABASE_URL` 설정

## 배포 후 확인사항

1. **헬스체크**: `/health` 엔드포인트 응답 확인
2. **서비스 상태**: `/status` 엔드포인트 응답 확인
3. **로그 확인**: Railway 로그에서 "🚂 AUTH SERVICE" 메시지 확인
4. **DB 연결**: "🚂 Auth Service - Railway DB 연결 성공" 메시지 확인

## 문제 해결

### 헬스체크 실패 시
- `/health` 엔드포인트가 제대로 응답하는지 확인
- 포트 설정이 올바른지 확인

### 서비스 시작 실패 시
- Railway 로그에서 구체적인 오류 메시지 확인
- 환경변수 설정 확인

### DB 연결 실패 시
- `DATABASE_URL` 환경변수가 올바르게 설정되었는지 확인
- PostgreSQL 서비스가 실행 중인지 확인
- 연결 문자열 형식이 올바른지 확인
