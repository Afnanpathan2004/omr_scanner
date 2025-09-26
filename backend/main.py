"""
FastAPI backend for OMR Checker application.
Handles image upload, processing, and evaluation.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import json
import uuid
from pathlib import Path
import logging
from typing import Optional

from models import OMRResult, ErrorResponse
from mock_omr_utils import OMRProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="OMR Checker API",
    description="Backend API for OMR sheet processing and evaluation",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize directories
UPLOAD_DIR = Path("uploads")
ANSWER_KEYS_DIR = Path("answer_keys")
RESULTS_DIR = Path("results")

for directory in [UPLOAD_DIR, ANSWER_KEYS_DIR, RESULTS_DIR]:
    directory.mkdir(exist_ok=True)

# Initialize OMR processor
omr_processor = OMRProcessor()

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "OMR Checker API is running", "status": "healthy"}

@app.get("/answer-keys")
async def get_available_answer_keys():
    """Get list of available answer keys."""
    try:
        answer_keys = []
        for file_path in ANSWER_KEYS_DIR.glob("*.json"):
            answer_keys.append(file_path.stem)
        return {"answer_keys": answer_keys}
    except Exception as e:
        logger.error(f"Error fetching answer keys: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch answer keys")

@app.post("/upload", response_model=OMRResult)
async def upload_and_process_omr(
    file: UploadFile = File(...),
    exam_key: str = Form(default="exam1")
):
    """
    Upload and process OMR sheet image.
    
    Args:
        file: Uploaded image file (.jpg, .jpeg, .png)
        exam_key: Answer key identifier (default: exam1)
    
    Returns:
        OMRResult: Processing results with score and analysis
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Please upload an image file."
            )
        
        allowed_extensions = {'.jpg', '.jpeg', '.png'}
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Check file size (5MB limit)
        file_content = await file.read()
        if len(file_content) > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(
                status_code=400,
                detail="File size too large. Maximum allowed size is 5MB."
            )
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        logger.info(f"File saved: {file_path}")
        
        # Load answer key
        answer_key_path = ANSWER_KEYS_DIR / f"{exam_key}.json"
        if not answer_key_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Answer key '{exam_key}' not found"
            )
        
        with open(answer_key_path, 'r') as f:
            answer_key = json.load(f)
        
        logger.info(f"Loaded answer key: {exam_key}")
        
        # Process OMR sheet
        result = omr_processor.process_omr_sheet(str(file_path), answer_key)
        
        # Clean up uploaded file (optional - comment out for debugging)
        try:
            os.remove(file_path)
            logger.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up file {file_path}: {str(e)}")
        
        # Save result for logging (optional)
        result_id = str(uuid.uuid4())
        result_path = RESULTS_DIR / f"{result_id}.json"
        with open(result_path, 'w') as f:
            json.dump(result.dict(), f, indent=2)
        
        logger.info(f"Processing completed. Score: {result.score}/{result.total}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during processing: {str(e)}"
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8009, reload=True)
