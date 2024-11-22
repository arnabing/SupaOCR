from fastapi import FastAPI, UploadFile, File, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pyzerox import zerox
import os
from dotenv import load_dotenv
import datetime
import logging
from fastapi import HTTPException
import sys
import traceback

load_dotenv()

print("\n🚀 [Init] Starting server...")
openai_key = os.getenv('OPENAI_API_KEY')

# Validate API key
if not openai_key:
    print("❌ [Init] No OpenAI API key found")
    raise Exception("OpenAI API key not found in environment")
else:
    print("✅ [Init] OpenAI API key found")

print(f"🔑 [Init] Using model: gpt-4o-mini")

app = FastAPI()

# Get the frontend URL from environment
FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://your-vercel-app.vercel.app')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://supaocr.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("supaocr")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

@app.post("/convert")
async def convert_document(file: UploadFile = File(...)):
    if not openai_key:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured"
        )
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

@app.post("/process")
async def process_file(file: UploadFile):
    try:
        logger.info(f"Processing file: {file.filename}")
        logger.debug(f"File content type: {file.content_type}")
        
        # Save file temporarily
        file_path = f"/tmp/{file.filename}"
        content = await file.read()
        logger.debug(f"File size: {len(content)} bytes")
        
        with open(file_path, "wb") as f:
            f.write(content)
            
        # Process with zerox
        logger.info("Starting zerox processing")
        result = await zerox(
            file_path=file_path,
            model="gpt-4o-mini",
            cleanup=True
        )
        logger.info("Zerox processing complete")
        
        return {"markdown": "\n\n".join(page.content for page in result.pages)}
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        logger.error("Traceback:", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail={"error": str(e), "traceback": traceback.format_exc()}
        )
