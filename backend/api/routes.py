"""
API routes for the AI Music Coach application.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import uuid
import os
from typing import List

from .models import AudioUpload, ProcessingResult, ProcessingRequest, ChordInfo

router = APIRouter(prefix="/api/v1", tags=["chord-singer"])

# In-memory storage for demo (use database in production)
uploaded_files = {}
processing_jobs = {}


@router.post("/upload", response_model=AudioUpload)
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload an audio file for processing.
    
    Args:
        file: Audio file to upload
        
    Returns:
        AudioUpload: Information about the uploaded file
    """
    # Validate file type
    allowed_types = ["audio/mpeg", "audio/wav", "audio/flac", "audio/mp4"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    
    # Save file (in production, use cloud storage)
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Store file information
    uploaded_files[file_id] = {
        "filename": file.filename,
        "file_path": file_path,
        "file_size": len(content),
        "content_type": file.content_type
    }
    
    return AudioUpload(
        filename=file.filename,
        file_size=len(content),
        content_type=file.content_type
    )


@router.post("/process", response_model=ProcessingResult)
async def process_audio(
    request: ProcessingRequest,
    background_tasks: BackgroundTasks
):
    """
    Process uploaded audio to create chord-singing cover.
    
    Args:
        request: Processing request with file ID and options
        background_tasks: FastAPI background tasks
        
    Returns:
        ProcessingResult: Processing job information
    """
    # Validate file exists
    if request.audio_file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    file_info = uploaded_files[request.audio_file_id]
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Create initial job result
    job_result = ProcessingResult(
        job_id=job_id,
        status="processing",
        original_filename=file_info["filename"],
        chord_progression=[]  # Will be populated during processing
    )
    
    processing_jobs[job_id] = job_result
    
    # Add background task for processing
    background_tasks.add_task(
        process_audio_background,
        job_id,
        request.audio_file_id,
        request.options
    )
    
    return job_result


@router.get("/jobs/{job_id}", response_model=ProcessingResult)
async def get_job_status(job_id: str):
    """
    Get the status of a processing job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        ProcessingResult: Current job status and results
    """
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return processing_jobs[job_id]


@router.get("/jobs/{job_id}/download")
async def download_result(job_id: str):
    """
    Download the processed audio file.
    
    Args:
        job_id: Job identifier
        
    Returns:
        FileResponse: Processed audio file
    """
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = processing_jobs[job_id]
    
    if job.status != "completed" or not job.output_filename:
        raise HTTPException(status_code=400, detail="Job not completed or no output file")
    
    file_path = os.path.join("outputs", job.output_filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Output file not found")
    
    return FileResponse(
        path=file_path,
        filename=job.output_filename,
        media_type="audio/wav"
    )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "chord-singer-api"}


async def process_audio_background(job_id: str, file_id: str, options: dict):
    """
    Background task for processing audio.
    
    Args:
        job_id: Job identifier
        file_id: File identifier
        options: Processing options
    """
    try:
        # TODO: Implement actual audio processing
        # This is a placeholder implementation
        
        file_info = uploaded_files[file_id]
        
        # Simulate processing time
        import asyncio
        await asyncio.sleep(5)
        
        # Generate dummy chord progression
        chord_progression = [
            ChordInfo(chord="C", start_time=0.0, end_time=2.0, confidence=0.95),
            ChordInfo(chord="Am", start_time=2.0, end_time=4.0, confidence=0.92),
            ChordInfo(chord="F", start_time=4.0, end_time=6.0, confidence=0.88),
            ChordInfo(chord="G", start_time=6.0, end_time=8.0, confidence=0.91)
        ]
        
        # Update job result
        job_result = processing_jobs[job_id]
        job_result.status = "completed"
        job_result.chord_progression = chord_progression
        job_result.output_filename = f"output_{job_id}.wav"
        job_result.processing_time = 5.0
        
    except Exception as e:
        # Update job with error
        job_result = processing_jobs[job_id]
        job_result.status = "failed"
        job_result.error_message = str(e) 