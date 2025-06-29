"""
Tests for audio utilities, specifically the preprocess_audio function.
"""

import pytest
import sys
import os
import tempfile
from pydub import AudioSegment
import numpy as np

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from audio_processing.audio_utils import preprocess_audio, AudioProcessor


class TestPreprocessAudio:
    """Test cases for the preprocess_audio function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test fixtures."""
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_audio(self, filename: str, duration_ms: int = 1000, 
                         channels: int = 2, frame_rate: int = 22050) -> str:
        """Create a test audio file."""
        # Generate a simple sine wave
        sample_rate = frame_rate
        duration_seconds = duration_ms / 1000.0
        samples = int(sample_rate * duration_seconds)
        
        # Create a simple tone
        frequency = 440  # A4 note
        t = np.linspace(0, duration_seconds, samples, False)
        tone = np.sin(2 * np.pi * frequency * t)
        
        # Convert to 16-bit PCM
        audio_data = (tone * 32767).astype(np.int16)
        
        # Create AudioSegment
        if channels == 1:
            audio = AudioSegment(audio_data.tobytes(), frame_rate=frame_rate, 
                               sample_width=2, channels=1)
        else:
            # For stereo, duplicate the mono channel
            audio = AudioSegment(audio_data.tobytes(), frame_rate=frame_rate, 
                               sample_width=2, channels=1)
            audio = audio.set_channels(2)
        
        # Save to file
        file_path = os.path.join(self.temp_dir, filename)
        audio.export(file_path, format=os.path.splitext(filename)[1][1:])
        
        return file_path
    
    def test_preprocess_audio_success(self):
        """Test successful audio preprocessing."""
        # Create test audio file
        test_file = self.create_test_audio("test.wav", duration_ms=2000, channels=2, frame_rate=22050)
        
        # Preprocess the audio
        processed_path, duration = preprocess_audio(test_file)
        
        # Verify results
        assert os.path.exists(processed_path)
        assert duration == 2.0  # 2000ms = 2.0 seconds
        
        # Check that the processed file is in the correct format
        processed_audio = AudioSegment.from_file(processed_path)
        assert processed_audio.channels == 1  # Should be mono
        assert processed_audio.frame_rate == 44100  # Should be 44.1kHz
        
        # Clean up
        os.unlink(processed_path)
    
    def test_preprocess_audio_file_not_found(self):
        """Test error handling for non-existent file."""
        with pytest.raises(FileNotFoundError):
            preprocess_audio("nonexistent_file.wav")
    
    def test_preprocess_audio_unsupported_format(self):
        """Test error handling for unsupported file format."""
        # Create a file with unsupported extension
        unsupported_file = os.path.join(self.temp_dir, "test.xyz")
        with open(unsupported_file, 'w') as f:
            f.write("dummy content")
        
        with pytest.raises(ValueError) as exc_info:
            preprocess_audio(unsupported_file)
        
        assert "Unsupported file format" in str(exc_info.value)
    
    def test_preprocess_audio_already_mono(self):
        """Test preprocessing of already mono audio."""
        test_file = self.create_test_audio("test_mono.wav", duration_ms=1000, channels=1, frame_rate=44100)
        
        processed_path, duration = preprocess_audio(test_file)
        
        # Verify results
        assert os.path.exists(processed_path)
        assert duration == 1.0
        
        processed_audio = AudioSegment.from_file(processed_path)
        assert processed_audio.channels == 1
        assert processed_audio.frame_rate == 44100
        
        # Clean up
        os.unlink(processed_path)
    
    def test_preprocess_audio_already_correct_sample_rate(self):
        """Test preprocessing of audio already at 44.1kHz."""
        test_file = self.create_test_audio("test_44k.wav", duration_ms=1500, channels=2, frame_rate=44100)
        
        processed_path, duration = preprocess_audio(test_file)
        
        # Verify results
        assert os.path.exists(processed_path)
        assert duration == 1.5
        
        processed_audio = AudioSegment.from_file(processed_path)
        assert processed_audio.channels == 1
        assert processed_audio.frame_rate == 44100
        
        # Clean up
        os.unlink(processed_path)
    
    def test_audio_processor_class_method(self):
        """Test the AudioProcessor class method."""
        processor = AudioProcessor()
        test_file = self.create_test_audio("test_class.wav", duration_ms=1000, channels=2, frame_rate=22050)
        
        processed_path, duration = processor.preprocess_audio(test_file)
        
        # Verify results
        assert os.path.exists(processed_path)
        assert duration == 1.0
        
        processed_audio = AudioSegment.from_file(processed_path)
        assert processed_audio.channels == 1
        assert processed_audio.frame_rate == 44100
        
        # Clean up
        os.unlink(processed_path)


if __name__ == "__main__":
    pytest.main([__file__]) 