from fastapi import FastAPI, UploadFile, File, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pyzerox import zerox
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

print("\n🚀 [Init] Starting server...")
openai_key = os.getenv('OPENAI_API_KEY')

# Validate API key
if not openai_key:
    print("❌ [Init] No OpenAI API key found")
elif not openai_key.startswith('sk-'):
    print("❌ [Init] Invalid OpenAI key format. Should start with 'sk-'")
elif 'proj' in openai_key:
    print("❌ [Init] Detected project-specific key. Please use OpenAI API key")
else:
    print("✅ [Init] OpenAI API key format valid")

print(f"🔑 [Init] Using model: gpt-4o-mini")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://supaocr.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/convert")
async def convert_document(file: UploadFile = File(...)):
    try:
        print("\n📄 [File] Received:", file.filename)
        print(f"📄 [File] Type: {file.content_type}")

        # Save file temporarily
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        file_size = os.path.getsize(file_path)
        print(f"💾 [File] Saved: {file_path} ({file_size/1024:.1f} KB)")

        # Process with zerox
        print("\n🔄 [Zerox] Starting conversion...")
        print(f"🛠️ [Zerox] Using model: gpt-4o-mini")
        print(f"🔑 [Zerox] Using OpenAI key: {openai_key[:8]}...")

        # Configure litellm (based on previous working code)
        os.environ["OPENAI_API_KEY"] = openai_key

        result = await zerox(
            file_path=file_path,
            model="gpt-4o-mini",
            cleanup=True,
            maintain_format=True
        )

        print(f"\n✅ [Zerox] Conversion complete")
        print(f"📊 [Stats] Pages processed: {len(result.pages)}")
        print(f"⏱️ [Stats] Time taken: {result.completion_time}ms")
        print(f"📥 [Stats] Input tokens: {result.input_tokens}")
        print(f"📤 [Stats] Output tokens: {result.output_tokens}")

        # Clean up and return
        os.remove(file_path)
        print("🧹 [Cleanup] Removed temporary file")

        markdown = "\n\n".join(page.content for page in result.pages)
        print(f"📝 [Output] Markdown length: {len(markdown)} chars")
        
        return {"markdown": markdown}

    except Exception as e:
        print(f"\n❌ [Error] {type(e).__name__}: {str(e)}")
        print("\n🔍 [Debug] Full traceback:")
        import traceback
        print(traceback.format_exc())
        return {"error": str(e)}

@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/health")
async def health():
    return {"status": "ok"}
