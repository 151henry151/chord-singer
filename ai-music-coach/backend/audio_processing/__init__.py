"""
Audio processing module for chord detection, melody extraction, and source separation.
"""

from .chord_detection import ChordDetector
from .melody_extraction import MelodyExtractor
from .audio_utils import AudioProcessor, preprocess_audio

__all__ = ['ChordDetector', 'MelodyExtractor', 'AudioProcessor', 'preprocess_audio'] 