"""
Audio utilities for general audio processing tasks.
"""

import numpy as np
import librosa
from pydub import AudioSegment
from typing import Tuple, Optional
import os
import tempfile


def preprocess_audio(audio_path: str) -> Tuple[str, float]:
    """
    Preprocess audio file to standard format.
    
    Args:
        audio_path: Path to the input audio file
        
    Returns:
        Tuple of (processed_file_path, duration_in_seconds)
        
    Raises:
        ValueError: If the file type is not supported
        FileNotFoundError: If the audio file doesn't exist
        Exception: For other audio processing errors
    """
    # Check if file exists
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    # Define supported audio formats
    supported_formats = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.wma']
    file_extension = os.path.splitext(audio_path)[1].lower()
    
    if file_extension not in supported_formats:
        raise ValueError(f"Unsupported file format: {file_extension}. Supported formats: {', '.join(supported_formats)}")
    
    try:
        # Load audio using pydub
        audio = AudioSegment.from_file(audio_path)
        
        # Convert to mono channel
        if audio.channels > 1:
            audio = audio.set_channels(1)
        
        # Convert to 44.1kHz sample rate
        if audio.frame_rate != 44100:
            audio = audio.set_frame_rate(44100)
        
        # Get duration in seconds
        duration_seconds = len(audio) / 1000.0
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_file_path = temp_file.name
        temp_file.close()
        
        # Export processed audio to temporary WAV file
        audio.export(temp_file_path, format='wav')
        
        return temp_file_path, duration_seconds
        
    except Exception as e:
        # Clean up temporary file if it was created
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise Exception(f"Error preprocessing audio file: {str(e)}")


class AudioProcessor:
    """
    A class for general audio processing utilities.
    """
    
    def __init__(self, target_sr: int = 22050):
        """
        Initialize the audio processor.
        
        Args:
            target_sr: Target sample rate for processing
        """
        self.target_sr = target_sr
    
    def preprocess_audio(self, audio_path: str) -> Tuple[str, float]:
        """
        Preprocess audio file to standard format using class method.
        
        Args:
            audio_path: Path to the input audio file
            
        Returns:
            Tuple of (processed_file_path, duration_in_seconds)
        """
        return preprocess_audio(audio_path)
    
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        Load audio file and convert to target sample rate.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (audio_array, sample_rate)
        """
        audio, sr = librosa.load(file_path, sr=self.target_sr)
        return audio, sr
    
    def save_audio(self, audio: np.ndarray, file_path: str, sr: int = 22050):
        """
        Save audio array to file.
        
        Args:
            audio: Audio array
            file_path: Output file path
            sr: Sample rate
        """
        import soundfile as sf
        sf.write(file_path, audio, sr)
    
    def normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        Normalize audio to prevent clipping.
        
        Args:
            audio: Audio array
            
        Returns:
            Normalized audio array
        """
        return librosa.util.normalize(audio)
    
    def trim_silence(self, audio: np.ndarray, threshold_db: float = -60) -> np.ndarray:
        """
        Trim silence from beginning and end of audio.
        
        Args:
            audio: Audio array
            threshold_db: Silence threshold in dB
            
        Returns:
            Trimmed audio array
        """
        return librosa.effects.trim(audio, top_db=abs(threshold_db))[0]
    
    def convert_format(self, input_path: str, output_path: str, format: str = 'wav'):
        """
        Convert audio file format.
        
        Args:
            input_path: Input file path
            output_path: Output file path
            format: Target format
        """
        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format=format)
    
    def get_audio_info(self, file_path: str) -> dict:
        """
        Get basic information about an audio file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary with audio information
        """
        audio = AudioSegment.from_file(file_path)
        
        return {
            'duration': len(audio) / 1000.0,  # Duration in seconds
            'sample_rate': audio.frame_rate,
            'channels': audio.channels,
            'bit_depth': audio.sample_width * 8,
            'format': audio.format
        } 