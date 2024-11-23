import { NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

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
        })

        const responseText = await response.text()
        console.log('📥 [Debug] Raw response:', responseText)

        try {
            const data = JSON.parse(responseText)

            if (!response.ok || data.error) {
                console.error('❌ [Debug] Backend error:', {
                    status: response.status,
                    error: data.error,
                    type: data.type,
                    requestId: data.request_id
                })

                return NextResponse.json({
                    error: data.error || 'Backend processing failed',
                    requestId: data.request_id
                }, { status: response.status })
            }

            console.log('✅ [Debug] Conversion successful:', {
                requestId: data.request_id,
                stats: data.stats
            })

            return NextResponse.json(data)

        } catch (parseError) {
            console.error('❌ [Debug] Failed to parse response:', responseText)
            return NextResponse.json({
                error: 'Invalid response from backend',
                details: responseText
            }, { status: 500 })
        }
    } catch (error: any) {
        console.error('💥 [Debug] Request failed:', error)
        return NextResponse.json({
            error: 'Failed to process file',
            details: error.message
        }, { status: 500 })
    }
} 