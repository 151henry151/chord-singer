"""
Example script demonstrating the preprocess_audio function.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from audio_processing.audio_utils import preprocess_audio, AudioProcessor


def main():
    """Demonstrate the preprocess_audio function."""
    
    print("AI Music Coach - Audio Preprocessing Example")
    print("=" * 50)
    
    # Example 1: Using the standalone function
    print("\n1. Using standalone preprocess_audio function:")
    
    # Note: In a real scenario, you would provide an actual audio file path
    # For this example, we'll show the function signature and usage pattern
    
    try:
        # This would be the actual usage:
        # processed_path, duration = preprocess_audio("path/to/your/audio.mp3")
        # print(f"Processed file: {processed_path}")
        # print(f"Duration: {duration:.2f} seconds")
        
        print("Function signature: preprocess_audio(audio_path: str) -> Tuple[str, float]")
        print("Returns: (processed_file_path, duration_in_seconds)")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Using the AudioProcessor class
    print("\n2. Using AudioProcessor class:")
    
    try:
        processor = AudioProcessor()
        print("Created AudioProcessor instance")
        
        # This would be the actual usage:
        # processed_path, duration = processor.preprocess_audio("path/to/your/audio.wav")
        # print(f"Processed file: {processed_path}")
        # print(f"Duration: {duration:.2f} seconds")
        
        print("Method: processor.preprocess_audio(audio_path: str) -> Tuple[str, float]")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Supported file formats
    print("\n3. Supported audio formats:")
    supported_formats = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.wma']
    for fmt in supported_formats:
        print(f"  - {fmt}")
    
    # Example 4: What the function does
    print("\n4. What preprocess_audio does:")
    print("  - Loads audio using pydub.AudioSegment.from_file")
    print("  - Converts to mono channel (if stereo)")
    print("  - Converts to 44.1kHz sample rate (if different)")
    print("  - Saves to temporary WAV file")
    print("  - Returns file path and duration")
    
    # Example 5: Error handling
    print("\n5. Error handling:")
    print("  - FileNotFoundError: If audio file doesn't exist")
    print("  - ValueError: If file format is not supported")
    print("  - Exception: For other audio processing errors")
    
    print("\n" + "=" * 50)
    print("Ready to preprocess your audio files!")


if __name__ == "__main__":
    main() 