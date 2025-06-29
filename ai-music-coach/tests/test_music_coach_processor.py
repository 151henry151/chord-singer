"""
Tests for the MusicCoachProcessor class.
"""

import pytest
import sys
import os
import tempfile
import numpy as np
from pydub import AudioSegment

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import MusicCoachProcessor


class TestMusicCoachProcessor:
    """Test cases for the MusicCoachProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = MusicCoachProcessor()
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_audio(self, filename: str, duration_ms: int = 5000) -> str:
        """Create a test audio file."""
        # Generate a simple chord progression (C major, A minor, F major, G major)
        sample_rate = 44100
        duration_seconds = duration_ms / 1000.0
        samples = int(sample_rate * duration_seconds)
        
        # Create a simple chord progression
        t = np.linspace(0, duration_seconds, samples, False)
        
        # C major chord (C, E, G)
        c_major = (np.sin(2 * np.pi * 261.63 * t) +  # C4
                   np.sin(2 * np.pi * 329.63 * t) +  # E4
                   np.sin(2 * np.pi * 392.00 * t))   # G4
        
        # A minor chord (A, C, E)
        a_minor = (np.sin(2 * np.pi * 220.00 * t) +  # A3
                   np.sin(2 * np.pi * 261.63 * t) +  # C4
                   np.sin(2 * np.pi * 329.63 * t))   # E4
        
        # F major chord (F, A, C)
        f_major = (np.sin(2 * np.pi * 174.61 * t) +  # F3
                   np.sin(2 * np.pi * 220.00 * t) +  # A3
                   np.sin(2 * np.pi * 261.63 * t))   # C4
        
        # G major chord (G, B, D)
        g_major = (np.sin(2 * np.pi * 196.00 * t) +  # G3
                   np.sin(2 * np.pi * 246.94 * t) +  # B3
                   np.sin(2 * np.pi * 293.66 * t))   # D4
        
        # Combine chords in a progression
        chord_duration = duration_seconds / 4
        samples_per_chord = int(samples / 4)
        
        audio_data = np.concatenate([
            c_major[:samples_per_chord],
            a_minor[:samples_per_chord],
            f_major[:samples_per_chord],
            g_major[:samples_per_chord]
        ])
        
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
        """Test that MusicCoachProcessor initializes correctly."""
        assert self.processor is not None
        assert hasattr(self.processor, 'chord_detector')
        assert hasattr(self.processor, 'vocal_synthesizer')
    
    def test_process_song_basic(self):
        """Test basic song processing functionality."""
        # Create test audio file
        input_path = self.create_test_audio("test_song.wav", duration_ms=4000)
        output_path = os.path.join(self.temp_dir, "output.wav")
        
        # Process the song
        result = self.processor.process_song(input_path, output_path)
        
        # Verify results
        assert isinstance(result, dict)
        assert 'detected_chords' in result
        assert 'audio_duration' in result
        assert 'output_file_path' in result
        assert 'chord_count' in result
        
        # Check that output file was created
        assert os.path.exists(result['output_file_path'])
        
        # Check that we have some detected chords
        assert result['chord_count'] > 0
        assert len(result['detected_chords']) > 0
        
        # Check audio duration
        assert result['audio_duration'] > 0
        
        # Verify output audio file
        output_audio = AudioSegment.from_wav(result['output_file_path'])
        assert len(output_audio) > 0
    
    def test_process_song_error_handling(self):
        """Test error handling for invalid input."""
        # Test with non-existent file
        with pytest.raises(Exception):
            self.processor.process_song("nonexistent_file.wav", "output.wav")
    
    def test_chord_detection_integration(self):
        """Test that chord detection is working."""
        input_path = self.create_test_audio("chord_test.wav", duration_ms=2000)
        output_path = os.path.join(self.temp_dir, "chord_output.wav")
        
        result = self.processor.process_song(input_path, output_path)
        
        # Check that chords were detected
        detected_chords = result['detected_chords']
        assert len(detected_chords) > 0
        
        # Check chord format
        for chord_name, start_time, end_time in detected_chords:
            assert isinstance(chord_name, str)
            assert isinstance(start_time, float)
            assert isinstance(end_time, float)
            assert start_time >= 0
            assert end_time > start_time
    
    def test_vocal_synthesis_integration(self):
        """Test that vocal synthesis is working."""
        input_path = self.create_test_audio("vocal_test.wav", duration_ms=3000)
        output_path = os.path.join(self.temp_dir, "vocal_output.wav")
        
        result = self.processor.process_song(input_path, output_path)
        
        # Check that output file was created and has content
        output_audio = AudioSegment.from_wav(result['output_file_path'])
        assert len(output_audio) > 0
        
        # Check that output duration matches input duration
        expected_duration_ms = int(result['audio_duration'] * 1000)
        assert len(output_audio) == expected_duration_ms


if __name__ == "__main__":
    pytest.main([__file__]) 