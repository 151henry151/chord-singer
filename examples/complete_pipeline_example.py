"""
Example script demonstrating the complete AI Music Coach pipeline.
"""

import sys
import os
import tempfile
import requests

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import MusicCoachProcessor


def main():
    """Demonstrate the complete AI Music Coach pipeline."""
    
    print("AI Music Coach - Complete Pipeline Example")
    print("=" * 50)
    
    # Initialize the processor
    print("\n1. Initializing MusicCoachProcessor...")
    processor = MusicCoachProcessor()
    
    # Create a simple test audio file
    print("\n2. Creating test audio file...")
    test_audio_path = create_test_audio()
    
    # Process the song
    print("\n3. Processing song through the pipeline...")
    output_path = tempfile.mktemp(suffix=".wav")
    
    try:
        result = processor.process_song(test_audio_path, output_path)
        
        print("✓ Song processing completed successfully!")
        print(f"  Input file: {test_audio_path}")
        print(f"  Output file: {result['output_file_path']}")
        print(f"  Audio duration: {result['audio_duration']:.2f} seconds")
        print(f"  Chords detected: {result['chord_count']}")
        
        # Display detected chords
        print("\n4. Detected chord progression:")
        for i, (chord_name, start_time, end_time) in enumerate(result['detected_chords']):
            print(f"  {i+1}. {start_time:.1f}s - {end_time:.1f}s: {chord_name}")
        
        # File information
        input_size = os.path.getsize(test_audio_path) / 1024  # KB
        output_size = os.path.getsize(result['output_file_path']) / 1024  # KB
        
        print(f"\n5. File information:")
        print(f"  Input size: {input_size:.1f} KB")
        print(f"  Output size: {output_size:.1f} KB")
        
        print(f"\n6. Output file ready: {result['output_file_path']}")
        print("   You can now play this file to hear the spoken chord vocals!")
        
    except Exception as e:
        print(f"✗ Error processing song: {e}")
    
    finally:
        # Clean up test files
        if os.path.exists(test_audio_path):
            os.unlink(test_audio_path)
    
    print("\n" + "=" * 50)
    print("Complete pipeline example finished!")


def create_test_audio():
    """Create a simple test audio file with a chord progression."""
    import numpy as np
    from pydub import AudioSegment
    
    # Create a simple chord progression (C major, A minor, F major, G major)
    sample_rate = 44100
    duration_seconds = 8.0
    samples = int(sample_rate * duration_seconds)
    
    # Create time array
    t = np.linspace(0, duration_seconds, samples, False)
    
    # Define chord frequencies
    chords = [
        # C major (C, E, G)
        [261.63, 329.63, 392.00],
        # A minor (A, C, E)
        [220.00, 261.63, 329.63],
        # F major (F, A, C)
        [174.61, 220.00, 261.63],
        # G major (G, B, D)
        [196.00, 246.94, 293.66]
    ]
    
    # Create audio data
    audio_data = np.zeros(samples)
    chord_duration = duration_seconds / len(chords)
    samples_per_chord = int(samples / len(chords))
    
    for i, chord_freqs in enumerate(chords):
        start_sample = i * samples_per_chord
        end_sample = start_sample + samples_per_chord
        
        # Create chord by summing sine waves
        chord_audio = np.zeros(samples_per_chord)
        for freq in chord_freqs:
            chord_audio += np.sin(2 * np.pi * freq * np.linspace(0, chord_duration, samples_per_chord, False))
        
        audio_data[start_sample:end_sample] = chord_audio
    
    # Normalize and convert to 16-bit PCM
    audio_data = audio_data / np.max(np.abs(audio_data))
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Create AudioSegment
    audio = AudioSegment(audio_data.tobytes(), frame_rate=sample_rate, 
                        sample_width=2, channels=1)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    temp_path = temp_file.name
    temp_file.close()
    
    audio.export(temp_path, format='wav')
    
    return temp_path


def test_api_endpoint():
    """Test the API endpoint (if server is running)."""
    print("\n7. Testing API endpoint...")
    
    # Create test audio file
    test_audio_path = create_test_audio()
    
    try:
        # Upload file to API
        with open(test_audio_path, 'rb') as f:
            files = {'file': ('test_song.wav', f, 'audio/wav')}
            response = requests.post('http://localhost:8000/process-song/', files=files)
        
        if response.status_code == 200:
            print("✓ API endpoint test successful!")
            
            # Save response to file
            output_path = "api_test_output.wav"
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"  API output saved to: {output_path}")
        else:
            print(f"✗ API endpoint test failed: {response.status_code}")
            print(f"  Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to API server. Is it running?")
    except Exception as e:
        print(f"✗ API test error: {e}")
    
    finally:
        # Clean up
        if os.path.exists(test_audio_path):
            os.unlink(test_audio_path)


if __name__ == "__main__":
    main()
    
    # Uncomment the line below to test the API endpoint
    # test_api_endpoint() 