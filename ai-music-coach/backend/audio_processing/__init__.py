"""
Audio processing module for chord detection, melody extraction, and audio utilities.
"""

# from .chord_detection import ChordDetector
from .melody_extraction import MelodyExtractor
from .audio_utils import preprocess_audio, AudioProcessor

__all__ = ['MelodyExtractor', 'preprocess_audio', 'AudioProcessor'] 