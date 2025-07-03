"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class AudioUpload(BaseModel):
    """Model for audio upload request."""
    
    filename: str = Field(..., description="Name of the uploaded file")
    file_size: int = Field(..., description="Size of the file in bytes")
    content_type: str = Field(..., description="MIME type of the file")
    
    class Config:
        schema_extra = {
            "example": {
                "filename": "song.mp3",
                "file_size": 5242880,
                "content_type": "audio/mpeg"
            }
        }


class ChordInfo(BaseModel):
    """Model for chord information."""
    
    chord: str = Field(..., description="Chord name (e.g., 'C', 'Am', 'F#m')")
    start_time: float = Field(..., description="Start time in seconds")
    end_time: float = Field(..., description="End time in seconds")
    confidence: float = Field(..., description="Detection confidence (0-1)")


class ProcessingResult(BaseModel):
    """Model for audio processing result."""
    
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Processing status")
    original_filename: str = Field(..., description="Original uploaded filename")
    chord_progression: List[ChordInfo] = Field(..., description="Detected chord progression")
    output_filename: Optional[str] = Field(None, description="Generated output filename")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    created_at: datetime = Field(default_factory=datetime.now)
    error_message: Optional[str] = Field(None, description="Error message if processing failed")
    
    class Config:
        schema_extra = {
            "example": {
                "job_id": "job_12345",
                "status": "completed",
                "original_filename": "song.mp3",
                "chord_progression": [
                    {
                        "chord": "C",
                        "start_time": 0.0,
                        "end_time": 2.0,
                        "confidence": 0.95
                    },
                    {
                        "chord": "Am",
                        "start_time": 2.0,
                        "end_time": 4.0,
                        "confidence": 0.92
                    }
                ],
                "output_filename": "song_chord_singing.wav",
                "processing_time": 15.5,
                "created_at": "2024-01-01T12:00:00Z"
            }
        }


class ProcessingRequest(BaseModel):
    """Model for processing request."""
    
    audio_file_id: str = Field(..., description="ID of uploaded audio file")
    options: Dict[str, Any] = Field(default_factory=dict, description="Processing options")
    
    class Config:
        schema_extra = {
            "example": {
                "audio_file_id": "file_12345",
                "options": {
                    "tts_engine": "coqui-tts",
                    "language": "en",
                    "output_format": "wav"
                }
            }
        } 