"""
Vocal synthesis module for generating sung chord names using Coqui TTS.
"""

import numpy as np
from typing import List, Tuple
import tempfile
import os
from scipy.signal import resample
import re
from pydub import AudioSegment
from TTS.api import TTS
import librosa


class VocalSynthesizer:
    """
    A class for synthesizing sung chord names using Coqui TTS with singing characteristics.
    """
    
    def __init__(self, model_name: str = "tts_models/en/ljspeech/tacotron2-DDC", 
                 vocoder_name: str = "vocoder_models/en/ljspeech/hifigan_v2"):
        """
        Initialize the vocal synthesizer with Coqui TTS.
        
        Args:
            model_name: Coqui TTS model to use
            vocoder_name: Vocoder model to use for audio generation
        """
        self.model_name = model_name
        self.rate = 1.0
        self.volume = 1.0
        
        # Initialize Coqui TTS
        try:
            self.tts = TTS(model_name=model_name, vocoder_name=vocoder_name, progress_bar=False)
            print(f"✓ Coqui TTS initialized with model: {model_name}")
        except Exception as e:
            print(f"Warning: Could not load specific model, using default: {e}")
            # Fall back to default model
            self.tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
            print("✓ Coqui TTS initialized with default model")
    
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
        combined_audio = AudioSegment.silent(duration=total_duration_ms)
        
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
        Synthesize a single chord name to audio using Coqui TTS.
        
        Args:
            chord_name: Name of the chord to synthesize
            
        Returns:
            AudioSegment containing the spoken chord name
        """
        if not self.tts:
            raise RuntimeError("TTS engine not initialized")
        
        try:
            # Generate audio using Coqui TTS
            audio_path = self.tts.tts_to_file(
                text=chord_name,
                file_path="temp_chord.wav"
            )
            
            # Load the generated audio
            chord_audio = AudioSegment.from_wav(audio_path)
            
            # Clean up temporary file
            if os.path.exists(audio_path):
                os.unlink(audio_path)
            
            return chord_audio
            
        except Exception as e:
            print(f"Error synthesizing chord '{chord_name}': {e}")
            # Return silence as fallback
            return AudioSegment.silent(duration=1000)  # 1 second of silence
    
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
            padding = AudioSegment.silent(duration=padding_duration_ms)
            return audio + padding
    
    def set_voice_properties(self, rate: int = None, volume: float = None, voice_id: str = None):
        """
        Update voice properties for Coqui TTS.
        
        Args:
            rate: Speech rate (not directly applicable to Coqui TTS)
            volume: Volume level (0.0 to 1.0)
            voice_id: Voice model to use
        """
        if volume is not None:
            print(f"Note: Volume adjustment will be applied during audio processing")
        if rate is not None:
            print(f"Note: Rate adjustment not directly supported in Coqui TTS")
        if voice_id is not None:
            print(f"Note: Voice switching requires reinitializing TTS model")
    
    def get_available_voices(self) -> List[dict]:
        """
        Get list of available voices for Coqui TTS.
        
        Returns:
            List of voice dictionaries with id and name
        """
        # Return available Coqui TTS models
        available_models = TTS.list_models()
        return [
            {'id': model, 'name': model.split('/')[-1]} 
            for model in available_models 
            if 'tts_models' in model and '/en/' in model
        ]
    
    def cleanup(self):
        """
        Clean up the Coqui TTS resources.
        """
        if hasattr(self, 'tts'):
            self.tts = None

    def synthesize_sung_chord_vocals(self, chord_timeline: List[Tuple[str, float, float]],
                                     melody_contour: List[Tuple[float, float]],
                                     original_audio_duration_sec: float,
                                     output_path: str,
                                     original_audio_path: str) -> str:
        """
        Synthesize sung chord vocals, pitch-mapped to the melody contour.
        Args:
            chord_timeline: List of (chord_name, start_time, end_time)
            melody_contour: List of (timestamp_sec, frequency_hz) from MelodyExtractor
            original_audio_duration_sec: Total duration of the original audio
            output_path: Path where the output audio will be saved
            original_audio_path: Path to the original audio file for instrumental track
        Returns:
            Path to the generated audio file
        """
        print(f"Synthesizing vocals for {len(chord_timeline)} chords")
        print(f"Audio duration: {original_audio_duration_sec} seconds")
        print(f"Output path: {output_path}")
        print(f"Original audio path: {original_audio_path}")
        
        # Load the original instrumental track
        try:
            print(f"Loading original instrumental track from: {original_audio_path}")
            instrumental_track = AudioSegment.from_file(original_audio_path)
            print(f"Loaded instrumental track: {len(instrumental_track)} ms")
            
            # Ensure the instrumental track matches the expected duration
            if len(instrumental_track) != int(original_audio_duration_sec * 1000):
                print(f"Warning: Instrumental duration mismatch. Expected: {int(original_audio_duration_sec * 1000)}ms, Got: {len(instrumental_track)}ms")
                # Trim or pad to match expected duration
                expected_duration_ms = int(original_audio_duration_sec * 1000)
                if len(instrumental_track) > expected_duration_ms:
                    instrumental_track = instrumental_track[:expected_duration_ms]
                else:
                    # Pad with silence
                    padding_duration = expected_duration_ms - len(instrumental_track)
                    padding = AudioSegment.silent(duration=padding_duration)
                    instrumental_track = instrumental_track + padding
        except Exception as e:
            print(f"Error loading original audio: {e}")
            print("Falling back to silent instrumental track")
            instrumental_track = AudioSegment.silent(duration=int(original_audio_duration_sec * 1000))
        
        # Generate synthesized vocals
        vocals_track = AudioSegment.silent(duration=len(instrumental_track))

        for i, (chord_name, start_time, end_time) in enumerate(chord_timeline):
            print(f"Processing chord {i+1}/{len(chord_timeline)}: {chord_name} at {start_time}-{end_time}s")
            # Find melody segment for this chord
            melody_points = [(t, f) for (t, f) in melody_contour if start_time <= t < end_time and f > 0]
            chord_duration_ms = int((end_time - start_time) * 1000)
            syllables = self.syllabify_chord_name(chord_name)
            tts_text = ' '.join(syllables)
            print(f"  Melody points: {len(melody_points)}")
            try:
                chord_audio = self.sing_chord_name_to_melody_contour(tts_text, melody_points, chord_duration_ms)
                print(f"  Generated audio length: {len(chord_audio)} ms")
                vocals_track = vocals_track.overlay(chord_audio, position=int(start_time * 1000))
            except Exception as e:
                print(f"  Error generating audio for chord '{chord_name}': {e}")
                # Continue with next chord

        print(f"Vocals track length: {len(vocals_track)} ms")
        
        # Combine instrumental and vocals
        # Lower the volume of the instrumental to make vocals more prominent
        instrumental_track = instrumental_track - 10  # Reduce volume by 10dB
        vocals_track = vocals_track + 5  # Increase vocals volume by 5dB
        
        combined_audio = instrumental_track.overlay(vocals_track)
        
        print(f"Final combined audio length: {len(combined_audio)} ms")
        print(f"Exporting to: {output_path}")
        
        try:
            combined_audio.export(output_path, format='wav')
            print(f"Successfully exported audio to: {output_path}")
            
            # Verify file was created and has content
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"Output file size: {file_size} bytes")
                if file_size == 0:
                    print("Warning: Output file is empty!")
            else:
                print("Error: Output file was not created!")
                
        except Exception as e:
            print(f"Error exporting audio: {e}")
            import traceback
            traceback.print_exc()
        
        return output_path

    def _spectral_pitch_shift(self, samples: np.ndarray, sr: int, pitch_factor: float) -> np.ndarray:
        """
        Apply spectral pitch shifting using phase vocoder technique.
        This changes pitch without affecting timing/duration.
        
        Args:
            samples: Input audio samples
            sr: Sample rate
            pitch_factor: Pitch shift factor (1.0 = no change, 2.0 = octave up, 0.5 = octave down)
            
        Returns:
            Pitch-shifted samples with same duration as input
        """
        if len(samples) < 2:
            return samples
        
        # Apply phase vocoder pitch shifting
        try:
            # Use librosa's phase vocoder for proper pitch shifting
            shifted_samples = librosa.effects.pitch_shift(
                samples, 
                sr=sr, 
                n_steps=12 * np.log2(pitch_factor),  # Convert factor to semitones
                bins_per_octave=12
            )
            
            return shifted_samples
            
        except Exception as e:
            print(f"Phase vocoder failed, falling back to resampling: {e}")
            # Fallback to resampling if phase vocoder fails
            new_length = int(len(samples) / pitch_factor)
            if new_length > 1:
                return resample(samples, new_length)
            else:
                return samples

    def sing_chord_name(self, chord_name: str, target_pitch_hz: float, duration_ms: int) -> AudioSegment:
        """
        Generate TTS audio for chord_name and pitch-shift it to target_pitch_hz using spectral shifting.
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
        
        # Estimate original pitch - Coqui TTS typically generates around 200-300 Hz
        orig_pitch_hz = 250.0  # Typical Coqui TTS pitch
        
        # Compute pitch shift factor
        pitch_factor = target_pitch_hz / orig_pitch_hz
        
        # Clamp the pitch factor to reasonable bounds (0.5 to 2.0)
        pitch_factor = max(0.5, min(2.0, pitch_factor))
        
        print(f"    Spectral pitch shift: {orig_pitch_hz:.1f} Hz -> {target_pitch_hz:.1f} Hz (factor: {pitch_factor:.2f})")
        
        # Apply spectral pitch shifting (preserves duration)
        shifted_samples = self._spectral_pitch_shift(samples, sr, pitch_factor)
        
        # Convert back to AudioSegment
        shifted_audio = AudioSegment(
            shifted_samples.astype(np.int16).tobytes(),
            frame_rate=int(sr),
            sample_width=tts_audio.sample_width,
            channels=tts_audio.channels
        )
        
        # Now adjust duration (stretch or trim)
        final_audio = self._adjust_audio_duration(shifted_audio, duration_ms)
        
        return final_audio

    def sing_chord_name_to_melody_contour(self, chord_name: str, melody_segment: List[Tuple[float, float]], duration_ms: int) -> AudioSegment:
        """
        Generate enhanced TTS audio for chord_name and dynamically pitch-shift it to follow the melody contour using spectral shifting.
        Args:
            chord_name: The chord name to sing
            melody_segment: List of (timestamp, frequency_hz) for this chord segment
            duration_ms: The target duration in ms
        Returns:
            AudioSegment of the pitch-shifted, duration-matched chord name
        """
        # Enhance the chord name for singing
        enhanced_chord_name = self.enhance_for_singing(chord_name)
        print(f"    Enhanced text: '{enhanced_chord_name}'")
        
        # Generate TTS audio at default pitch
        tts_audio = self._synthesize_single_chord(enhanced_chord_name)
        samples = np.array(tts_audio.get_array_of_samples()).astype(np.float32)
        sr = tts_audio.frame_rate
        orig_pitch_hz = 250.0  # Typical Coqui TTS pitch

        # Define a conservative octave range for vocal synthesis
        min_pitch_hz = 200.0  # Lower bound
        max_pitch_hz = 500.0  # Upper bound

        if not melody_segment:
            # No melody points - return unmodified TTS audio with duration adjustment
            final_audio = self._adjust_audio_duration(tts_audio, duration_ms)
            return final_audio

        n_segments = len(melody_segment)
        segment_length = int(len(samples) / n_segments)
        segments = []
        
        print(f"    Processing {n_segments} melody segments for '{chord_name}'")
        
        for i, (_, freq) in enumerate(melody_segment):
            start = i * segment_length
            end = (i + 1) * segment_length if i < n_segments - 1 else len(samples)
            seg = samples[start:end]
            
            # Normalize the target pitch to stay within reasonable range
            if freq > 0:
                print(f"      Segment {i}: Original freq = {freq:.1f} Hz")
                
                # Find the closest pitch in our target range by octave shifting
                normalized_freq = freq
                while normalized_freq > max_pitch_hz:
                    normalized_freq /= 2.0  # Go down an octave
                while normalized_freq < min_pitch_hz:
                    normalized_freq *= 2.0  # Go up an octave
                
                # Ensure it's within bounds
                normalized_freq = max(min_pitch_hz, min(max_pitch_hz, normalized_freq))
                print(f"      Segment {i}: Normalized freq = {normalized_freq:.1f} Hz")
            else:
                normalized_freq = orig_pitch_hz
                print(f"      Segment {i}: Using default freq = {normalized_freq:.1f} Hz")
            
            # Apply spectral pitch shifting to this segment
            pitch_factor = normalized_freq / orig_pitch_hz
            # Conservative bounds
            pitch_factor = max(0.7, min(1.5, pitch_factor))
            
            print(f"      Segment {i}: Pitch factor = {pitch_factor:.2f}")
            
            # Apply spectral pitch shifting (preserves duration)
            shifted_seg = self._spectral_pitch_shift(seg, sr, pitch_factor)
            segments.append(shifted_seg)
        
        # Concatenate all pitch-shifted segments
        if segments:
            all_samples = np.concatenate(segments)
        else:
            all_samples = samples
        
        # Convert back to AudioSegment
        shifted_audio = AudioSegment(
            all_samples.astype(np.int16).tobytes(),
            frame_rate=int(sr),
            sample_width=tts_audio.sample_width,
            channels=tts_audio.channels
        )
        
        # Adjust duration
        final_audio = self._adjust_audio_duration(shifted_audio, duration_ms)
        return final_audio

    def syllabify_chord_name(self, chord_name: str) -> List[str]:
        """
        Break down chord symbols into pronounceable syllables.
        E.g., 'Cmaj7' -> ['C', 'major', 'seven']
        """
        # Simple rules for common chord types
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

    def enhance_for_singing(self, chord_name: str) -> str:
        """
        Enhanced chord name text for singing with proper pronunciation.
        Fixes the "#" character vocabulary issue and implements proper chord pronunciation.
        
        Args:
            chord_name: Original chord name
            
        Returns:
            Enhanced chord name with singing characteristics
        """
        enhanced = chord_name.upper()
        
        # Phase 1: Parse chord structure more carefully to handle sharps and flats
        chord_parts = []
        
        # Extract root note with sharp/flat as a unit
        root_match = re.match(r'^([A-G][#♯b♭]?)', enhanced)
        if root_match:
            root_with_accidental = root_match.group(1)
            root_pronunciations = {
                # Natural notes
                'A': 'AYE',   'B': 'BEE',   'C': 'SEE',   'D': 'DEE',   
                'E': 'EEE',   'F': 'EFF',   'G': 'GEE',
                # Sharp notes
                'A#': 'AYE SHARP',  'A♯': 'AYE SHARP',
                'B#': 'BEE SHARP',  'B♯': 'BEE SHARP',
                'C#': 'SEE SHARP',  'C♯': 'SEE SHARP',
                'D#': 'DEE SHARP',  'D♯': 'DEE SHARP',
                'E#': 'EEE SHARP',  'E♯': 'EEE SHARP',
                'F#': 'EFF SHARP',  'F♯': 'EFF SHARP',
                'G#': 'GEE SHARP',  'G♯': 'GEE SHARP',
                # Flat notes
                'Ab': 'AYE FLAT',   'A♭': 'AYE FLAT',
                'Bb': 'BEE FLAT',   'B♭': 'BEE FLAT',
                'Cb': 'SEE FLAT',   'C♭': 'SEE FLAT',
                'Db': 'DEE FLAT',   'D♭': 'DEE FLAT',
                'Eb': 'EEE FLAT',   'E♭': 'EEE FLAT',
                'Fb': 'EFF FLAT',   'F♭': 'EFF FLAT',
                'Gb': 'GEE FLAT',   'G♭': 'GEE FLAT',
            }
            chord_parts.append(root_pronunciations.get(root_with_accidental, root_with_accidental))
            enhanced = enhanced[len(root_with_accidental):]  # Remove the root note with accidental
        
        # Phase 3: Chord quality pronunciations
        chord_quality_pronunciations = [
            ('MAJ7', 'MAJOR SEVEN'),
            ('MIN7', 'MINOR SEVEN'),
            ('MAJ', 'MAJOR'),
            ('MIN', 'MINOR'),
            ('MINOR', 'MINOR'),
            ('AUG', 'AUGMENTED'),
            ('DIM', 'DIMINISHED'),
            ('SUS4', 'SUSPENDED FOUR'),
            ('SUS2', 'SUSPENDED TWO'),
            ('SUS', 'SUSPENDED'),
            ('ADD', 'ADD'),
        ]
        
        # Apply chord quality pronunciations in order of specificity
        for quality, pronunciation in chord_quality_pronunciations:
            if enhanced.startswith(quality):
                chord_parts.append(pronunciation)
                enhanced = enhanced[len(quality):]
                break
        
        # Phase 4: Number pronunciations  
        number_pronunciations = {
            '13': 'THIRTEEN',
            '11': 'ELEVEN',
            '9': 'NINE',
            '7': 'SEVEN',
            '6': 'SIX',
            '4': 'FOUR',
            '2': 'TWO'
        }
        
        # Apply number pronunciations in order of length (longest first)
        for number, pronunciation in number_pronunciations.items():
            if enhanced.startswith(number):
                chord_parts.append(pronunciation)
                enhanced = enhanced[len(number):]
                break
        
        # Combine all parts
        enhanced = ' '.join(chord_parts)
        
        # Phase 5: Add singing enhancements
        # Elongate vowels for singing effect (more subtly than before)
        enhanced = re.sub(r'([AEIOU])', r'\1\1', enhanced)  # Double vowels
        
        # Add musical phrasing
        enhanced = enhanced.replace(' ', ' ... ')  # Add pauses between words
        
        # Special handling for common chord types
        enhanced = enhanced.replace('MAJOR', 'MAAAY-JOR')
        enhanced = enhanced.replace('MINOR', 'MIIIN-OR')
        enhanced = enhanced.replace('SEVEN', 'SEV-EN')
        enhanced = enhanced.replace('NINE', 'NIIINE')
        enhanced = enhanced.replace('ELEVEN', 'ELEV-EN')
        enhanced = enhanced.replace('THIRTEEN', 'THIR-TEEN')
        
        # Clean up extra spaces
        enhanced = ' '.join(enhanced.split())
        
        return enhanced 