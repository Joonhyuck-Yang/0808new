'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import axios from 'axios';

export default function SignupPage() {
  const router = useRouter();

  // Form state management - flow_master 테이블 구조에 맞춤
  const [formData, setFormData] = useState({
    name: '',           // text not null
    type: '',           // text null
    category: '',       // text null
    unit_id: ''         // uuid null (기본값은 gen_random_uuid())
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Form input handler
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // UUID 생성 함수 (간단한 버전)
  const generateUUID = () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  };

  // Signup form submission
  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // 필수 필드 확인 (name은 not null)
    if (!formData.name.trim()) {
      setError('이름은 필수 입력 항목입니다.');
      setIsLoading(false);
      return;
    }

    try {
      // flow_master 테이블 구조에 맞는 데이터 생성
      const signupData = {
        id: generateUUID(),           // uuid not null default gen_random_uuid()
        name: formData.name.trim(),   // text not null
        type: formData.type || null,  // text null
        category: formData.category || null, // text null
        unit_id: formData.unit_id || generateUUID() // uuid null default gen_random_uuid()
      };

      // 입력받은 데이터를 JSON 형태로 구성 (name: db 컬럼, value: 입력값)
      const inputData = {
        name: {
          name: formData.name.trim(),
          type: formData.type || null,
          category: formData.category || null,
          unit_id: formData.unit_id || generateUUID()
        },
        value: {
          name: formData.name.trim(),
          type: formData.type || null,
          category: formData.category || null,
          unit_id: formData.unit_id || generateUUID()
        }
      };

      // localStorage에 저장
      localStorage.setItem('flow_master_data', JSON.stringify(signupData));

      // axios를 사용해서 Gateway API로 데이터 전송
      console.log('🚀 회원가입 데이터 전송 시작...');
      
      // 도커 환경에서는 gateway 서비스 이름을 사용
      const apiUrl = 'http://gateway:8080/api/v1/signup';
      
      const response = await axios.post(apiUrl, signupData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log('✅ 회원가입 성공:', response.data);

      // 성공 메시지 - JSON 형태로 alert 표시
      alert(`flow_master 데이터가 생성되었습니다!\n\n${JSON.stringify(inputData, null, 2)}\n\n서버 응답: ${response.data.message}`);

      // 로그인 페이지로 이동
      router.push('/login?message=flow_master 데이터가 생성되었습니다.');
    } catch (error: any) {
      console.error('❌ 회원가입 실패:', error);
      if (error.response) {
        setError('회원가입 실패: ' + (error.response.data?.detail || error.response.statusText));
      } else if (error.request) {
        setError('서버에 연결할 수 없습니다. 8080번 포트가 실행 중인지 확인해주세요.');
      } else {
        setError('회원가입 실패: ' + error.message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-3xl shadow-2xl px-8 py-12">
          {/* Signup Title */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 tracking-tight mb-2">
              Flow Master 등록
            </h1>
            <p className="text-gray-600">
              새로운 flow_master 데이터를 생성하세요
            </p>
          </div>

          {/* Signup Form */}
          <form onSubmit={handleSignup} className="space-y-6">
            {/* Name Input - 필수 */}
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                이름 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="이름을 입력하세요"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
                required
              />
            </div>

            {/* Type Input - 선택 */}
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                타입
              </label>
              <select
                name="type"
                value={formData.type}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
              >
                <option value="">타입을 선택하세요</option>
                <option value="process">Process</option>
                <option value="workflow">Workflow</option>
                <option value="automation">Automation</option>
                <option value="manual">Manual</option>
              </select>
            </div>

            {/* Category Input - 선택 */}
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                카테고리
              </label>
              <select
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
              >
                <option value="">카테고리를 선택하세요</option>
                <option value="business">Business</option>
                <option value="technical">Technical</option>
                <option value="operational">Operational</option>
                <option value="management">Management</option>
              </select>
            </div>

            {/* Unit ID Input - 선택 */}
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Unit ID
              </label>
              <input
                type="text"
                name="unit_id"
                value={formData.unit_id}
                onChange={handleInputChange}
                placeholder="Unit ID (자동 생성됨)"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200 bg-gray-50"
                readOnly
              />
              <p className="text-xs text-gray-500 mt-1">Unit ID는 자동으로 생성됩니다.</p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}

            {/* Signup Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 text-white py-4 rounded-2xl hover:bg-blue-700 transition-all duration-200 font-medium text-lg shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? '생성 중...' : 'Flow Master 생성 (axios 전송)'}
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

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-600 text-sm">
              이미 계정이 있으신가요?{' '}
              <Link href="/login" className="text-blue-600 hover:text-blue-700 font-medium">
                로그인
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
