"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import ReactMarkdown from 'react-markdown'

interface ConversionViewProps {
    markdown?: string
    file?: File
}

export function ConversionView({ markdown, file }: ConversionViewProps) {
    const [previewUrl, setPreviewUrl] = useState<string>()

    useEffect(() => {
        console.log('📝 [ConversionView] Received markdown update:', markdown?.length ?? 0)
    }, [markdown])

    useEffect(() => {
        if (file) {
            const url = URL.createObjectURL(file)
            setPreviewUrl(url)
            return () => URL.revokeObjectURL(url)
        }
    }, [file])

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="p-4">
                <h2 className="text-lg font-semibold mb-2">Original Document</h2>
                <div className="min-h-[400px] bg-muted rounded-lg p-4 overflow-hidden relative">
                    {previewUrl && (
                        <object
                            data={previewUrl}
                            type="application/pdf"
                            className="absolute inset-0 w-full h-full object-contain rounded border border-muted"
                        >
                            <p>PDF preview not available</p>
                        </object>
                    )}
                </div>
            </Card>
            <Card className="p-4">
                <h2 className="text-lg font-semibold mb-2">Markdown Output</h2>
                <div className="min-h-[400px] bg-muted rounded-lg p-4 prose prose-sm max-w-none overflow-auto">
                    {markdown ? (
                        <ReactMarkdown>{markdown}</ReactMarkdown>
                    ) : (
                        'Converted markdown will appear here'
                    )}
                </div>
            </Card>
        </div>
    )
} 