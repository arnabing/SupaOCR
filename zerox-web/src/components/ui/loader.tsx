import { Loader2 } from "lucide-react"

export function Loader({ text = "Processing..." }: { text?: string }) {
    return (
        <div className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            <p>{text}</p>
        </div>
    )
}
