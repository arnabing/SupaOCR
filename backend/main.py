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
from time import time

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
    ],
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
    start_time = time()
    request_id = datetime.datetime.now().isoformat()
    logger.info(f"=== Starting Conversion (Request ID: {request_id}) ===")
    
    try:
        # Add timeout tracking
        logger.info(f"⏱️ Request started at: {start_time}")
        
        # Log detailed file information
        logger.info(f"📁 File details:")
        logger.info(f"  - Filename: {file.filename}")
        logger.info(f"  - Content type: {file.content_type}")
        logger.info(f"  - File object type: {type(file)}")
        
        # Log memory info before file operations
        logger.info("💾 Memory check before file operations:")
        logger.info(f"  - /tmp directory exists: {os.path.exists('/tmp')}")
        logger.info(f"  - /tmp directory writable: {os.access('/tmp', os.W_OK)}")
        
        # Save file with more detailed logging
        file_path = f"/tmp/{file.filename}"
        try:
            content = await file.read()
            logger.info(f"📄 Read file content:")
            logger.info(f"  - Content size: {len(content)} bytes")
            logger.info(f"  - Content type: {type(content)}")
            
            with open(file_path, "wb") as f:
                f.write(content)
                
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                logger.info(f"✅ File saved successfully:")
                logger.info(f"  - Path: {file_path}")
                logger.info(f"  - Size: {file_size/1024:.1f} KB")
            else:
                logger.error("❌ File not saved properly")
                
        except Exception as file_error:
            logger.error(f"❌ File handling error: {str(file_error)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail={"error": "File handling failed", "details": str(file_error)}
            )

        # Log zerox configuration
        logger.info("🔧 Zerox configuration:")
        logger.info(f"  - Model: gpt-4o-mini")
        logger.info(f"  - OpenAI key length: {len(openai_key)}")
        logger.info(f"  - API base: {os.getenv('OPENAI_API_BASE', 'default')}")

        # Process with zerox
        try:
            logger.info(f"🚀 Starting zerox at: {time() - start_time:.2f}s elapsed")
            result = await zerox(
                file_path=file_path,
                model="gpt-4o-mini",
                cleanup=True,
            )
            logger.info(f"✅ Zerox completed at: {time() - start_time:.2f}s elapsed")
            
        except Exception as zerox_error:
            logger.error(f"❌ Zerox error at {time() - start_time:.2f}s: {str(zerox_error)}")
            logger.error(f"Zerox error type: {type(zerox_error)}")
            logger.error(traceback.format_exc())
            raise

        return JSONResponse(
            status_code=200,
            content={
                "pages": [{
                    "content": page.content,
                    "page_number": idx + 1
                } for idx, page in enumerate(result.pages)],
                "request_id": request_id,
                "stats": {
                    "file_size": file_size,
                    "total_pages": len(result.pages),
                    "total_chars": sum(len(page.content) for page in result.pages)
                }
            }
        )

    except Exception as e:
        logger.error(f"❌ General error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "request_id": request_id}
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
