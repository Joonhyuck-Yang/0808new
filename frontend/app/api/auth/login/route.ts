import { NextRequest, NextResponse } from 'next/server';

const RAILWAY_API_URL = process.env.RAILWAY_API_URL || 'https://your-gateway-url.railway.app';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password } = body;

    // 입력 검증
    if (!email || !password) {
      return NextResponse.json(
        { success: false, message: '이메일과 비밀번호를 입력해주세요.' },
        { status: 400 }
      );
    }

    // Railway API로 로그인 요청
    const response = await fetch(`${RAILWAY_API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { success: false, message: data.message || '로그인에 실패했습니다.' },
        { status: response.status }
      );
    }

    // 응답에 토큰 포함
    const apiResponse = NextResponse.json(
      { 
        success: true, 
        message: '로그인 성공',
        user: data.user,
        token: data.token
      },
      { status: 200 }
    );

    // 쿠키에 토큰 설정
    if (data.token) {
      apiResponse.cookies.set('auth-token', data.token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        maxAge: 24 * 60 * 60 // 24시간
      });
    }

    return apiResponse;

  } catch (error) {
    console.error('로그인 오류:', error);
    return NextResponse.json(
      { success: false, message: '서버 오류가 발생했습니다.' },
      { status: 500 }
    );
  }
}
