'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import Link from 'next/link';

export default function LoginPage() {
  const router = useRouter();

  // Form state management
  const [formData, setFormData] = useState({
    id: '',
    password: ''
  });

  // Form input handler
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Login form submission
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 입력값을 JSON 형태로 변환 (ID와 password만)
    const loginData = {
      id: formData.id,
      password: formData.password
    };
    
    // JSON 형태로 저장 (localStorage에 저장)
    localStorage.setItem('loginData', JSON.stringify(loginData));
    
    // Alert로 JSON 데이터 표시
    alert(`로그인 데이터가 JSON 형태로 저장되었습니다:\n\n${JSON.stringify(loginData, null, 2)}`);
    
    console.log('Login attempt:', loginData);
    
    // 검증 없이 무조건 대시보드 페이지로 이동
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="bg-white rounded-3xl shadow-2xl px-8 py-12">
          {/* Login Title */}
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-gray-900 tracking-tight">
              Login
            </h1>
          </div>

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-8">
            {/* Username Input */}
            <div className="relative">
              <input
                type="text"
                name="id"
                value={formData.id}
                onChange={handleInputChange}
                placeholder="Username"
                className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                required
              />
            </div>

            {/* Password Input */}
            <div className="relative">
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Password"
                className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                required
              />
            </div>

            {/* Login Button */}
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-4 rounded-2xl hover:bg-blue-700 transition-all duration-200 font-medium text-lg shadow-sm"
            >
              Login
            </button>
          </form>

          {/* Divider */}
          <div className="mt-8">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">또는</span>
              </div>
            </div>
          </div>

          {/* Sign Up Button */}
          <div className="mt-6">
            <Link href="/signup">
              <button className="w-full bg-green-600 text-white py-4 rounded-2xl hover:bg-green-700 transition-all duration-200 font-medium text-lg shadow-sm">
                회원가입
              </button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
