"use client"

import { useCallback, useState } from "react"
import { useDropzone } from "react-dropzone"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Upload, FileText, ArrowRight, Loader2 } from "lucide-react"

interface FileUploaderProps {
    onConversionComplete: (markdown: string, file: File) => void
}

export function FileUploader({ onConversionComplete }: FileUploaderProps) {
    const [file, setFile] = useState<File | null>(null)
    const [isLoading, setIsLoading] = useState(false)

    const onDrop = useCallback((acceptedFiles: File[]) => {
        console.log('📁 [FileUploader] File dropped:', acceptedFiles[0].name)
        setFile(acceptedFiles[0])
    }, [])

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        multiple: false
    })

    const handleConvert = async () => {
        if (!file) return
        console.log('📤 [FileUploader] Starting file conversion for:', file.name)
        setIsLoading(true)
        setIsLoading(true)
        const formData = new FormData()
        formData.append('file', file)
        console.log('📦 [FileUploader] FormData created with file')
        console.log('📦 [FileUploader] FormData created with file')
        try {
            console.log('🔄 [FileUploader] Sending request to API route')
            const response = await fetch('/api/convert', {
                method: 'POST',
                body: formData,
            })

            const data = await response.json()

            if (!response.ok) {
                console.error('❌ [FileUploader] API error:', {
                    status: response.status,
                    error: data.error
                })
                throw new Error(data.error || `API returned ${response.status}`)
            }

            console.log('✅ [FileUploader] Received response from API route')

            if (data.markdown) {
                console.log('📝 [FileUploader] Markdown received, updating view')
                onConversionComplete(data.markdown, file)
            }
        } catch (error) {
            console.error('❌ [FileUploader] Error:', error)
            // TODO: Add user-facing error message
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <Card className="relative overflow-hidden backdrop-blur-sm bg-background/95 border border-muted">
            <div
                {...getRootProps()}
                className="border-2 border-dashed border-muted rounded-lg m-4 p-8 text-center cursor-pointer transition-all hover:border-primary/50"
            >
                <input {...getInputProps()} />
                <div className="space-y-4">
                    <div className="w-16 h-16 mx-auto rounded-full bg-primary/10 flex items-center justify-center">
                        <Upload className="w-8 h-8 text-primary" />
                    </div>
                    {isDragActive ? (
                        <p className="text-lg font-medium">Drop it here...</p>
                    ) : (
                        <>
                            <p className="text-lg font-medium">Drag & drop your file here</p>
                            <p className="text-sm text-muted-foreground">
                                or click to browse
                            </p>
                        </>
                    )}
                </div>
            </div>
            {file && (
                <div className="p-4 border-t bg-muted/50">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <FileText className="w-4 h-4 text-primary" />
                            <span className="text-sm font-medium">{file.name}</span>
                        </div>
                        <Button
                            onClick={handleConvert}
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                                <>
                                    Convert to Markdown
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </>
                            )}
                        </Button>
                    </div>
                </div>
            )}
        </Card>
    )
} 