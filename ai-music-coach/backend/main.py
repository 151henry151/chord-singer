"""
Main entry point for the AI Music Coach backend application.
"""

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import tempfile
import shutil
import uuid
import time
from typing import Dict, Any

from backend.api.routes import router
from utils.config import get_api_config
from backend.audio_processing.audio_utils import preprocess_audio
from backend.audio_processing.chord_detection import ChordDetector
from backend.synthesis.vocal_synthesis import VocalSynthesizer
from backend.audio_processing.melody_extraction import MelodyExtractor

# Get configuration
config = get_api_config()

# Global status tracking
processing_status = {}

class MusicCoachProcessor:
    """
    Main processor class that orchestrates chord detection and vocal synthesis.
    """
    
    def __init__(self):
        """Initialize the processor with chord detector, melody extractor, and vocal synthesizer."""
        self.chord_detector = ChordDetector()
        self.melody_extractor = MelodyExtractor()
        self.vocal_synthesizer = VocalSynthesizer()
    
    def process_song(self, input_audio_path: str, output_audio_path: str, job_id: str) -> Dict[str, Any]:
        """
        Process a song to create sung chord vocals, pitch-mapped to the melody.
        Args:
            input_audio_path: Path to the input audio file
            output_audio_path: Path where the output audio will be saved
            job_id: Unique job identifier for status tracking
        Returns:
            Dictionary containing detected chords, melody, and output file path
        """
        try:
            # Update status
            processing_status[job_id] = {"status": "preprocessing", "progress": 10, "message": "Preprocessing audio..."}
            
            # Step 1: Preprocess the audio
            print(f"Preprocessing audio: {input_audio_path}")
            processed_audio_path, audio_duration = preprocess_audio(input_audio_path)
            
            # Update status
            processing_status[job_id] = {"status": "detecting_chords", "progress": 30, "message": "Detecting chords..."}
            
            # Step 2: Detect chords
            print(f"Detecting chords in audio...")
            detected_chords = self.chord_detector.detect_chords(processed_audio_path)
            
            # Update status
            processing_status[job_id] = {"status": "extracting_melody", "progress": 50, "message": "Extracting melody..."}
            
            # Step 3: Extract melody contour
            print(f"Extracting melody contour...")
            melody_contour = self.melody_extractor.extract_melody(processed_audio_path)
            
            # Update status
            processing_status[job_id] = {"status": "synthesizing", "progress": 70, "message": "Synthesizing vocals..."}
            
            # Step 4: Synthesize sung chord vocals (pitch-mapped)
            print(f"Synthesizing sung chord vocals (pitch-mapped)...")
            output_path = self.vocal_synthesizer.synthesize_sung_chord_vocals(
                detected_chords, melody_contour, audio_duration, output_audio_path
            )
            
            # Update status
            processing_status[job_id] = {"status": "completed", "progress": 100, "message": "Processing complete!"}
            
            # Clean up processed audio file
            if os.path.exists(processed_audio_path):
                os.unlink(processed_audio_path)
            
            return {
                "detected_chords": detected_chords,
                "melody_contour": melody_contour,
                "audio_duration": audio_duration,
                "output_file_path": output_path,
                "chord_count": len(detected_chords)
            }
            
        except Exception as e:
            # Update status with error
            processing_status[job_id] = {"status": "error", "progress": 0, "message": f"Error: {str(e)}"}
            
            # Clean up processed audio file if it exists
            if 'processed_audio_path' in locals() and os.path.exists(processed_audio_path):
                os.unlink(processed_audio_path)
            raise Exception(f"Error processing song: {str(e)}")


# Initialize the processor
processor = MusicCoachProcessor()

app = FastAPI(
    title="AI Music Coach",
    description="An AI-powered music learning tool for chord progression training",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config['frontend_url']],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Create necessary directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
os.makedirs("ml_models", exist_ok=True)


@app.post("/process-song/")
async def process_song_endpoint(file: UploadFile = File(...)):
    """
    Process an uploaded song to create spoken chord vocals.
    
    Args:
        file: Uploaded audio file
        
    Returns:
        Job ID for tracking progress
    """
    # Validate file type
    allowed_types = ["audio/mpeg", "audio/wav", "audio/flac", "audio/mp4", "audio/ogg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Initialize status
    processing_status[job_id] = {"status": "starting", "progress": 0, "message": "Starting processing..."}
    
    # Create temporary files
    temp_input_path = None
    temp_output_path = None
    
    try:
        # Save uploaded file to temporary location
        temp_input_path = tempfile.mktemp(suffix=os.path.splitext(file.filename)[1])
        with open(temp_input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create temporary output file
        temp_output_path = tempfile.mktemp(suffix=".wav")
        
        # Process the song
        result = processor.process_song(temp_input_path, temp_output_path, job_id)
        
        # Return job ID for status tracking
        return {"job_id": job_id, "message": "Processing started"}
        
    except Exception as e:
        # Update status with error
        processing_status[job_id] = {"status": "error", "progress": 0, "message": f"Error: {str(e)}"}
        raise HTTPException(status_code=500, detail=f"Error processing song: {str(e)}")
        
    finally:
        # Clean up temporary files
        if temp_input_path and os.path.exists(temp_input_path):
            os.unlink(temp_input_path)


@app.get("/status/{job_id}")
async def get_processing_status(job_id: str):
    """
    Get the processing status for a job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Current processing status
    """
    if job_id not in processing_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    status = processing_status[job_id]
    
    # If completed, include download link
    if status["status"] == "completed":
        status["download_url"] = f"/download/{job_id}"
    
    return status


@app.get("/download/{job_id}")
async def download_result(job_id: str):
    """
    Download the processed audio file.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Processed audio file
    """
    if job_id not in processing_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    status = processing_status[job_id]
    if status["status"] != "completed":
        raise HTTPException(status_code=400, detail="Processing not complete")
    
    # For now, return a placeholder - in a real implementation, you'd store the file path
    # and return the actual processed file
    return {"message": "Download endpoint - file would be returned here"}


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "AI Music Coach API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "process_song": "/process-song/",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-music-coach"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config['host'],
        port=config['port'],
        reload=config['debug']
    ) 