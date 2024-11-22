import { NextResponse } from 'next/server'

const BACKEND_URL = (process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000').replace('localhost', '127.0.0.1')

export async function POST(request: Request) {
    console.log('🔵 [API Route] Starting file conversion request')

    try {
        const formData = await request.formData()
        const file = formData.get('file') as File
        console.log('📁 [API Route] File received:', file?.name)

        if (!file) {
            console.log('❌ [API Route] No file provided')
            return NextResponse.json(
                { error: 'No file provided' },
                { status: 400 }
            )
        }

        console.log(`🌐 [API Route] Connecting to backend: ${BACKEND_URL}/convert`)
        const zeroxResponse = await fetch(`${BACKEND_URL}/convert`, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
            },
            body: formData,
        }).catch(error => {
            console.error('🔴 [API Route] Network error:', {
                message: error.message,
                cause: error.cause,
                code: error.cause?.code,
                address: error.cause?.address,
                port: error.cause?.port
            })
            throw error
        })

        console.log('📡 [API Route] Backend response status:', zeroxResponse.status)

        if (!zeroxResponse.ok) {
            const errorData = await zeroxResponse.json()
            console.error('❌ [API Route] Backend error:', errorData)
            throw new Error('Backend conversion failed')
        }

        const data = await zeroxResponse.json()
        console.log('✅ [API Route] Successfully received response from backend')
        return NextResponse.json(data)
    } catch (error: any) {
        console.error('💥 [API Route] Error details:', {
            name: error?.name || 'Unknown',
            message: error?.message || 'Unknown error',
            stack: error?.stack || 'No stack trace'
        })
        return NextResponse.json(
            { error: 'Failed to convert file' },
            { status: 500 }
        )
    }
} 