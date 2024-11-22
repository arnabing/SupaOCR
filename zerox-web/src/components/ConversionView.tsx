"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"

interface ConversionViewProps {
    markdown?: string
    file?: File
}

export function ConversionView({ markdown, file }: ConversionViewProps) {
    const [previewUrl, setPreviewUrl] = useState<string>()

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
                        <embed
                            src={previewUrl}
                            type="application/pdf"
                            className="absolute inset-0 w-full h-full object-contain rounded border border-muted"
                        />
                    )}
                </div>
            </Card>
            <Card className="p-4">
                <h2 className="text-lg font-semibold mb-2">Markdown Output</h2>
                <div className="min-h-[400px] bg-muted rounded-lg p-4 font-mono text-sm whitespace-pre-wrap overflow-auto">
                    {markdown || 'Converted markdown will appear here'}
                </div>
            </Card>
        </div>
    )
} 