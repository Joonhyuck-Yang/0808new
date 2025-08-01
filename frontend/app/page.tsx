'use client';

import { useState } from 'react';

export default function Home() {
  const [inputValue, setInputValue] = useState('');

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
        <div className="relative">
          {/* Main Input Field */}
          <div className="relative bg-white border border-gray-200 rounded-2xl shadow-sm hover:shadow-md transition-shadow duration-200">
            <div className="flex items-center px-4 py-3">
              {/* Tools Button */}
              <div className="flex items-center mr-3">
                <button className="flex items-center text-gray-500 hover:text-gray-700 transition-colors duration-200">
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
                />
              </div>

              {/* Right Side Icons */}
              <div className="flex items-center space-x-3 ml-3">
                {/* Microphone Icon */}
                <button className="p-2 text-gray-500 hover:text-gray-700 transition-colors duration-200 rounded-full hover:bg-gray-100">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </button>

                {/* Send/Submit Icon */}
                <button className="p-2 text-gray-500 hover:text-gray-700 transition-colors duration-200 rounded-full hover:bg-gray-100">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          {/* Focus State Enhancement */}
          <div className="absolute inset-0 rounded-2xl pointer-events-none border-2 border-transparent focus-within:border-blue-500 transition-colors duration-200"></div>
        </div>
      </div>

      {/* Additional Info */}
      <div className="mt-8 text-center">
        <p className="text-sm text-gray-500">
          AI가 당신의 질문에 답변해드립니다
        </p>
      </div>
    </div>
  );
}
