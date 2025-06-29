"""
Basic tests for AI Music Coach.
"""

import pytest
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from audio_processing.chord_detection import ChordDetector
from audio_processing.audio_utils import AudioProcessor
from synthesis.vocal_synthesis import VocalSynthesizer
from utils.config import get_config


def test_config_loading():
    """Test that configuration can be loaded."""
    config = get_config()
    assert 'api_host' in config
    assert 'api_port' in config
    assert 'audio_sample_rate' in config


def test_chord_detector_initialization():
    """Test that ChordDetector can be initialized."""
    detector = ChordDetector()
    assert detector is not None
    assert hasattr(detector, 'chord_names')
    assert len(detector.chord_names) > 0


def test_audio_processor_initialization():
    """Test that AudioProcessor can be initialized."""
    processor = AudioProcessor()
    assert processor is not None
    assert processor.target_sr == 22050


def test_vocal_synthesizer_initialization():
    """Test that VocalSynthesizer can be initialized."""
    synthesizer = VocalSynthesizer()
    assert synthesizer is not None
    assert synthesizer.language == 'en'


def test_chord_names_format():
    """Test that chord names are in the expected format."""
    detector = ChordDetector()
    for chord_name in detector.chord_names:
        # Basic validation: chord names should be strings
        assert isinstance(chord_name, str)
        assert len(chord_name) > 0


if __name__ == "__main__":
    pytest.main([__file__]) 