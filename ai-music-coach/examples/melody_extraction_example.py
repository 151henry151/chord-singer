#!/usr/bin/env python3
"""
Example script demonstrating the MelodyExtractor functionality.
"""

import sys
import os
import numpy as np
from pydub import AudioSegment

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from audio_processing.melody_extraction import MelodyExtractor


def create_test_audio(output_path: str, duration_ms: int = 5000):
    """
    Create a test audio file with a simple melody for demonstration.
    
    Args:
        output_path: Path to save the test audio file
        duration_ms: Duration of the audio in milliseconds
    """
    print(f"Creating test audio file: {output_path}")
    
    # Generate a simple melody (C major scale: C, D, E, F, G, A, B, C)
    sample_rate = 22050
    duration_seconds = duration_ms / 1000.0
    
    # Define note frequencies (C4 to C5)
    note_frequencies = [
        261.63,  # C4
        293.66,  # D4
        329.63,  # E4
        349.23,  # F4
        392.00,  # G4
        440.00,  # A4
        493.88,  # B4
        523.25   # C5
    ]
    
    # Calculate samples per note
    samples_per_note = int(sample_rate * duration_seconds / len(note_frequencies))
    total_samples = samples_per_note * len(note_frequencies)
    
    # Create audio data
    audio_data = np.zeros(total_samples)
    
    for i, freq in enumerate(note_frequencies):
        start_sample = i * samples_per_note
        end_sample = start_sample + samples_per_note
        
        # Create time array for this note
        t = np.linspace(0, samples_per_note / sample_rate, samples_per_note, False)
        
        # Generate sine wave for this note
        note_audio = np.sin(2 * np.pi * freq * t)
        
        # Apply simple envelope to avoid clicks
        envelope = np.ones(samples_per_note)
        fade_samples = int(0.01 * sample_rate)  # 10ms fade
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        
        note_audio = note_audio * envelope
        
        audio_data[start_sample:end_sample] = note_audio
    
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
    """Main function to demonstrate melody extraction."""
    print("=== MelodyExtractor Example ===\n")
    
    # Create test audio file
    test_audio_path = "test_melody.wav"
    create_test_audio(test_audio_path)
    
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
    
    # Get melody segments
    print("Analyzing melody segments...")
    segments = extractor.get_melody_segments(melody_data, min_segment_duration=0.1)
    print(f"Found {len(segments)} melody segments")
    
    for i, segment in enumerate(segments[:3]):  # Show first 3 segments
        if segment:
            start_time = segment[0][0]
            end_time = segment[-1][0]
            duration = end_time - start_time
            avg_freq = np.mean([freq for _, freq in segment])
            print(f"  Segment {i+1}: {start_time:.3f}s - {end_time:.3f}s "
                  f"(duration: {duration:.3f}s, avg freq: {avg_freq:.1f} Hz)")
    print()
    
    # Test with different parameters
    print("Testing with custom parameters...")
    custom_extractor = MelodyExtractor(
        fmin=200.0,  # Higher minimum frequency
        fmax=800.0,  # Lower maximum frequency
        sr=44100,    # Higher sample rate
        frame_length=1024,
        hop_length=256
    )
    
    custom_melody_data = custom_extractor.extract_melody(test_audio_path)
    print(f"Custom extractor found {len(custom_melody_data)} frames")
    
    if custom_melody_data:
        custom_stats = custom_extractor.get_melody_statistics(custom_melody_data)
        print(f"Custom extractor frequency range: {custom_stats['min_frequency']:.1f} - {custom_stats['max_frequency']:.1f} Hz")
    
    print("\n=== Example completed successfully ===")
    
    # Clean up
    if os.path.exists(test_audio_path):
        os.remove(test_audio_path)
        print(f"Cleaned up test file: {test_audio_path}")


if __name__ == "__main__":
    main() 