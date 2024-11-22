"use client"

import { useState } from "react"
import { FileUploader } from "@/components/FileUploader"
import { ConversionView } from "@/components/ConversionView"

export default function Home() {
  const [markdown, setMarkdown] = useState<string>()
  const [previewFile, setPreviewFile] = useState<File>()

  const handleConversionComplete = (markdown: string, file: File) => {
    setMarkdown(markdown)
    setPreviewFile(file)
  }

  return (
    <main className="min-h-screen p-4 md:p-24">
      <div className="max-w-5xl mx-auto space-y-8">
        <h1 className="text-4xl font-bold text-center">SupaOCR to LLM</h1>
        <FileUploader onConversionComplete={handleConversionComplete} />
        <ConversionView markdown={markdown} file={previewFile} />
      </div>
    </main>
  )
}
