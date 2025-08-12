// Railway API 클라이언트 설정
const RAILWAY_API_URL = process.env.RAILWAY_API_URL || 'https://your-gateway-url.railway.app';

// API 클라이언트 함수들
export async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const url = `${RAILWAY_API_URL}${endpoint}`;
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.statusText}`);
  }

  return response.json();
}

// 사용자 관련 API 함수들
export async function getUserById(userId: string, token: string) {
  return apiRequest(`/api/v1/users/${userId}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
}

export async function updateUser(userId: string, userData: any, token: string) {
  return apiRequest(`/api/v1/users/${userId}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(userData),
  });
}

// 데이터베이스 연결 함수는 더 이상 필요하지 않음
export async function getDatabase() {
  throw new Error('Local database is not supported. Use Railway API instead.');
}

export async function closeDatabase() {
  // 더 이상 필요하지 않음
}
