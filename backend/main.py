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
from litellm import litellm

load_dotenv()

print("\n🚀 [Init] Starting server...")
openai_key = os.getenv('OPENAI_API_KEY')

# Validate API key
if not openai_key:
    print("❌ [Init] No OpenAI API key found")
    raise Exception("OpenAI API key not found in environment")
else:
    print("✅ [Init] OpenAI API key found")

# Configure LiteLLM for Omni provider
os.environ["LITELLM_MODEL_CONFIG"] = """{
    "model_list": [
        {
            "model_name": "gpt-4o-mini",
            "litellm_params": {
                "model": "gpt-4o-mini",
                "api_base": "https://api.omnitool.ai/v1",
                "api_key": "%s",
                "api_type": "openai"
            }
        }
    ]
}""" % openai_key

print(f"🔑 [Init] Using model: gpt-4o-mini")

app = FastAPI()

# Get the frontend URL from environment
FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://your-vercel-app.vercel.app')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://supaocr.vercel.app",
        "http://localhost:3000",
        "https://supaocr-backend-production.up.railway.app"
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
        # Log OpenAI key details (first 8 chars only)
        logger.info(f"Using OpenAI key starting with: {openai_key[:8]}...")
        
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
        try:
            result = await zerox(
                file_path=file_path,
                model="gpt-4o-mini",
                cleanup=True,
                litellm_params={
                    "api_base": "https://api.omnitool.ai/v1",
                    "api_key": openai_key,
                    "api_type": "openai"
                }
            )
        except Exception as zerox_error:
            logger.error(f"Zerox processing error: {str(zerox_error)}")
            raise
        
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
    return {
        "status": "ok",
        "environment": {
            "frontend_url": os.getenv('FRONTEND_URL'),
            "port": os.getenv('PORT'),
            "api_key_configured": bool(openai_key)
        }
    }

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

@app.get("/test-openai")
async def test_openai():
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=openai_key)
        logger.info("Testing OpenAI connection...")
        
        # Test with a simple completion
        response = await client.chat.completions.create(
            model="gpt-4-vision-preview",  # Try the official model name
            messages=[{
                "role": "user", 
                "content": "Hello, can you see this message?"
            }]
        )
        
        return {
            "status": "ok",
            "message": "OpenAI API key is working",
            "model": "gpt-4-vision-preview",
            "response": response.choices[0].message.content
        }
    except Exception as e:
        logger.error(f"OpenAI test failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "OpenAI API key test failed",
            "key_prefix": openai_key[:8] if openai_key else None
        }

litellm.set_verbose = True
