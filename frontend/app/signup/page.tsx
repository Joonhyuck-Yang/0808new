'use client';

import { useState } from 'react';
import axios from 'axios';

export default function SignupPage() {
  const [formData, setFormData] = useState({
    name: '',
    pass: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setResult(null);

    try {
      console.log('🚀 회원가입 데이터 전송 시작...');
      console.log('📦 전송할 데이터:', formData);
      
      const response = await axios.post('https://gateway-production-be21.up.railway.app/api/v1/signup', formData, {
        headers: {
          'Content-Type': 'application/json',
        }
      });

      const result = response.data;
      console.log('✅ 회원가입 성공:', result);
      
      if (response.status === 200 || response.status === 201) {
        setResult(result);
        // 폼 초기화
        setFormData({ name: '', pass: '' });
        alert('회원가입 성공!\\n\\n아이디: ' + formData.name + '\\n비밀번호: ' + formData.pass + '\\n\\nRailway 로그를 확인하세요!');
      } else {
        throw new Error(result.detail || result.message || '회원가입 실패');
      }
    } catch (error: any) {
      console.error('❌ 회원가입 실패:', error);
      
      // axios 에러 처리
      let errorMessage = '회원가입 실패';
      if (error.response) {
        // 서버 응답이 있는 경우
        errorMessage = error.response.data?.detail || error.response.data?.message || `서버 오류: ${error.response.status}`;
      } else if (error.request) {
        // 요청은 보냈지만 응답이 없는 경우
        errorMessage = '서버에 연결할 수 없습니다';
      } else {
        // 기타 오류
        errorMessage = error.message || '알 수 없는 오류가 발생했습니다';
      }
      
      alert('회원가입 실패: ' + errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-3xl shadow-2xl px-8 py-12">
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-gray-900 tracking-tight">
              Sign Up
            </h1>
            <p className="text-gray-600 mt-4">
              아이디와 비밀번호를 입력하세요
            </p>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-8">
            <div className="relative">
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="아이디 (Username)"
                className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                required
              />
            </div>
            
            <div className="relative">
              <input
                type="password"
                id="pass"
                name="pass"
                value={formData.pass}
                onChange={handleInputChange}
                placeholder="비밀번호 (Password)"
                className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                required
              />
            </div>
            
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-4 bg-blue-600 text-white font-semibold rounded-2xl hover:bg-blue-700 transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? '🔄 처리 중...' : '🚀 회원가입'}
            </button>
          </form>
          
          <div className="mt-8 text-center">
            <p className="text-gray-600 text-sm">
              회원가입 버튼을 누르면 아이디와 비밀번호가 Railway 로그에 출력됩니다
            </p>
          </div>
        </div>

        {/* 결과 표시 */}
        {result && (
          <div className="mt-6 bg-gray-50 rounded-lg p-4">
            <h3 className="text-lg font-medium text-gray-800 mb-2">전송된 데이터</h3>
            <pre className="text-sm text-gray-600 bg-white p-3 rounded border overflow-x-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
