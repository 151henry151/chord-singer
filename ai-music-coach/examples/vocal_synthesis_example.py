"""
Example script demonstrating the VocalSynthesizer class for spoken chord vocals.
"""

import sys
import os
import tempfile

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from synthesis.vocal_synthesis import VocalSynthesizer


def main():
    """Demonstrate the VocalSynthesizer functionality."""
    
    print("AI Music Coach - Vocal Synthesis Example")
    print("=" * 50)
    
    # Initialize the synthesizer
    print("\n1. Initializing VocalSynthesizer...")
    synthesizer = VocalSynthesizer(voice_rate=150, voice_volume=0.9)
    
    # Show available voices
    print("\n2. Available voices:")
    voices = synthesizer.get_available_voices()
    for i, voice in enumerate(voices):
        print(f"  {i+1}. {voice['name']} (ID: {voice['id']})")
    
    # Create a sample chord timeline
    print("\n3. Creating sample chord timeline...")
    chord_timeline = [
        ("C major", 0.0, 2.0),
        ("A minor", 2.0, 4.0),
        ("F major", 4.0, 6.0),
        ("G major", 6.0, 8.0),
        ("C major", 8.0, 10.0)
    ]
    
    print("Chord timeline:")
    for chord_name, start_time, end_time in chord_timeline:
        print(f"  {start_time:.1f}s - {end_time:.1f}s: {chord_name}")
    
    # Synthesize spoken chord vocals
    print("\n4. Synthesizing spoken chord vocals...")
    original_duration = 10.0  # 10 seconds
    
    # Create temporary output file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        output_path = temp_file.name
    
    try:
        result_path = synthesizer.synthesize_spoken_chord_vocals(
            chord_timeline, original_duration, output_path
        )
        
        print(f"✓ Successfully generated spoken chord vocals!")
        print(f"  Output file: {result_path}")
        print(f"  Duration: {original_duration} seconds")
        
        # Show file size
        file_size = os.path.getsize(result_path) / 1024  # KB
        print(f"  File size: {file_size:.1f} KB")
        
    except Exception as e:
        print(f"✗ Error generating vocals: {e}")
    
    finally:
        # Clean up
        synthesizer.cleanup()
        if os.path.exists(output_path):
            os.unlink(output_path)
    
    print("\n5. Usage example:")
    print("""
# Basic usage
synthesizer = VocalSynthesizer()
chord_timeline = [("C major", 0.0, 2.0), ("A minor", 2.0, 4.0)]
output_path = synthesizer.synthesize_spoken_chord_vocals(
    chord_timeline, 4.0, "output.wav"
)

# Customize voice properties
synthesizer.set_voice_properties(rate=200, volume=0.8)

# Get available voices
voices = synthesizer.get_available_voices()
for voice in voices:
    print(f"{voice['name']}: {voice['id']}")
    """)
    
    print("\n" + "=" * 50)
    print("Vocal synthesis example completed!")


if __name__ == "__main__":
    main() 