import { NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export async function POST(request: Request) {
    console.log('🔵 [Debug] BACKEND_URL:', BACKEND_URL)

    try {
        const formData = await request.formData()
        const file = formData.get('file') as File

        // Log file details
        console.log('📋 [Debug] File details:', {
            name: file?.name,
            size: file?.size ? `${file.size / 1024} KB` : 'unknown',
            type: file?.type || 'unknown'
        })

        // Log request to backend
        console.log('📤 [Debug] Sending to:', `${BACKEND_URL}/convert`)

        const response = await fetch(`${BACKEND_URL}/convert`, {
            method: 'POST',
            body: formData,
        })

        // Log backend response
        console.log('📥 [Debug] Backend response:', {
            status: response.status,
            ok: response.ok,
            type: response.type
        })

        const responseText = await response.text()
        console.log('📄 [Debug] Response text:', responseText)

        // Try to parse as JSON
        let data
        try {
            data = JSON.parse(responseText)
        } catch (e) {
            console.error('❌ [Debug] Failed to parse response as JSON:', responseText)
            throw new Error('Invalid JSON response from backend')
        }

        return NextResponse.json(data)
    } catch (error: any) {
        console.error('💥 [Debug] Full error:', {
            message: error?.message,
            cause: error?.cause,
            stack: error?.stack
        })
        return NextResponse.json({ error: 'Failed to process file' }, { status: 500 })
    }
} 