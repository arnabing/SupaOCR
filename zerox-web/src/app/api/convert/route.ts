import { NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export async function POST(request: Request) {
    console.log('🔵 [Debug] Starting conversion request')
    console.log('🔵 [Debug] BACKEND_URL:', BACKEND_URL)

    try {
        const formData = await request.formData()
        const file = formData.get('file') as File

        if (!file) {
            console.error('❌ [Debug] No file in request')
            return NextResponse.json({ error: 'No file provided' }, { status: 400 })
        }

        console.log('📋 [Debug] File details:', {
            name: file.name,
            size: `${file.size / 1024} KB`,
            type: file.type
        })

        const response = await fetch(`${BACKEND_URL}/convert`, {
            method: 'POST',
            body: formData,
            signal: AbortSignal.timeout(120000)
        })

        const data = await response.json()
        console.log('📥 [Debug] Response data:', data)

        if (!response.ok || data.error) {
            console.error('❌ [Debug] Backend error:', data)
            return NextResponse.json({
                error: data.error || 'Backend processing failed',
                details: data.traceback
            }, { status: response.status || 500 })
        }

        return NextResponse.json(data)
    } catch (error: any) {
        console.error('💥 [Debug] Request failed:', error)
        return NextResponse.json({
            error: 'Failed to process file',
            details: error.message
        }, { status: 500 })
    }
} 