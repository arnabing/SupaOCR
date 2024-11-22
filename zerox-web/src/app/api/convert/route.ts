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
            size: `${(file?.size || 0) / 1024} KB`,
            type: file?.type
        })

        if (!file) {
            console.log('❌ [API Route] No file provided')
            return NextResponse.json(
                { error: 'No file provided' },
                { status: 400 }
            )
        }

        console.log(`🌐 [API Route] Sending to backend: ${BACKEND_URL}/convert`)
        const response = await fetch(`${BACKEND_URL}/convert`, {
            method: 'POST',
            body: formData,
        }).catch(error => {
            console.error('🔴 [API Route] Network error:', {
                message: error.message,
                cause: error.cause
            })
            throw error
        })

        if (!response.ok) {
            const errorData = await response.json()
            console.error('❌ [API Route] Backend error:', {
                status: response.status,
                error: errorData
            })
            return NextResponse.json(
                { error: errorData.error || 'Backend processing failed' },
                { status: response.status }
            )
        }

        const data = await response.json()
        console.log('✅ [API Route] Success:', {
            markdownLength: data.markdown?.length || 0
        })
        return NextResponse.json(data)
    } catch (error: any) {
        console.error('💥 [API Route] Error:', {
            name: error?.name,
            message: error?.message
        })
        return NextResponse.json(
            { error: 'Failed to process file' },
            { status: 500 }
        )
    }
} 