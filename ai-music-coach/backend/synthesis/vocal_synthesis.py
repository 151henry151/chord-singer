"""
Vocal synthesis module for generating spoken chord names using text-to-speech.
"""

import numpy as np
from typing import List, Tuple
import pyttsx3
from pydub import AudioSegment
from pydub.generators import Silence
import tempfile
import os
from scipy.signal import resample


class VocalSynthesizer:
    """
    A class for synthesizing spoken chord names using text-to-speech.
    """
    
    def __init__(self, voice_rate: int = 150, voice_volume: float = 0.9):
        """
        Initialize the vocal synthesizer with pyttsx3 engine.
        
        Args:
            voice_rate: Speech rate (words per minute)
            voice_volume: Volume level (0.0 to 1.0)
        """
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', voice_rate)
        self.engine.setProperty('volume', voice_volume)
        
        # Get available voices and set to a clear voice if available
        voices = self.engine.getProperty('voices')
        if voices:
            # Prefer a female voice if available for clearer pronunciation
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            else:
                # Use the first available voice
                self.engine.setProperty('voice', voices[0].id)
    
    def synthesize_spoken_chord_vocals(self, chord_timeline: List[Tuple[str, float, float]], 
                                     original_audio_duration_sec: float, 
                                     output_path: str) -> str:
        """
        Synthesize spoken chord vocals aligned with the original song timing.
        
        Args:
            chord_timeline: List of tuples (chord_name, start_time, end_time)
            original_audio_duration_sec: Total duration of the original audio
            output_path: Path where the output audio will be saved
            
        Returns:
            Path to the generated audio file
        """
        # Create a silent audio segment for the full duration
        total_duration_ms = int(original_audio_duration_sec * 1000)
        combined_audio = Silence().to_audio_segment(duration=total_duration_ms)
        
        # Process each chord in the timeline
        for chord_name, start_time, end_time in chord_timeline:
            # Generate spoken audio for this chord
            chord_audio = self._synthesize_single_chord(chord_name)
            
            # Calculate timing in milliseconds
            start_ms = int(start_time * 1000)
            end_ms = int(end_time * 1000)
            chord_duration_ms = end_ms - start_ms
            
            # Adjust chord audio duration to match the chord timing
            adjusted_chord_audio = self._adjust_audio_duration(chord_audio, chord_duration_ms)
            
            # Overlay the chord audio at the correct position
            combined_audio = combined_audio.overlay(adjusted_chord_audio, position=start_ms)
        
        # Export the final audio
        combined_audio.export(output_path, format='wav')
        
        return output_path
    
    def _synthesize_single_chord(self, chord_name: str) -> AudioSegment:
        """
        Synthesize a single chord name to audio.
        
        Args:
            chord_name: Name of the chord to synthesize
            
        Returns:
            AudioSegment containing the spoken chord name
        """
        try:
            # Create a temporary file for the TTS output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate speech and save to temporary file
            self.engine.save_to_file(chord_name, temp_path)
            self.engine.runAndWait()
            
            # Load the generated audio
            chord_audio = AudioSegment.from_wav(temp_path)
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return chord_audio
            
        except Exception as e:
            print(f"Error synthesizing chord '{chord_name}': {e}")
            # Return silence as fallback
            return Silence().to_audio_segment(duration=1000)  # 1 second of silence
    
    def _adjust_audio_duration(self, audio: AudioSegment, target_duration_ms: int) -> AudioSegment:
        """
        Adjust audio duration to match target duration.
        
        Args:
            audio: Input audio segment
            target_duration_ms: Target duration in milliseconds
            
        Returns:
            Audio segment with adjusted duration
        """
        current_duration_ms = len(audio)
        
        if current_duration_ms == target_duration_ms:
            return audio
        elif current_duration_ms > target_duration_ms:
            # Trim the audio to fit
            return audio[:target_duration_ms]
        else:
            # Pad with silence to reach target duration
            padding_duration_ms = target_duration_ms - current_duration_ms
            padding = Silence().to_audio_segment(duration=padding_duration_ms)
            return audio + padding
    
    def set_voice_properties(self, rate: int = None, volume: float = None, voice_id: str = None):
        """
        Update voice properties.
        
        Args:
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
            voice_id: Voice ID to use
        """
        if rate is not None:
            self.engine.setProperty('rate', rate)
        if volume is not None:
            self.engine.setProperty('volume', volume)
        if voice_id is not None:
            self.engine.setProperty('voice', voice_id)
    
    def get_available_voices(self) -> List[dict]:
        """
        Get list of available voices.
        
        Returns:
            List of voice dictionaries with id and name
        """
        voices = self.engine.getProperty('voices')
        return [{'id': voice.id, 'name': voice.name} for voice in voices]
    
    def cleanup(self):
        """
        Clean up the TTS engine.
        """
        if hasattr(self, 'engine'):
            self.engine.stop()

    def synthesize_sung_chord_vocals(self, chord_timeline: List[Tuple[str, float, float]],
                                     melody_contour: List[Tuple[float, float]],
                                     original_audio_duration_sec: float,
                                     output_path: str) -> str:
        """
        Synthesize sung chord vocals, pitch-mapped to the melody contour.
        Args:
            chord_timeline: List of (chord_name, start_time, end_time)
            melody_contour: List of (timestamp_sec, frequency_hz) from MelodyExtractor
            original_audio_duration_sec: Total duration of the original audio
            output_path: Path where the output audio will be saved
        Returns:
            Path to the generated audio file
        """
        total_duration_ms = int(original_audio_duration_sec * 1000)
        combined_audio = Silence().to_audio_segment(duration=total_duration_ms)

        for chord_name, start_time, end_time in chord_timeline:
            # Find melody segment for this chord
            segment = [f for (t, f) in melody_contour if start_time <= t < end_time and f > 0]
            if segment:
                target_pitch_hz = float(np.mean(segment))
            else:
                target_pitch_hz = 220.0  # fallback: A3
            chord_duration_ms = int((end_time - start_time) * 1000)
            # Syllabify for more natural TTS
            syllables = self.syllabify_chord_name(chord_name)
            tts_text = ' '.join(syllables)
            chord_audio = self.sing_chord_name(tts_text, target_pitch_hz, chord_duration_ms)
            combined_audio = combined_audio.overlay(chord_audio, position=int(start_time * 1000))

        combined_audio.export(output_path, format='wav')
        return output_path

    def sing_chord_name(self, chord_name: str, target_pitch_hz: float, duration_ms: int) -> AudioSegment:
        """
        Generate TTS audio for chord_name and pitch-shift it to target_pitch_hz, stretching to duration_ms.
        Args:
            chord_name: The chord name to sing
            target_pitch_hz: The target pitch in Hz
            duration_ms: The target duration in ms
        Returns:
            AudioSegment of the pitch-shifted, duration-matched chord name
        """
        # Generate TTS audio at default pitch
        tts_audio = self._synthesize_single_chord(chord_name)
        # Convert to numpy array
        samples = np.array(tts_audio.get_array_of_samples()).astype(np.float32)
        sr = tts_audio.frame_rate
        # Estimate original pitch (very rough: use default TTS pitch, e.g., 220 Hz)
        orig_pitch_hz = 220.0
        # Compute resample factor
        resample_factor = target_pitch_hz / orig_pitch_hz
        if resample_factor <= 0:
            resample_factor = 1.0
        # Pitch shift by resampling (note: this changes duration)
        new_length = int(len(samples) / resample_factor)
        if new_length > 0:
            shifted = resample(samples, new_length)
        else:
            shifted = samples
        # Convert back to AudioSegment
        shifted_audio = AudioSegment(
            shifted.astype(np.int16).tobytes(),
            frame_rate=int(sr),
            sample_width=tts_audio.sample_width,
            channels=tts_audio.channels
        )
        # Now adjust duration (stretch or trim)
        final_audio = self._adjust_audio_duration(shifted_audio, duration_ms)
        return final_audio

    def syllabify_chord_name(self, chord_name: str) -> List[str]:
        """
        Break down chord symbols into pronounceable syllables.
        E.g., 'Cmaj7' -> ['C', 'major', 'seven']
        """
        # Simple rules for common chord types
        import re
        chord = chord_name.upper()
        root = re.match(r'^[A-G][#B]?b?', chord)
        rest = chord[len(root.group(0)):] if root else chord
        syllables = [root.group(0)] if root else []
        # Map common chord types
        mapping = [
            (r'MAJ7', ['major', 'seven']),
            (r'MIN7', ['minor', 'seven']),
            (r'MAJ', ['major']),
            (r'MIN', ['minor']),
            (r'M', ['major']),
            (r'MINOR', ['minor']),
            (r'AUG', ['augmented']),
            (r'DIM', ['diminished']),
            (r'7', ['seven']),
            (r'6', ['six']),
            (r'9', ['nine']),
            (r'11', ['eleven']),
            (r'13', ['thirteen'])
        ]
        found = False
        for pat, syls in mapping:
            if rest.startswith(pat):
                syllables.extend(syls)
                rest = rest[len(pat):]
                found = True
                break
        if not found and rest:
            syllables.append(rest.lower())
        return [s for s in syllables if s] 