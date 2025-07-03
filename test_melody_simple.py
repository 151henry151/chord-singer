#!/usr/bin/env python3
"""
Simple test script for MelodyExtractor.
"""

import sys
import os
import numpy as np
from pydub import AudioSegment

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import directly from the module file to avoid dependency issues
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'audio_processing'))
from melody_extraction import MelodyExtractor


def create_test_audio(output_path: str, duration_ms: int = 3000, frequency: float = 440.0):
    """Create a test audio file with a single tone."""
    print(f"Creating test audio file: {output_path}")
    
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
    audio.export(output_path, format='wav')
    print(f"Test audio created successfully: {output_path}")


def main():
    """Test the MelodyExtractor functionality."""
    print("=== Simple MelodyExtractor Test ===\n")
    
    # Create test audio file
    test_audio_path = "test_tone.wav"
    create_test_audio(test_audio_path, duration_ms=2000, frequency=440.0)
    
    # Initialize MelodyExtractor
    print("Initializing MelodyExtractor...")
    extractor = MelodyExtractor()
    print(f"Frequency range: {extractor.fmin:.1f} Hz - {extractor.fmax:.1f} Hz")
    print(f"Sample rate: {extractor.sr} Hz")
    print()
    
    # Extract melody from audio file
    print("Extracting melody from audio file...")
    melody_data = extractor.extract_melody(test_audio_path)
    
    if not melody_data:
        print("No melody data extracted. Check if the audio file is valid.")
        return
    
    print(f"Extracted {len(melody_data)} melody frames")
    print()
    
    # Display first few melody frames
    print("First 10 melody frames (timestamp, frequency):")
    for i, (timestamp, freq) in enumerate(melody_data[:10]):
        print(f"  {timestamp:.3f}s: {freq:.1f} Hz")
    print()
    
    # Convert to note names
    print("Converting frequencies to note names...")
    notes = extractor.get_melody_notes(melody_data)
    
    print("First 10 notes (timestamp, note):")
    for i, (timestamp, note) in enumerate(notes[:10]):
        print(f"  {timestamp:.3f}s: {note}")
    print()
    
    # Get melody statistics
    print("Melody statistics:")
    stats = extractor.get_melody_statistics(melody_data)
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    print()
    
    # Test with audio array
    print("Testing with audio array...")
    import librosa
    audio, sr = librosa.load(test_audio_path, sr=None)
    array_melody_data = extractor.extract_melody_from_array(audio, sr)
    print(f"Array extraction found {len(array_melody_data)} frames")
    
    print("\n=== Test completed successfully ===")
    
    # Clean up
    if os.path.exists(test_audio_path):
        os.remove(test_audio_path)
        print(f"Cleaned up test file: {test_audio_path}")


if __name__ == "__main__":
    main() 