"""
Example script demonstrating the AdvancedVocalSynthesizer class with Coqui TTS.
Shows advanced vocal synthesis with singing enhancements.
"""

import sys
import os
import tempfile
import asyncio

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from synthesis.advanced_vocal_synthesis import AdvancedVocalSynthesizer, synthesize_sung_chord_vocals_sync


async def test_coqui_tts():
    """Test Coqui TTS synthesis with singing enhancements."""
    print("\n🎵 Testing Coqui TTS (Advanced Neural TTS)")
    print("=" * 60)
    
    synthesizer = AdvancedVocalSynthesizer(
        model_name="tts_models/en/ljspeech/tacotron2-DDC",
        vocoder_name="vocoder_models/en/ljspeech/hifigan_v2",
        rate=0.9,
        volume=0.9
    )
    
    # Test with a simple chord progression
    chord_timeline = [
        ("C major", 0.0, 2.0),
        ("A minor", 2.0, 4.0),
        ("F major", 4.0, 6.0),
        ("G major", 6.0, 8.0)
    ]
    
    # Create a simple melody contour (C major scale)
    melody_contour = [
        (0.0, 261.63),   # C4
        (0.5, 293.66),   # D4
        (1.0, 329.63),   # E4
        (1.5, 349.23),   # F4
        (2.0, 220.00),   # A3
        (2.5, 246.94),   # B3
        (3.0, 261.63),   # C4
        (3.5, 293.66),   # D4
        (4.0, 174.61),   # F3
        (4.5, 196.00),   # G3
        (5.0, 220.00),   # A3
        (5.5, 246.94),   # B3
        (6.0, 196.00),   # G3
        (6.5, 220.00),   # A3
        (7.0, 246.94),   # B3
        (7.5, 261.63),   # C4
    ]
    
    # Create a simple instrumental track (just silence for demo)
    instrumental_duration = 8.0
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        output_path = temp_file.name
    
    try:
        result_path = synthesizer.synthesize_sung_chord_vocals(
            chord_timeline, melody_contour, instrumental_duration,
            output_path, output_path  # Use same file for instrumental (silence)
        )
        
        print(f"✓ Successfully generated Coqui TTS vocals!")
        print(f"  Output file: {result_path}")
        print(f"  Duration: {instrumental_duration} seconds")
        
        # Show file size
        file_size = os.path.getsize(result_path) / 1024  # KB
        print(f"  File size: {file_size:.1f} KB")
        
    except Exception as e:
        print(f"✗ Error generating Coqui TTS vocals: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        synthesizer.cleanup()
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_stable_vocals():
    """Test stable vocals synthesis (no pitch mapping)."""
    print("\n🎵 Testing Stable Vocals (No Pitch Mapping)")
    print("=" * 60)
    
    synthesizer = AdvancedVocalSynthesizer(
        model_name="tts_models/en/ljspeech/tacotron2-DDC",
        vocoder_name="vocoder_models/en/ljspeech/hifigan_v2",
        rate=0.9,
        volume=0.9
    )
    
    # Test with a simple chord progression
    chord_timeline = [
        ("C major", 0.0, 2.0),
        ("A minor", 2.0, 4.0),
        ("F major", 4.0, 6.0),
        ("G major", 6.0, 8.0)
    ]
    
    # Create a simple instrumental track (just silence for demo)
    instrumental_duration = 8.0
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        output_path = temp_file.name
    
    try:
        result_path = synthesizer.synthesize_stable_chord_vocals(
            chord_timeline, instrumental_duration, 
            output_path, output_path  # Use same file for instrumental (silence)
        )
        
        print(f"✓ Successfully generated stable vocals!")
        print(f"  Output file: {result_path}")
        print(f"  Duration: {instrumental_duration} seconds")
        
        file_size = os.path.getsize(result_path) / 1024
        print(f"  File size: {file_size:.1f} KB")
        
    except Exception as e:
        print(f"✗ Error generating stable vocals: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        synthesizer.cleanup()
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_sync_wrapper():
    """Test the synchronous wrapper function."""
    print("\n🎵 Testing Synchronous Wrapper")
    print("=" * 60)
    
    chord_timeline = [
        ("C major", 0.0, 2.0),
        ("A minor", 2.0, 4.0),
        ("F major", 4.0, 6.0),
        ("G major", 6.0, 8.0)
    ]
    
    melody_contour = [
        (0.0, 261.63),   # C4
        (1.0, 329.63),   # E4
        (2.0, 220.00),   # A3
        (3.0, 261.63),   # C4
        (4.0, 174.61),   # F3
        (5.0, 220.00),   # A3
        (6.0, 196.00),   # G3
        (7.0, 261.63),   # C4
    ]
    
    instrumental_duration = 8.0
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        output_path = temp_file.name
    
    try:
        result_path = synthesize_sung_chord_vocals_sync(
            chord_timeline, melody_contour, instrumental_duration,
            output_path, output_path,
            model_name="tts_models/en/ljspeech/tacotron2-DDC",
            vocoder_name="vocoder_models/en/ljspeech/hifigan_v2"
        )
        
        print(f"✓ Successfully generated vocals using sync wrapper!")
        print(f"  Output file: {result_path}")
        print(f"  Duration: {instrumental_duration} seconds")
        
        file_size = os.path.getsize(result_path) / 1024
        print(f"  File size: {file_size:.1f} KB")
        
    except Exception as e:
        print(f"✗ Error generating vocals: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_available_voices():
    """Test getting available Coqui TTS voices."""
    print("\n🎵 Testing Available Coqui TTS Voices")
    print("=" * 60)
    
    try:
        synthesizer = AdvancedVocalSynthesizer()
        voices = synthesizer.get_available_voices()
        
        print(f"✓ Found {len(voices)} available Coqui TTS models")
        print("\nCoqui TTS Models (first 10):")
        for i, voice in enumerate(voices[:10]):
            print(f"  {i+1}. {voice['name']} (ID: {voice['id']})")
        
        if len(voices) > 10:
            print(f"  ... and {len(voices) - 10} more models")
        
    except Exception as e:
        print(f"  Error getting Coqui TTS voices: {e}")


async def main():
    """Run all tests."""
    print("🎵 Advanced Vocal Synthesis Example")
    print("=" * 60)
    print("This example demonstrates:")
    print("  • Coqui TTS integration")
    print("  • Spectral pitch shifting")
    print("  • Singing enhancements")
    print("  • Stable vocals for learning")
    print("  • Natural-sounding chord pronunciation")
    
    # Test Coqui TTS with pitch mapping
    await test_coqui_tts()
    
    # Test stable vocals (no pitch mapping)
    test_stable_vocals()
    
    # Test synchronous wrapper
    test_sync_wrapper()
    
    # Test available voices
    test_available_voices()
    
    print("\n🎵 Example completed!")
    print("All tests should have generated audio files with:")
    print("  • Natural-sounding vocals")
    print("  • Proper chord pronunciation")
    print("  • Musical enhancements")
    print("  • Perfect timing synchronization")


if __name__ == "__main__":
    asyncio.run(main()) 