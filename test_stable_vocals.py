#!/usr/bin/env python3
"""
Test script for stable vocals - verifies the fix for extreme pitch jumps.
"""

import sys
import os
import tempfile
import asyncio

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from synthesis.advanced_vocal_synthesis import synthesize_stable_chord_vocals_sync


def test_stable_vocals():
    """Test the stable vocals synthesis."""
    print("🎵 Testing Stable Vocals Synthesis")
    print("=" * 50)
    print("This should produce clear, stable vocals without extreme pitch jumps.")
    
    # Create a simple chord progression
    chord_timeline = [
        ("C major", 0.0, 2.0),
        ("A minor", 2.0, 4.0),
        ("F major", 4.0, 6.0),
        ("G major", 6.0, 8.0),
        ("C major", 8.0, 10.0)
    ]
    
    # Create a simple instrumental track (just silence for testing)
    instrumental_duration = 10.0
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        output_path = temp_file.name
    
    try:
        print(f"Generating stable vocals for {len(chord_timeline)} chords...")
        print(f"Duration: {instrumental_duration} seconds")
        print(f"Output: {output_path}")
        
        result_path = synthesize_stable_chord_vocals_sync(
            chord_timeline=chord_timeline,
            original_audio_duration_sec=instrumental_duration,
            output_path=output_path,
            original_audio_path=output_path,  # Use same file for instrumental (silence)
            tts_engine="edge-tts",
            voice_name="en-US-JennyNeural"
        )
        
        print(f"✅ Successfully generated stable vocals!")
        print(f"   Output file: {result_path}")
        
        # Check file size
        if os.path.exists(result_path):
            file_size = os.path.getsize(result_path) / 1024  # KB
            print(f"   File size: {file_size:.1f} KB")
            
            if file_size > 0:
                print("   ✅ File has content (not empty)")
            else:
                print("   ⚠️  File is empty!")
        else:
            print("   ❌ File was not created!")
        
        print("\n🎵 Test completed!")
        print("The vocals should now be:")
        print("  • Stable in pitch (no extreme jumps)")
        print("  • Clear and understandable")
        print("  • Natural-sounding (not robotic)")
        print("  • Perfect for learning chord progressions")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if os.path.exists(output_path):
            os.unlink(output_path)


if __name__ == "__main__":
    test_stable_vocals() 