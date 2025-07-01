"""
Example script demonstrating the AdvancedVocalSynthesizer class.
Shows the difference between basic pyttsx3 and advanced TTS engines.
"""

import sys
import os
import tempfile
import asyncio

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from synthesis.advanced_vocal_synthesis import AdvancedVocalSynthesizer, synthesize_sung_chord_vocals_sync


async def test_edge_tts():
    """Test edge-tts synthesis."""
    print("\n🎵 Testing Edge-TTS (Microsoft's high-quality TTS)")
    print("=" * 60)
    
    synthesizer = AdvancedVocalSynthesizer(
        tts_engine="edge-tts",
        voice_name="en-US-JennyNeural",
        rate=0.8,  # Slightly slower for singing
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
        result_path = await synthesizer.synthesize_sung_chord_vocals(
            chord_timeline, melody_contour, instrumental_duration, 
            output_path, output_path  # Use same file for instrumental (silence)
        )
        
        print(f"✓ Successfully generated Edge-TTS vocals!")
        print(f"  Output file: {result_path}")
        print(f"  Duration: {instrumental_duration} seconds")
        
        # Show file size
        file_size = os.path.getsize(result_path) / 1024  # KB
        print(f"  File size: {file_size:.1f} KB")
        
    except Exception as e:
        print(f"✗ Error generating Edge-TTS vocals: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        synthesizer.cleanup()
        if os.path.exists(output_path):
            os.unlink(output_path)


async def test_gtts():
    """Test gTTS synthesis."""
    print("\n🎵 Testing gTTS (Google Text-to-Speech)")
    print("=" * 60)
    
    synthesizer = AdvancedVocalSynthesizer(
        tts_engine="gtts",
        rate=1.0,
        volume=0.9
    )
    
    # Test with a simple chord progression
    chord_timeline = [
        ("C major", 0.0, 2.0),
        ("A minor", 2.0, 4.0),
        ("F major", 4.0, 6.0),
        ("G major", 6.0, 8.0)
    ]
    
    # Simple melody contour
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
        result_path = await synthesizer.synthesize_sung_chord_vocals(
            chord_timeline, melody_contour, instrumental_duration, 
            output_path, output_path
        )
        
        print(f"✓ Successfully generated gTTS vocals!")
        print(f"  Output file: {result_path}")
        print(f"  Duration: {instrumental_duration} seconds")
        
        file_size = os.path.getsize(result_path) / 1024
        print(f"  File size: {file_size:.1f} KB")
        
    except Exception as e:
        print(f"✗ Error generating gTTS vocals: {e}")
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
            tts_engine="edge-tts",
            voice_name="en-US-JennyNeural"
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


def list_available_voices():
    """List available voices for different TTS engines."""
    print("\n🎤 Available Voices")
    print("=" * 60)
    
    # Test edge-tts voices
    print("\nEdge-TTS Voices (first 10):")
    try:
        synthesizer = AdvancedVocalSynthesizer(tts_engine="edge-tts")
        voices = synthesizer.get_available_voices()
        for i, voice in enumerate(voices[:10]):
            print(f"  {i+1}. {voice['name']} ({voice['language']})")
        synthesizer.cleanup()
    except Exception as e:
        print(f"  Error getting Edge-TTS voices: {e}")
    
    # Test pyttsx3 voices
    print("\npyttsx3 Voices:")
    try:
        synthesizer = AdvancedVocalSynthesizer(tts_engine="pyttsx3")
        voices = synthesizer.get_available_voices()
        for i, voice in enumerate(voices):
            print(f"  {i+1}. {voice['name']}")
        synthesizer.cleanup()
    except Exception as e:
        print(f"  Error getting pyttsx3 voices: {e}")


async def main():
    """Main function to run all tests."""
    print("🎵 Advanced Vocal Synthesis Demo")
    print("=" * 60)
    print("This demo shows the difference between basic pyttsx3 and advanced TTS engines.")
    print("The advanced engines should produce much more natural-sounding vocals.")
    
    # List available voices
    list_available_voices()
    
    # Test different TTS engines
    await test_edge_tts()
    await test_gtts()
    test_sync_wrapper()
    
    print("\n" + "=" * 60)
    print("🎵 Demo completed!")
    print("\nKey improvements in the advanced vocal synthesis:")
    print("  • Multiple TTS engines (Edge-TTS, gTTS, pyttsx3)")
    print("  • Natural-sounding voices instead of robotic speech")
    print("  • Pitch mapping to follow melody contours")
    print("  • Singing-specific audio effects (vibrato, reverb, compression)")
    print("  • Enhanced text processing for better singing pronunciation")
    print("  • Automatic fallback between engines")


if __name__ == "__main__":
    asyncio.run(main()) 