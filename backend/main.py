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
from fastapi.responses import JSONResponse

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

# Add at startup
print("\n=== Environment Variables ===")
print("OPENAI_API_KEY:", "✓ Set" if openai_key else "✗ Missing")
print("FRONTEND_URL:", os.getenv('FRONTEND_URL', '✗ Missing'))
print("PORT:", os.getenv('PORT', '✗ Missing'))

@app.post("/convert")
async def convert_document(file: UploadFile = File(...)):
    request_id = datetime.datetime.now().isoformat()
    logger.info(f"=== Starting Conversion (Request ID: {request_id}) ===")
    
    # Validate environment
    if not openai_key:
        logger.error("OpenAI API key missing")
        raise HTTPException(
            status_code=500,
            detail={"error": "OpenAI API key not configured", "request_id": request_id}
        )

    try:
        # Log file details
        logger.info(f"File received: {file.filename} ({file.content_type})")
        
        # Save file temporarily
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        file_size = os.path.getsize(file_path)
        logger.info(f"File saved: {file_path} ({file_size/1024:.1f} KB)")

        # Process with zerox
        logger.info(f"Starting zerox processing with model: gpt-4o-mini")
        result = await zerox(
            file_path=file_path,
            model="gpt-4o-mini",
            openai_api_key=openai_key,
            cleanup=True
        )
        
        # Generate response
        markdown = "\n\n".join(page.content for page in result.pages)
        logger.info(f"Conversion complete. Generated {len(markdown)} chars of markdown")
        
        return JSONResponse(
            status_code=200,
            content={
                "markdown": markdown,
                "request_id": request_id,
                "stats": {
                    "file_size": file_size,
                    "markdown_length": len(markdown)
                }
            }
        )

    except Exception as e:
        logger.error(f"Error processing request {request_id}: {str(e)}")
        logger.error("Traceback:", exc_info=True)
        
        error_detail = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "request_id": request_id
        }
        
        return JSONResponse(
            status_code=500,
            content=error_detail
        )

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
