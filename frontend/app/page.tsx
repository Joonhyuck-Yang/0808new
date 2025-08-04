'use client';

import { useState } from 'react';

interface ChatMessage {
  message: string;
}

export default function Home() {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [showJsonModal, setShowJsonModal] = useState(false);
  const [lastSubmittedJson, setLastSubmittedJson] = useState<string>('');

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

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center px-4">
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

                {/* Submit Button (Waveform Icon) */}
                <button 
                  type="submit"
                  className="p-2 text-gray-500 hover:text-gray-700 transition-colors duration-200 rounded-full hover:bg-gray-100"
                  disabled={!inputValue.trim()}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          {/* Focus State Enhancement */}
          <div className="absolute inset-0 rounded-2xl pointer-events-none border-2 border-transparent focus-within:border-blue-500 transition-colors duration-200"></div>
        </form>
      </div>

      {/* JSON Modal */}
      {showJsonModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-medium text-gray-800 mb-4">저장된 JSON 형태:</h3>
            <div className="bg-gray-50 rounded p-3 mb-4">
              <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                {lastSubmittedJson}
              </pre>
            </div>
            <div className="text-sm text-gray-600 mb-4">
              <p><strong>입력된 메시지:</strong> {inputValue || messages[messages.length - 1]?.message}</p>
            </div>
            <button
              onClick={() => setShowJsonModal(false)}
              className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition-colors"
            >
              확인
            </button>
          </div>
        </div>
      )}

      {/* Messages Display */}
      {messages.length > 0 && (
        <div className="w-full max-w-2xl mt-8">
          <h2 className="text-lg font-medium text-gray-800 mb-4">입력된 메시지들:</h2>
          <div className="space-y-3">
            {messages.map((msg, index) => (
              <div key={index} className="bg-gray-50 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-sm font-medium text-gray-600">메시지 {index + 1}:</span>
                  <span className="text-xs text-gray-500">JSON 형태</span>
                </div>
                <div className="bg-white rounded p-3 border">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                    {JSON.stringify(msg, null, 2)}
                  </pre>
                </div>
                <div className="mt-2 text-sm text-gray-600">
                  <strong>내용:</strong> {msg.message}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Additional Info */}
      <div className="mt-8 text-center">
        <p className="text-sm text-gray-500">
          AI가 당신의 질문에 답변해드립니다
        </p>
      </div>
    </div>
  );
}
