"""
Tests for the VocalSynthesizer class.
"""

import pytest
import sys
import os
import tempfile
from pydub import AudioSegment

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from synthesis.vocal_synthesis import VocalSynthesizer


class TestVocalSynthesizer:
    """Test cases for the VocalSynthesizer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.synthesizer = VocalSynthesizer()
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test fixtures."""
        self.synthesizer.cleanup()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test that VocalSynthesizer initializes correctly."""
        assert self.synthesizer is not None
        assert hasattr(self.synthesizer, 'engine')
    
    def test_synthesize_single_chord(self):
        """Test synthesizing a single chord name."""
        chord_audio = self.synthesizer._synthesize_single_chord("C major")
        
        assert isinstance(chord_audio, AudioSegment)
        assert len(chord_audio) > 0  # Should have some audio content
    
    def test_adjust_audio_duration_trim(self):
        """Test adjusting audio duration by trimming."""
        # Create a test audio segment (2 seconds)
        test_audio = AudioSegment.silent(duration=2000)
        
        # Trim to 1 second
        adjusted = self.synthesizer._adjust_audio_duration(test_audio, 1000)
        
        assert len(adjusted) == 1000
    
    def test_adjust_audio_duration_pad(self):
        """Test adjusting audio duration by padding."""
        # Create a test audio segment (1 second)
        test_audio = AudioSegment.silent(duration=1000)
        
        # Pad to 3 seconds
        adjusted = self.synthesizer._adjust_audio_duration(test_audio, 3000)
        
        assert len(adjusted) == 3000
    
    def test_adjust_audio_duration_no_change(self):
        """Test adjusting audio duration when no change is needed."""
        # Create a test audio segment (2 seconds)
        test_audio = AudioSegment.silent(duration=2000)
        
        # No change needed
        adjusted = self.synthesizer._adjust_audio_duration(test_audio, 2000)
        
        assert len(adjusted) == 2000
        assert adjusted == test_audio
    
    def test_synthesize_spoken_chord_vocals(self):
        """Test synthesizing spoken chord vocals for a timeline."""
        # Create a simple chord timeline
        chord_timeline = [
            ("C major", 0.0, 2.0),
            ("A minor", 2.0, 4.0),
            ("F major", 4.0, 6.0),
            ("G major", 6.0, 8.0)
        ]
        
        original_duration = 8.0
        output_path = os.path.join(self.temp_dir, "test_output.wav")
        
        # Synthesize the vocals
        result_path = self.synthesizer.synthesize_spoken_chord_vocals(
            chord_timeline, original_duration, output_path
        )
        
        # Verify the output
        assert os.path.exists(result_path)
        assert result_path == output_path
        
        # Check that the output audio has the correct duration
        output_audio = AudioSegment.from_wav(result_path)
        expected_duration_ms = int(original_duration * 1000)
        assert len(output_audio) == expected_duration_ms
    
    def test_get_available_voices(self):
        """Test getting available voices."""
        voices = self.synthesizer.get_available_voices()
        
        assert isinstance(voices, list)
        # Should have at least one voice available
        assert len(voices) > 0
        
        # Each voice should have id and name
        for voice in voices:
            assert 'id' in voice
            assert 'name' in voice
    
    def test_set_voice_properties(self):
        """Test setting voice properties."""
        # Test setting rate
        self.synthesizer.set_voice_properties(rate=200)
        
        # Test setting volume
        self.synthesizer.set_voice_properties(volume=0.8)
        
        # Test setting voice (if we have available voices)
        voices = self.synthesizer.get_available_voices()
        if voices:
            voice_id = voices[0]['id']
            self.synthesizer.set_voice_properties(voice_id=voice_id)
    
    def test_error_handling_invalid_chord(self):
        """Test error handling for invalid chord names."""
        # This should not raise an exception, but return silence
        chord_audio = self.synthesizer._synthesize_single_chord("")
        
        assert isinstance(chord_audio, AudioSegment)
        assert len(chord_audio) > 0  # Should return silence, not empty audio


if __name__ == "__main__":
    pytest.main([__file__]) 