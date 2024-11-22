import { NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export async function POST(request: Request) {
    console.log('🔵 [API Route] Starting file conversion request')
    console.log('🌐 [API Route] Using backend URL:', BACKEND_URL)

    try {
        const formData = await request.formData()
        const file = formData.get('file') as File
        console.log('📁 [API Route] File received:', {
            name: file?.name,
            size: file?.size,
            type: file?.type
        })

        if (!file) {
            console.log('❌ [API Route] No file provided')
            return NextResponse.json(
                { error: 'No file provided' },
                { status: 400 }
            )
        }

        console.log(`🌐 [API Route] Sending to backend: ${BACKEND_URL}/process`)
        const response = await fetch(`${BACKEND_URL}/process`, {
            method: 'POST',
            body: formData,
        }).catch(error => {
            console.error('🔴 [API Route] Network error:', {
                message: error.message,
                cause: error.cause,
                stack: error.stack
            })
            throw error
        })

        console.log('📡 [API Route] Backend response:', {
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries(response.headers.entries())
        })

        if (!response.ok) {
            const errorText = await response.text()
            console.error('❌ [API Route] Backend error response:', errorText)
            throw new Error(`Backend error: ${errorText}`)
        }

        const data = await response.json()
        console.log('✅ [API Route] Successfully received response')
        return NextResponse.json(data)
    } catch (error: any) {
        console.error('💥 [API Route] Error details:', {
            name: error?.name,
            message: error?.message,
            stack: error?.stack,
            cause: error?.cause
        })
        return NextResponse.json(
            { error: 'Failed to process file' },
            { status: 500 }
        )
    }
} 