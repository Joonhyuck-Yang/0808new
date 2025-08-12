#!/usr/bin/env python3
"""
Flow Master API 테스트 스크립트
로컬 또는 Railway에서 실행 중인 API를 테스트합니다.
"""

import requests
import json
import time
from datetime import datetime

# API 기본 URL (로컬 테스트용)
BASE_URL = "http://localhost:8080"

def test_health_check():
    """헬스체크 테스트"""
    print("🏥 헬스체크 테스트...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        if response.status_code == 200:
            print("✅ 헬스체크 성공:", response.json())
            return True
        else:
            print("❌ 헬스체크 실패:", response.status_code)
            return False
    except Exception as e:
        print(f"❌ 헬스체크 오류: {e}")
        return False

def test_flow_master_creation():
    """Flow Master 생성 테스트"""
    print("\n🚀 Flow Master 생성 테스트...")
    
    test_data = {
        "name": f"테스트 Flow Master {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "type": "process",
        "category": "business",
        "description": "API 테스트를 위한 Flow Master",
        "unit_id": f"unit_{int(time.time())}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/signup",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Flow Master 생성 성공!")
            print("📊 응답 데이터:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"❌ Flow Master 생성 실패: {response.status_code}")
            print("응답:", response.text)
            return False
    except Exception as e:
        print(f"❌ Flow Master 생성 오류: {e}")
        return False

def test_data_retrieval():
    """저장된 데이터 조회 테스트"""
    print("\n📋 저장된 데이터 조회 테스트...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/signup/data")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 데이터 조회 성공!")
            print(f"📊 총 {result.get('count', 0)}개의 데이터")
            
            if result.get('data'):
                print("\n📝 저장된 데이터:")
                for i, item in enumerate(result['data'], 1):
                    print(f"\n--- 항목 {i} ---")
                    print(f"시간: {item.get('timestamp', 'N/A')}")
                    data = item.get('data', {})
                    print(f"이름: {data.get('name', 'N/A')}")
                    print(f"타입: {data.get('type', 'N/A')}")
                    print(f"카테고리: {data.get('category', 'N/A')}")
                    print(f"설명: {data.get('description', 'N/A')}")
            else:
                print("📭 저장된 데이터가 없습니다.")
            
            return True
        else:
            print(f"❌ 데이터 조회 실패: {response.status_code}")
            print("응답:", response.text)
            return False
    except Exception as e:
        print(f"❌ 데이터 조회 오류: {e}")
        return False

def test_frontend_page():
    """프론트엔드 페이지 접근 테스트"""
    print("\n🌐 프론트엔드 페이지 테스트...")
    
    try:
        response = requests.get(f"{BASE_URL}/frontend")
        
        if response.status_code == 200:
            print("✅ 프론트엔드 페이지 접근 성공!")
            print(f"📄 HTML 길이: {len(response.text)} 문자")
            return True
        else:
            print(f"❌ 프론트엔드 페이지 접근 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 프론트엔드 페이지 테스트 오류: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🧪 Flow Master API 테스트 시작")
    print("=" * 50)
    
    # 서버가 실행 중인지 확인
    print("🔍 API 서버 연결 확인 중...")
    try:
        requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        print("✅ API 서버에 연결되었습니다.")
    except:
        print("❌ API 서버에 연결할 수 없습니다.")
        print("서버가 실행 중인지 확인하세요:")
        print("  - 로컬: docker-compose up")
        print("  - 또는: cd gateway && python main.py")
        return
    
    # 테스트 실행
    tests = [
        test_health_check,
        test_flow_master_creation,
        test_data_retrieval,
        test_frontend_page
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(1)  # 테스트 간 간격
    
    # 결과 요약
    print("\n" + "=" * 50)
    print(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트가 통과했습니다!")
    else:
        print("⚠️  일부 테스트가 실패했습니다.")
    
    print("\n🌐 프론트엔드 접속:")
    print(f"   로컬: {BASE_URL}/frontend")
    print(f"   API 문서: {BASE_URL}/docs")

if __name__ == "__main__":
    main()
