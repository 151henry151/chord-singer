"""
Tests for the MelodyExtractor class.
"""

import pytest
import sys
import os
import tempfile
import numpy as np
from pydub import AudioSegment

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from audio_processing.melody_extraction import MelodyExtractor


class TestMelodyExtractor:
    """Test cases for the MelodyExtractor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = MelodyExtractor()
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_audio(self, filename: str, duration_ms: int = 3000, 
                         frequency: float = 440.0) -> str:
        """Create a test audio file with a single tone."""
        # Generate a simple sine wave
        sample_rate = 22050
        duration_seconds = duration_ms / 1000.0
        samples = int(sample_rate * duration_seconds)
        
        # Create time array
        t = np.linspace(0, duration_seconds, samples, False)
        
        # Generate sine wave
        audio_data = np.sin(2 * np.pi * frequency * t)
        
        # Normalize and convert to 16-bit PCM
        audio_data = audio_data / np.max(np.abs(audio_data))
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # Create AudioSegment
        audio = AudioSegment(audio_data.tobytes(), frame_rate=sample_rate, 
                           sample_width=2, channels=1)
        
        # Save to file
        file_path = os.path.join(self.temp_dir, filename)
        audio.export(file_path, format='wav')
        
        return file_path
    
    def test_initialization(self):
        """Test that MelodyExtractor initializes correctly."""
        extractor = MelodyExtractor()
        assert extractor is not None
        assert extractor.fmin == pytest.approx(65.41, abs=1)  # C2
        assert extractor.fmax == pytest.approx(2093.00, abs=10)  # C7
        assert extractor.sr == 22050
    
    def test_extract_melody_single_tone(self):
        """Test melody extraction from a single tone."""
        # Create test audio with A4 (440 Hz)
        test_file = self.create_test_audio("test_tone.wav", duration_ms=2000, frequency=440.0)
        
        # Extract melody
        melody_data = self.extractor.extract_melody(test_file)
        
        # Verify results
        assert len(melody_data) > 0
        
        # Check that frequencies are around 440 Hz
        frequencies = [freq for _, freq in melody_data]
        mean_freq = np.mean(frequencies)
        assert 400 <= mean_freq <= 480  # Allow some tolerance
    
    def test_get_melody_notes(self):
        """Test conversion of frequencies to note names."""
        # Create test data
        test_data = [
            (0.0, 261.63),  # C4
            (0.5, 293.66),  # D4
            (1.0, 329.63),  # E4
            (1.5, 349.23),  # F4
        ]
        
        notes = self.extractor.get_melody_notes(test_data)
        
        # Verify results
        assert len(notes) == 4
        assert notes[0][1] == 'C4'
        assert notes[1][1] == 'D4'
        assert notes[2][1] == 'E4'
        assert notes[3][1] == 'F4'
    
    def test_get_melody_statistics(self):
        """Test melody statistics calculation."""
        # Create test data
        test_data = [
            (0.0, 261.63),
            (0.5, 293.66),
            (1.0, 329.63),
            (1.5, 349.23),
        ]
        
        stats = self.extractor.get_melody_statistics(test_data)
        
        # Verify results
        assert stats['total_frames'] == 4
        assert stats['voiced_frames'] == 4
        assert stats['min_frequency'] == pytest.approx(261.63, abs=0.1)
        assert stats['max_frequency'] == pytest.approx(349.23, abs=0.1)
    
    def test_error_handling_invalid_file(self):
        """Test error handling for invalid file."""
        melody_data = self.extractor.extract_melody("nonexistent_file.wav")
        assert melody_data == []


if __name__ == "__main__":
    pytest.main([__file__])
