import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const fail = searchParams.get('fail');

    if (fail === 'true') {
      return NextResponse.json(
        { status: 'unhealthy', error: 'Explicit failure requested' },
        { status: 503 }
      );
    }

    return NextResponse.json({ status: 'healthy' });
  } catch (error) {
    return NextResponse.json(
      { status: 'unhealthy', error: 'Internal server error' },
      { status: 500 }
    );
  }
}
