'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

export default function DashboardPage() {
  const [inputValue, setInputValue] = useState('');
  const [loginData, setLoginData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  // 페이지 로드 시 localStorage에서 로그인 데이터 가져오기
  useEffect(() => {
    const storedData = localStorage.getItem('loginData');
    if (storedData) {
      try {
        const parsedData = JSON.parse(storedData);
        setLoginData(parsedData);
        console.log('저장된 로그인 데이터:', parsedData);
      } catch (error) {
        console.error('로그인 데이터 파싱 오류:', error);
      }
    }
  }, []);

  // JSON 데이터를 axios로 전송하는 함수
  const sendLoginData = async () => {
    console.log('=== JSON 데이터 전송 시작 ===');
    
    if (!loginData) {
      console.log('❌ 전송할 로그인 데이터가 없습니다.');
      setMessage('전송할 로그인 데이터가 없습니다.');
      return;
    }

    console.log('📤 전송할 데이터:', loginData);
    setIsLoading(true);
    setMessage('');

    try {
      console.log('🚀 axios POST 요청 시작...');
      console.log('📍 전송 URL: http://localhost:8080/login');
      console.log('📦 전송 데이터:', JSON.stringify(loginData, null, 2));
      
      // axios를 사용해서 8080/login으로 POST 요청 전송
      const response = await axios.post('http://localhost:8080/login', loginData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      console.log('✅ 전송 성공!');
      console.log('📥 서버 응답:', response.data);
      setMessage('✅ JSON 데이터가 성공적으로 전송되었습니다!');
      
      // 전송 성공 후 응답 데이터도 표시
      if (response.data) {
        console.log('🎯 서버 응답 상세:', response.data);
      }
      
    } catch (error: any) {
      console.error('❌ 전송 실패:', error);
      console.error('🔍 에러 상세:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        statusText: error.response?.statusText
      });
      
      if (error.response) {
        // 서버에서 응답이 왔지만 에러인 경우
        const errorMsg = '❌ 전송 실패: ' + (error.response.data?.detail || error.response.statusText);
        console.error(errorMsg);
        setMessage(errorMsg);
      } else if (error.request) {
        // 요청은 보냈지만 응답이 없는 경우
        const errorMsg = '❌ 서버에 연결할 수 없습니다. 8080번 포트가 실행 중인지 확인해주세요.';
        console.error(errorMsg);
        setMessage(errorMsg);
      } else {
        // 요청 자체가 실패한 경우
        const errorMsg = '❌ 전송 실패: ' + error.message;
        console.error(errorMsg);
        setMessage(errorMsg);
      }
    } finally {
      console.log('🏁 전송 프로세스 완료');
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      console.log('입력된 메시지:', inputValue);
      setInputValue('');
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center p-4">
      {/* Main Content */}
      <div className="w-full max-w-2xl">
        {/* Title */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-medium text-white mb-4">
            준비되면 얘기해 주세요.
          </h1>
          
          {/* 로그인 데이터 표시 */}
          {loginData && (
            <div className="bg-gray-800 rounded-lg p-4 mb-6">
              <h2 className="text-lg font-medium text-white mb-3">저장된 로그인 데이터</h2>
              <div className="bg-gray-700 rounded p-3 mb-4">
                <pre className="text-green-400 text-sm overflow-x-auto">
                  {JSON.stringify(loginData, null, 2)}
                </pre>
              </div>
              
              {/* 전송 버튼 - 더 눈에 띄게 스타일링 */}
              <button
                onClick={sendLoginData}
                disabled={isLoading}
                className="w-full bg-green-600 text-white py-4 px-6 rounded-lg font-bold text-lg hover:bg-green-700 focus:ring-4 focus:ring-green-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
              >
                {isLoading ? '🔄 전송 중...' : '🚀 JSON 데이터 전송 (axios)'}
              </button>
              
              {/* 메시지 표시 */}
              {message && (
                <div className={`mt-3 p-3 rounded-lg text-sm ${
                  message.includes('성공') ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
                }`}>
                  {message}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Input Container */}
        <div className="relative">
          <form onSubmit={handleSubmit}>
            <div className="relative bg-gray-800 rounded-2xl shadow-lg border border-gray-700">
              <div className="flex items-center px-4 py-3">
                {/* Plus Icon */}
                <div className="flex items-center mr-3">
                  <button
                    type="button"
                    className="flex items-center text-gray-400 hover:text-gray-300 transition-colors duration-200"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                  </button>
                </div>

                {/* Input Field */}
                <div className="flex-1">
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="무엇이든 물어보세요"
                    className="w-full bg-transparent border-none outline-none text-white placeholder-gray-400 text-lg"
                    required
                  />
                </div>

                {/* Right Side Icons */}
                <div className="flex items-center space-x-3 ml-3">
                  {/* Microphone Icon */}
                  <button
                    type="button"
                    className="p-2 text-gray-400 hover:text-gray-300 transition-colors duration-200 rounded-full hover:bg-gray-700"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                  </button>

                  {/* Send Button (Waveform Icon) */}
                  <button
                    type="submit"
                    className="p-2 text-gray-400 hover:text-gray-300 transition-colors duration-200 rounded-full hover:bg-gray-700"
                    disabled={!inputValue.trim()}
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
