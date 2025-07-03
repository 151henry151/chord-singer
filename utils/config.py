"""
Configuration management utilities.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_config() -> Dict[str, Any]:
    """
    Get application configuration from environment variables.
    
    Returns:
        Dictionary containing configuration values
    """
    return {
        # API Configuration
        'api_host': os.getenv('API_HOST', '0.0.0.0'),
        'api_port': int(os.getenv('API_PORT', 8000)),
        'debug': os.getenv('DEBUG', 'True').lower() == 'true',
        
        # Frontend Configuration
        'frontend_url': os.getenv('FRONTEND_URL', 'http://localhost:3000'),
        
        # Audio Processing Configuration
        'audio_sample_rate': int(os.getenv('AUDIO_SAMPLE_RATE', 22050)),
        'audio_chunk_size': int(os.getenv('AUDIO_CHUNK_SIZE', 1024)),
        
        # Model Configuration
        'model_path': os.getenv('MODEL_PATH', './ml_models/'),
        'chord_detection_model': os.getenv('CHORD_DETECTION_MODEL', 'chord_detection_model.h5'),
        
        # File Upload Configuration
        'upload_dir': os.getenv('UPLOAD_DIR', './uploads/'),
        'max_file_size': os.getenv('MAX_FILE_SIZE', '50MB'),
        'allowed_audio_formats': os.getenv('ALLOWED_AUDIO_FORMATS', 'mp3,wav,flac,m4a').split(','),
        
        # Text-to-Speech Configuration
        'tts_engine': os.getenv('TTS_ENGINE', 'coqui-tts'),
        'tts_language': os.getenv('TTS_LANGUAGE', 'en'),
        
        # Development Configuration
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    }


def get_audio_config() -> Dict[str, Any]:
    """
    Get audio-specific configuration.
    
    Returns:
        Dictionary containing audio configuration values
    """
    config = get_config()
    return {
        'sample_rate': config['audio_sample_rate'],
        'chunk_size': config['audio_chunk_size'],
        'allowed_formats': config['allowed_audio_formats'],
        'max_file_size': config['max_file_size']
    }


def get_api_config() -> Dict[str, Any]:
    """
    Get API-specific configuration.
    
    Returns:
        Dictionary containing API configuration values
    """
    config = get_config()
    return {
        'host': config['api_host'],
        'port': config['api_port'],
        'debug': config['debug'],
        'frontend_url': config['frontend_url']
    }
