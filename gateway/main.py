from typing import Optional, List
from fastapi import APIRouter, FastAPI, Request, UploadFile, File, Query, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import os
import logging
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# 로컬 환경변수 로드
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("gateway_api")

# 회원가입 데이터를 저장할 파일 경로
SIGNUP_DATA_FILE = "data/signup_data.json"

# 회원가입 데이터를 파일에 저장하는 함수
def save_signup_data(data):
    try:
        # data 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(SIGNUP_DATA_FILE), exist_ok=True)
        
        # 기존 데이터 읽기
        existing_data = []
        if os.path.exists(SIGNUP_DATA_FILE):
            with open(SIGNUP_DATA_FILE, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        
        # 새 데이터 추가
        new_entry = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        existing_data.append(new_entry)
        
        # 파일에 저장
        with open(SIGNUP_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"회원가입 데이터가 {SIGNUP_DATA_FILE}에 저장되었습니다.")
        return True
    except Exception as e:
        logger.error(f"데이터 저장 실패: {str(e)}")
        return False

# 회원가입 데이터를 읽는 함수
def load_signup_data():
    try:
        if os.path.exists(SIGNUP_DATA_FILE):
            with open(SIGNUP_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"데이터 읽기 실패: {str(e)}")
        return []

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 서비스 시작")
yield
    logger.info("🛑 Gateway API 서비스 종료")

app = FastAPI(
title="Gateway API",
    description="Gateway API for ausikor.com",
version="0.1.0",
docs_url="/docs",
lifespan=lifespan
)

# CORS 미들웨어 설정
app.add_middleware(
CORSMiddleware,
allow_origins=[
"http://localhost:3000",  # 로컬 접근
"http://127.0.0.1:3000",  # 로컬 IP 접근
"http://frontend:3000",   # Docker 내부 네트워크
    ],
allow_credentials=True,  # HttpOnly 쿠키 사용을 위해 필수
allow_methods=["*"],
allow_headers=["*"],
)

# 메인 라우터 생성
gateway_router = APIRouter(prefix="/api/v1", tags=["Gateway API"])

# 헬스 체크 엔드포인트
@gateway_router.get("/health", summary="테스트 엔드포인트")
async def health_check():
    return {"status": "healthy!", "message": "Gateway API is running"}

# 로그인 페이지 (HTML)
@app.get("/", summary="로그인 페이지")
async def login_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>로그인</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center p-4">
        <div class="w-full max-w-sm">
            <div class="bg-white rounded-3xl shadow-2xl px-8 py-12">
                <!-- Login Title -->
                <div class="text-center mb-12">
                    <h1 class="text-5xl font-bold text-gray-900 tracking-tight">
                        Login
                    </h1>
                </div>

                <!-- Login Form -->
                <form id="loginForm" class="space-y-8">
                    <!-- Username Input -->
                    <div class="relative">
                        <input
                            type="text"
                            id="id"
                            name="id"
                            placeholder="Username"
                            class="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                            required
                        />
                    </div>

                    <!-- Password Input -->
                    <div class="relative">
                        <input
                            type="password"
                            id="password"
                            name="password"
                            placeholder="Password"
                            class="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                            required
                        />
                    </div>

                    <!-- Login Button -->
                    <button
                        type="submit"
                        class="w-full bg-blue-600 text-white py-4 rounded-2xl hover:bg-blue-700 transition-all duration-200 font-medium text-lg shadow-sm"
                    >
                        Login
                    </button>
                </form>

                <!-- Divider -->
                <div class="mt-8">
                    <div class="relative">
                        <div class="absolute inset-0 flex items-center">
                            <div class="w-full border-t border-gray-300" />
                        </div>
                        <div class="relative flex justify-center text-sm">
                            <span class="px-2 bg-white text-gray-500">또는</span>
                        </div>
                    </div>
                </div>

                <!-- Sign Up Button -->
                <div class="mt-6">
                    <button onclick="window.location.href='/signup'" class="w-full bg-green-600 text-white py-4 rounded-2xl hover:bg-green-700 transition-all duration-200 font-medium text-lg shadow-sm">
                        회원가입
                    </button>
                </div>
            </div>
        </div>

        <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                id: document.getElementById('id').value,
                password: document.getElementById('password').value
            };

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const result = await response.json();
                
                if (response.ok) {
                    alert('로그인 성공!\\n' + JSON.stringify(result, null, 2));
                    // 로그인 성공 후 대시보드로 이동
                    window.location.href = '/dashboard';
                } else {
                    alert('로그인 실패: ' + result.detail);
                }
            } catch (error) {
                alert('로그인 실패: ' + error.message);
            }
        });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/login", summary="로그인")
async def login(request: Request):
    try:
        body = await request.json()
        id = body.get("id")
        password = body.get("password")
        
        # 검증 없이 무조건 성공
        return {
            "status": "success",
            "message": "로그인 성공",
            "access_token": "dummy_token_12345",
            "user": {
                "id": id,
                "name": "사용자"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로그인 실패: {str(e)}")

# API v1 로그인 엔드포인트 (기존 경로 유지)
@gateway_router.post("/login", summary="로그인 API v1")
async def login_api_v1(request: Request):
    try:
        body = await request.json()
        id = body.get("id")
        password = body.get("password")
        
        # 간단한 검증 (실제로는 데이터베이스에서 확인해야 함)
        if id and password:
            # 성공 응답
            return {
                "status": "success",
                "message": "로그인 성공",
                "access_token": "dummy_token_12345",
                "user": {
                    "id": id,
                    "name": "사용자"
                }
            }
        else:
            raise HTTPException(status_code=400, detail="ID와 비밀번호를 입력해주세요")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로그인 실패: {str(e)}")

# 회원가입 엔드포인트
@gateway_router.post("/signup", summary="회원가입")
async def signup_api_v1(request: Request):
    try:
        body = await request.json()
        print("=" * 50)
        print("🎯 회원가입 요청 받음!")
        print("=" * 50)
        
        # 요청 데이터 로깅
        print(f"📦 받은 데이터: {json.dumps(body, indent=2, ensure_ascii=False)}")
        logger.info(f"회원가입 요청: {body}")
        
        # 간단한 검증
        if not body:
            raise HTTPException(status_code=400, detail="데이터가 없습니다.")
        
        # 데이터를 파일에 저장
        save_success = save_signup_data(body)
        
        # 성공 응답
        response_data = {
            "status": "success",
            "message": "회원가입됨!",
            "data": body,
            "saved_to_file": save_success
        }
        
        print(f"✅ 회원가입 완료: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        logger.info(f"회원가입 완료: {response_data}")
        print("=" * 50)
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"회원가입 오류: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=f"회원가입 실패: {str(e)}")

# 회원가입 데이터 조회 엔드포인트
@gateway_router.get("/signup/data", summary="회원가입 데이터 조회")
async def get_signup_data():
    try:
        data = load_signup_data()
        print("=" * 50)
        print(f"📊 회원가입 데이터 조회: {len(data)}개 항목")
        print("=" * 50)
        
        if data:
            for i, item in enumerate(data, 1):
                print(f"📝 항목 {i}:")
                print(f"   시간: {item.get('timestamp', 'N/A')}")
                print(f"   데이터: {json.dumps(item.get('data', {}), indent=4, ensure_ascii=False)}")
                print("-" * 30)
        else:
            print("📭 저장된 데이터가 없습니다.")
        
        print("=" * 50)
        logger.info(f"회원가입 데이터 조회: {len(data)}개 항목")
        
        return {
            "status": "success",
            "message": f"총 {len(data)}개의 회원가입 데이터",
            "data": data,
            "count": len(data)
        }
    except Exception as e:
        error_msg = f"데이터 조회 오류: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# 사용자 정보 엔드포인트
@gateway_router.get("/auth/me", summary="사용자 정보 조회")
async def get_user_info(request: Request):
    # 실제로는 JWT 토큰을 검증해야 함
    return {
        "status": "success",
        "user": {
            "id": "user123",
            "name": "테스트 사용자",
            "email": "test@example.com"
        }
    }

# 회원가입 페이지 (HTML)
@app.get("/signup", summary="회원가입 페이지")
async def signup_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>회원가입</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div class="w-full max-w-md">
            <div class="bg-white rounded-3xl shadow-2xl px-8 py-12">
                <!-- Signup Title -->
                <div class="text-center mb-12">
                    <h1 class="text-4xl font-bold text-gray-900 tracking-tight mb-2">
                        Flow Master 등록
                    </h1>
                    <p class="text-gray-600">
                        새로운 flow_master 데이터를 생성하세요
                    </p>
                </div>

                <!-- Signup Form -->
                <form id="signupForm" class="space-y-6">
                    <!-- Name Input - 필수 -->
                    <div class="relative">
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                            이름 <span class="text-red-500">*</span>
                        </label>
                        <input
                            type="text"
                            id="name"
                            name="name"
                            placeholder="이름을 입력하세요"
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
                            required
                        />
                    </div>

                    <!-- Type Input - 선택 -->
                    <div class="relative">
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                            타입
                        </label>
                        <select
                            id="type"
                            name="type"
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
                        >
                            <option value="">타입을 선택하세요</option>
                            <option value="process">Process</option>
                            <option value="workflow">Workflow</option>
                            <option value="automation">Automation</option>
                            <option value="manual">Manual</option>
                        </select>
                    </div>

                    <!-- Category Input - 선택 -->
                    <div class="relative">
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                            카테고리
                        </label>
                        <select
                            id="category"
                            name="category"
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
                        >
                            <option value="">카테고리를 선택하세요</option>
                            <option value="business">Business</option>
                            <option value="technical">Technical</option>
                            <option value="operational">Operational</option>
                            <option value="management">Management</option>
                        </select>
                    </div>

                    <!-- Unit ID Input - 선택 -->
                    <div class="relative">
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                            Unit ID
                        </label>
                        <input
                            type="text"
                            id="unit_id"
                            name="unit_id"
                            placeholder="Unit ID (자동 생성됨)"
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200 bg-gray-50"
                            readonly
                        />
                        <p class="text-xs text-gray-500 mt-1">Unit ID는 자동으로 생성됩니다.</p>
                    </div>

                    <!-- Error Message -->
                    <div id="errorMessage" class="bg-red-50 border border-red-200 rounded-lg p-3 hidden">
                        <p class="text-red-600 text-sm"></p>
                    </div>

                    <!-- Signup Button -->
                    <button
                        type="submit"
                        id="signupButton"
                        class="w-full bg-blue-600 text-white py-4 rounded-2xl hover:bg-blue-700 transition-all duration-200 font-medium text-lg shadow-sm"
                    >
                        Flow Master 생성 (axios 전송)
                    </button>
                </form>

                <!-- Divider -->
                <div class="mt-8">
                    <div class="relative">
                        <div class="absolute inset-0 flex items-center">
                            <div class="w-full border-t border-gray-300" />
                        </div>
                        <div class="relative flex justify-center text-sm">
                            <span class="px-2 bg-white text-gray-500">또는</span>
                        </div>
                    </div>
                </div>

                <!-- Login Link -->
                <div class="mt-6 text-center">
                    <p class="text-gray-600 text-sm">
                        이미 계정이 있으신가요? 
                        <button onclick="window.location.href='/'" class="text-blue-600 hover:text-blue-700 font-medium">
                            로그인
                        </button>
                    </p>
                </div>
            </div>
        </div>

        <script>
        // UUID 생성 함수
        function generateUUID() {
            return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                const r = Math.random() * 16 | 0;
                const v = c === 'x' ? r : (r & 0x3 | 0x8);
                return v.toString(16);
            });
        }

        // Unit ID 자동 생성
        document.getElementById('unit_id').value = generateUUID();

        document.getElementById('signupForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const signupButton = document.getElementById('signupButton');
            const errorMessage = document.getElementById('errorMessage');
            
            // 필수 필드 확인
            const name = document.getElementById('name').value.trim();
            if (!name) {
                errorMessage.querySelector('p').textContent = '이름은 필수 입력 항목입니다.';
                errorMessage.classList.remove('hidden');
                return;
            }

            // 버튼 비활성화
            signupButton.disabled = true;
            signupButton.textContent = '생성 중...';
            errorMessage.classList.add('hidden');

            // flow_master 테이블 구조에 맞는 데이터 생성
            const signupData = {
                id: generateUUID(),
                name: name,
                type: document.getElementById('type').value || null,
                category: document.getElementById('category').value || null,
                unit_id: document.getElementById('unit_id').value || generateUUID()
            };

            try {
                console.log('🚀 회원가입 데이터 전송 시작...');
                const response = await fetch('/api/v1/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(signupData)
                });

                const result = await response.json();
                console.log('✅ 회원가입 성공:', result);

                if (response.ok) {
                    // 성공 메시지 - JSON 형태로 alert 표시
                    const inputData = {
                        name: {
                            name: name,
                            type: document.getElementById('type').value || null,
                            category: document.getElementById('category').value || null,
                            unit_id: document.getElementById('unit_id').value || generateUUID()
                        },
                        value: {
                            name: name,
                            type: document.getElementById('type').value || null,
                            category: document.getElementById('category').value || null,
                            unit_id: document.getElementById('unit_id').value || generateUUID()
                        }
                    };

                    alert('flow_master 데이터가 생성되었습니다!\\n\\n' + JSON.stringify(inputData, null, 2) + '\\n\\n서버 응답: ' + result.message);
                    
                    // 로그인 페이지로 이동
                    window.location.href = '/?message=flow_master 데이터가 생성되었습니다.';
                } else {
                    throw new Error(result.detail || '회원가입 실패');
                }
            } catch (error) {
                console.error('❌ 회원가입 실패:', error);
                errorMessage.querySelector('p').textContent = '회원가입 실패: ' + error.message;
                errorMessage.classList.remove('hidden');
            } finally {
                // 버튼 활성화
                signupButton.disabled = false;
                signupButton.textContent = 'Flow Master 생성 (axios 전송)';
            }
        });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# 대시보드 페이지 (HTML)
@app.get("/dashboard", summary="대시보드 페이지")
async def dashboard_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>대시보드</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="min-h-screen bg-gray-900 flex flex-col items-center justify-center p-4">
        <!-- Main Content -->
        <div class="w-full max-w-2xl">
            <!-- Title -->
            <div class="text-center mb-8">
                <h1 class="text-2xl font-medium text-white mb-4">
                    준비되면 얘기해 주세요.
                </h1>

                <!-- 로그인 데이터 표시 -->
                <div id="loginDataDisplay" class="bg-gray-800 rounded-lg p-4 mb-6 hidden">
                    <h2 class="text-lg font-medium text-white mb-3">저장된 로그인 데이터</h2>
                    <div class="bg-gray-700 rounded p-3 mb-4">
                        <pre id="loginDataJson" class="text-green-400 text-sm overflow-x-auto"></pre>
                    </div>

                    <!-- 전송 버튼 -->
                    <button
                        id="sendDataButton"
                        class="w-full bg-green-600 text-white py-4 px-6 rounded-lg font-bold text-lg hover:bg-green-700 focus:ring-4 focus:ring-green-500 focus:ring-offset-2 transition-all duration-200 shadow-lg"
                    >
                        🚀 JSON 데이터 전송 (axios)
                    </button>

                    <!-- 메시지 표시 -->
                    <div id="messageDisplay" class="mt-3 p-3 rounded-lg text-sm hidden"></div>
                </div>
            </div>

            <!-- Input Container -->
            <div class="relative">
                <form id="chatForm">
                    <div class="relative bg-gray-800 rounded-2xl shadow-lg border border-gray-700">
                        <div class="flex items-center px-4 py-3">
                            <!-- Plus Icon -->
                            <div class="flex items-center mr-3">
                                <button
                                    type="button"
                                    class="flex items-center text-gray-400 hover:text-gray-300 transition-colors duration-200"
                                >
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                                    </svg>
                                </button>
                            </div>

                            <!-- Input Field -->
                            <div class="flex-1">
                                <input
                                    type="text"
                                    id="chatInput"
                                    placeholder="무엇이든 물어보세요"
                                    class="w-full bg-transparent border-none outline-none text-white placeholder-gray-400 text-lg"
                                    required
                                />
                            </div>

                            <!-- Right Side Icons -->
                            <div class="flex items-center space-x-3 ml-3">
                                <!-- Microphone Icon -->
                                <button
                                    type="button"
                                    class="p-2 text-gray-400 hover:text-gray-300 transition-colors duration-200 rounded-full hover:bg-gray-700"
                                >
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                                    </svg>
                                </button>

                                <!-- Send Button -->
                                <button
                                    type="submit"
                                    class="p-2 text-gray-400 hover:text-gray-300 transition-colors duration-200 rounded-full hover:bg-gray-700"
                                >
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
        </div>

        <script>
        // 페이지 로드 시 localStorage에서 로그인 데이터 가져오기
        window.addEventListener('load', function() {
            const loginData = localStorage.getItem('loginData');
            if (loginData) {
                try {
                    const parsedData = JSON.parse(loginData);
                    document.getElementById('loginDataJson').textContent = JSON.stringify(parsedData, null, 2);
                    document.getElementById('loginDataDisplay').classList.remove('hidden');
                    console.log('저장된 로그인 데이터:', parsedData);
                } catch (error) {
                    console.error('로그인 데이터 파싱 오류:', error);
                }
            }
        });

        // JSON 데이터를 전송하는 함수
        document.getElementById('sendDataButton').addEventListener('click', async function() {
            const loginData = localStorage.getItem('loginData');
            const messageDisplay = document.getElementById('messageDisplay');
            const sendDataButton = document.getElementById('sendDataButton');

            if (!loginData) {
                messageDisplay.textContent = '전송할 로그인 데이터가 없습니다.';
                messageDisplay.className = 'mt-3 p-3 rounded-lg text-sm bg-red-900 text-red-300';
                messageDisplay.classList.remove('hidden');
                return;
            }

            try {
                const parsedData = JSON.parse(loginData);
                console.log('📤 전송할 데이터:', parsedData);
                
                sendDataButton.disabled = true;
                sendDataButton.textContent = '🔄 전송 중...';
                messageDisplay.classList.add('hidden');

                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(parsedData)
                });

                const result = await response.json();
                console.log('✅ 전송 성공!', result);

                messageDisplay.textContent = '✅ JSON 데이터가 성공적으로 전송되었습니다!';
                messageDisplay.className = 'mt-3 p-3 rounded-lg text-sm bg-green-900 text-green-300';
                messageDisplay.classList.remove('hidden');

            } catch (error) {
                console.error('❌ 전송 실패:', error);
                messageDisplay.textContent = '❌ 전송 실패: ' + error.message;
                messageDisplay.className = 'mt-3 p-3 rounded-lg text-sm bg-red-900 text-red-300';
                messageDisplay.classList.remove('hidden');
            } finally {
                sendDataButton.disabled = false;
                sendDataButton.textContent = '🚀 JSON 데이터 전송 (axios)';
            }
        });

        // 채팅 폼 제출
        document.getElementById('chatForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const inputValue = document.getElementById('chatInput').value;
            if (inputValue.trim()) {
                console.log('입력된 메시지:', inputValue);
                document.getElementById('chatInput').value = '';
            }
        });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# 라우터를 앱에 포함
app.include_router(gateway_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)