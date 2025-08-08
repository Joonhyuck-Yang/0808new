'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface ChatMessage {
  message: string;
}

interface User {
  id: number;
  email: string;
  name: string;
}

export default function Home() {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [showJsonModal, setShowJsonModal] = useState(false);
  const [lastSubmittedJson, setLastSubmittedJson] = useState<string>('');
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // 로그인 상태 확인
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('/api/auth/me');
      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
      } else {
        // 로그인되지 않은 경우 로그인 페이지로 이동
        router.push('/login');
        return;
      }
    } catch (error) {
      console.error('인증 확인 오류:', error);
      router.push('/login');
      return;
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      const newMessage: ChatMessage = {
        message: inputValue
      };
      
      setMessages(prev => [...prev, newMessage]);
      const jsonString = JSON.stringify(newMessage, null, 2);
      setLastSubmittedJson(jsonString);
      setShowJsonModal(true);
      console.log('JSON 형태의 메시지:', jsonString);
      
      // 백엔드 API로 메시지 전송
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
        const response = await fetch(`${apiUrl}/api/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(newMessage),
        });
        
        if (response.ok) {
          const result = await response.json();
          console.log('백엔드 응답:', result);
        } else {
          console.error('API 요청 실패:', response.status);
        }
      } catch (error) {
        console.error('API 통신 오류:', error);
      }
      
      setInputValue('');
    }
  };

  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
      setUser(null);
      router.push('/login');
    } catch (error) {
      console.error('로그아웃 오류:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header with User Info */}
      <header className="bg-white border-b border-gray-200 px-4 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-xl font-semibold text-gray-900">AI Chat Interface</h1>
          <div className="flex items-center space-x-4">
            {user && (
              <div className="flex items-center space-x-3">
                <span className="text-gray-700">
                  안녕하세요, {user.name}님!
                </span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-gray-700 hover:text-gray-900 font-medium"
                >
                  로그아웃
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-4">
        {/* Main Question */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-medium text-gray-800 mb-4">
            오늘은 무슨 생각을 하고 계신가요?
          </h1>
        </div>

        {/* Input Container */}
        <div className="w-full max-w-2xl">
          <form onSubmit={handleSubmit} className="relative">
            {/* Main Input Field */}
            <div className="relative bg-white border border-gray-200 rounded-2xl shadow-sm hover:shadow-md transition-shadow duration-200">
              <div className="flex items-center px-4 py-3">
                {/* Tools Button */}
                <div className="flex items-center mr-3">
                  <button 
                    type="button"
                    className="flex items-center text-gray-500 hover:text-gray-700 transition-colors duration-200"
                  >
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    <span className="text-sm font-medium">도구</span>
                  </button>
                </div>

                {/* Input Field */}
                <div className="flex-1">
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="무엇이든 물어보세요"
                    className="w-full bg-transparent border-none outline-none text-gray-800 placeholder-gray-400 text-lg"
                    required
                  />
                </div>

                {/* Right Side Icons */}
                <div className="flex items-center space-x-3 ml-3">
                  {/* Microphone Icon */}
                  <button 
                    type="button"
                    className="p-2 text-gray-500 hover:text-gray-700 transition-colors duration-200 rounded-full hover:bg-gray-100"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                  </button>

                  {/* Send Button */}
                  <button
                    type="submit"
                    className="p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors duration-200"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </form>
        </div>

        {/* Messages Display */}
        {messages.length > 0 && (
          <div className="w-full max-w-2xl mt-8 space-y-4">
            {messages.map((message, index) => (
              <div key={index} className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-800">{message.message}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* JSON Modal */}
      {showJsonModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-96 overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">JSON 형태의 메시지</h3>
              <button
                onClick={() => setShowJsonModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
              {lastSubmittedJson}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
