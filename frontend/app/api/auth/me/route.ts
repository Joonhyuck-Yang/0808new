import { NextRequest, NextResponse } from 'next/server';

const RAILWAY_API_URL = process.env.RAILWAY_API_URL || 'https://your-gateway-url.railway.app';

export async function GET(request: NextRequest) {
  try {
    // 쿠키에서 토큰 가져오기
    const token = request.cookies.get('auth-token')?.value;

    if (!token) {
      return NextResponse.json(
        { success: false, message: '인증 토큰이 없습니다.' },
        { status: 401 }
      );
    }

    // Railway API로 사용자 정보 요청
    const response = await fetch(`${RAILWAY_API_URL}/api/v1/auth/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { success: false, message: data.message || '인증에 실패했습니다.' },
        { status: response.status }
      );
    }

    return NextResponse.json(
      { 
        success: true, 
        user: data.user
      },
      { status: 200 }
    );

  } catch (error) {
    console.error('인증 확인 오류:', error);
    return NextResponse.json(
      { success: false, message: '서버 오류가 발생했습니다.' },
      { status: 500 }
    );
  }
}
