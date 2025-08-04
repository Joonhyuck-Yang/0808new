# 로컬 개발 환경 실행 스크립트
# 프론트엔드(3000번 포트)와 백엔드(8080번 포트)를 동시에 실행

Write-Host "🚀 로컬 개발 환경을 시작합니다..." -ForegroundColor Green

# 백엔드 실행 (백그라운드)
Write-Host "📡 백엔드 서버를 시작합니다 (포트 8080)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd gateway; python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload"

# 잠시 대기
Start-Sleep -Seconds 3

# 프론트엔드 실행 (백그라운드)
Write-Host "🌐 프론트엔드 서버를 시작합니다 (포트 3000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; pnpm dev"

Write-Host "✅ 모든 서비스가 시작되었습니다!" -ForegroundColor Green
Write-Host "📱 프론트엔드: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 백엔드 API: http://localhost:8080" -ForegroundColor Cyan
Write-Host "📚 Swagger 문서: http://localhost:8080/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "서비스를 중지하려면 각 터미널 창을 닫으세요." -ForegroundColor Gray 