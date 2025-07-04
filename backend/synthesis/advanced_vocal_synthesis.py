"""
Advanced vocal synthesis module for generating natural-sounding sung chord names.
Uses Coqui TTS with singing-specific enhancements.
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import asyncio
import tempfile
import os
import re
from pydub import AudioSegment
from scipy.signal import resample
import librosa
import soundfile as sf

# TTS Engine
from TTS.api import TTS

# Phase 4: Advanced TTS for better naturalness (from plan_of_action.txt)
try:
    import edge_tts
    import asyncio
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    print("edge-tts not available, falling back to Coqui TTS")

# For better audio processing
from scipy import signal
import random


class AdvancedVocalSynthesizer:
    """
    Advanced vocal synthesizer using Coqui TTS with singing enhancements.
    Produces natural-sounding vocals with musical characteristics.
    """
    
    def __init__(self, 
                 model_name: str = "tts_models/en/ljspeech/tacotron2-DDC",
                 vocoder_name: str = "vocoder_models/en/ljspeech/hifigan_v2",
                 rate: float = 0.9,
                 volume: float = 0.9):
        """
        Initialize the advanced vocal synthesizer.
        
        Args:
            model_name: Coqui TTS model to use
            vocoder_name: Vocoder model for audio generation
            rate: Speech rate (affects processing, not directly applicable to Coqui)
            volume: Volume level (0.0-1.0)
        """
        self.model_name = model_name
        self.vocoder_name = vocoder_name
        self.rate = rate
        self.volume = volume
        
        # Initialize Coqui TTS
        try:
            self.tts = TTS(model_name=model_name, vocoder_name=vocoder_name, progress_bar=False)
            print(f"✓ Advanced VocalSynthesizer initialized with Coqui TTS")
            print(f"  Model: {model_name}")
            print(f"  Vocoder: {vocoder_name}")
            print(f"  Rate: {rate}")
            print(f"  Volume: {volume}")
        except Exception as e:
            print(f"Warning: Could not load specific model, using default: {e}")
            # Fall back to default model
            self.tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
            print("✓ Advanced VocalSynthesizer initialized with default Coqui TTS model")
    
    async def synthesize_sung_chord_vocals(self, 
                                          chord_timeline: List[Tuple[str, float, float]],
                                          melody_contour: List[Tuple[float, float]],
                                          original_audio_duration_sec: float,
                                          output_path: str,
                                          original_audio_path: str) -> str:
        """
        Synthesize sung chord vocals with advanced Coqui TTS and singing enhancements.
        
        Args:
            chord_timeline: List of (chord_name, start_time, end_time)
            melody_contour: List of (timestamp_sec, frequency_hz) from MelodyExtractor
            original_audio_duration_sec: Total duration of the original audio
            output_path: Path where the output audio will be saved
            original_audio_path: Path to the original audio file for instrumental track
            
        Returns:
            Path to the generated audio file
        """
        print(f"🎵 Synthesizing advanced vocals for {len(chord_timeline)} chords")
        print(f"   TTS Engine: Coqui TTS")
        print(f"   Model: {self.model_name}")
        
        # Load the original instrumental track
        try:
            instrumental_track = AudioSegment.from_file(original_audio_path)
            print(f"✓ Loaded instrumental track: {len(instrumental_track)} ms")
        except Exception as e:
            print(f"⚠️  Error loading original audio: {e}")
            instrumental_track = AudioSegment.silent(duration=int(original_audio_duration_sec * 1000))
        
        # Generate synthesized vocals
        vocals_track = AudioSegment.silent(duration=len(instrumental_track))
        
        for i, (chord_name, start_time, end_time) in enumerate(chord_timeline):
            print(f"🎼 Processing chord {i+1}/{len(chord_timeline)}: {chord_name}")
            
            # Find melody segment for this chord
            melody_points = [(t, f) for (t, f) in melody_contour 
                           if start_time <= t < end_time and f > 0]
            
            chord_duration_ms = int((end_time - start_time) * 1000)
            
            # Enhance chord name for singing
            enhanced_chord_name = self._enhance_for_singing(chord_name)
            print(f"   Enhanced text: '{enhanced_chord_name}'")
            
            try:
                # Generate audio with best available TTS (edge-tts preferred for naturalness)
                chord_audio = self._synthesize_with_best_tts(enhanced_chord_name)
                
                # Apply singing enhancements
                chord_audio = self._apply_singing_enhancements(
                    chord_audio, melody_points, chord_duration_ms
                )
                
                # Overlay at the correct position
                vocals_track = vocals_track.overlay(
                    chord_audio, position=int(start_time * 1000)
                )
                
                print(f"   ✓ Generated {len(chord_audio)} ms of audio")
                
            except Exception as e:
                print(f"   ✗ Error generating audio for '{chord_name}': {e}")
                continue
        
        # Mix instrumental and vocals with better balance
        instrumental_track = instrumental_track - 8  # Reduce instrumental volume
        vocals_track = vocals_track + 3  # Boost vocals slightly
        
        combined_audio = instrumental_track.overlay(vocals_track)
        
        # Export the final audio
        combined_audio.export(output_path, format='wav')
        print(f"🎵 Successfully exported to: {output_path}")
        
        return output_path
    
    def _synthesize_with_coqui_tts(self, text: str) -> AudioSegment:
        """Synthesize text using Coqui TTS."""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate speech with Coqui TTS
            self.tts.tts_to_file(text=text, file_path=temp_path)
            
            # Load the generated audio
            audio = AudioSegment.from_wav(temp_path)
            
            # Clean up
            os.unlink(temp_path)
            
            return audio
            
        except Exception as e:
            print(f"Coqui TTS error: {e}")
            # Return silence as fallback
            return AudioSegment.silent(duration=1000)
    
    async def _synthesize_with_edge_tts(self, text: str) -> AudioSegment:
        """
        Synthesize text using edge-tts for better naturalness.
        Implements Phase 4 of plan_of_action.txt - improved voice naturalness.
        """
        try:
            # Use en-US-JennyNeural voice as mentioned in the plan
            voice = "en-US-JennyNeural"
            
            # Create a temporary file for edge-tts output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate speech with edge-tts
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(temp_path)
            
            # Load the generated audio
            audio = AudioSegment.from_wav(temp_path)
            
            # Clean up
            os.unlink(temp_path)
            
            return audio
            
        except Exception as e:
            print(f"Edge TTS error: {e}")
            # Fallback to Coqui TTS
            return self._synthesize_with_coqui_tts(text)
    
    def _synthesize_with_best_tts(self, text: str) -> AudioSegment:
        """
        Synthesize text using the best available TTS engine.
        Prioritizes edge-tts for naturalness, falls back to Coqui TTS.
        """
        if EDGE_TTS_AVAILABLE:
            # Use edge-tts for better naturalness
            try:
                return asyncio.run(self._synthesize_with_edge_tts(text))
            except Exception as e:
                print(f"Edge TTS failed, falling back to Coqui TTS: {e}")
                return self._synthesize_with_coqui_tts(text)
        else:
            # Use Coqui TTS as fallback
            return self._synthesize_with_coqui_tts(text)
    
    def _apply_singing_enhancements(self, 
                                  audio: AudioSegment, 
                                  melody_points: List[Tuple[float, float]], 
                                  duration_ms: int) -> AudioSegment:
        """
        Apply singing-specific enhancements to make the audio sound more musical.
        
        Args:
            audio: Input audio segment
            melody_points: List of (timestamp, frequency) for pitch mapping
            duration_ms: Target duration in milliseconds
            
        Returns:
            Enhanced audio segment
        """
        # Convert to numpy array for processing
        samples = np.array(audio.get_array_of_samples()).astype(np.float32)
        sr = audio.frame_rate
        
        # Apply pitch mapping if melody points are available
        if melody_points:
            samples = self._apply_pitch_mapping(samples, sr, melody_points, duration_ms)
        
        # Apply singing-specific effects
        samples = self._apply_singing_effects(samples, sr)
        
        # Convert back to AudioSegment
        enhanced_audio = AudioSegment(
            samples.astype(np.int16).tobytes(),
            frame_rate=int(sr),
            sample_width=audio.sample_width,
            channels=audio.channels
        )
        
        # Adjust duration to match target
        enhanced_audio = self._adjust_audio_duration(enhanced_audio, duration_ms)
        
        return enhanced_audio
    
    def _apply_pitch_mapping(self, 
                           samples: np.ndarray, 
                           sr: int, 
                           melody_points: List[Tuple[float, float]], 
                           duration_ms: int) -> np.ndarray:
        """
        Apply pitch mapping to follow the melody contour with proper range normalization.
        """
        if not melody_points or len(samples) < 2:
            return samples
        
        # Calculate average pitch for the segment
        valid_freqs = [f for _, f in melody_points if f > 0]
        if not valid_freqs:
            return samples
        
        target_pitch = np.mean(valid_freqs)
        
        # Human vocal range for comfortable singing
        MIN_VOCAL_PITCH = 150.0   # Hz
        MAX_VOCAL_PITCH = 500.0   # Hz
        
        # Normalize the target pitch to stay within vocal range
        normalized_pitch = self._normalize_to_vocal_octave(target_pitch)
        
        # Clamp to reasonable vocal range
        normalized_pitch = max(MIN_VOCAL_PITCH, min(MAX_VOCAL_PITCH, normalized_pitch))
        
        # Estimate original Coqui TTS pitch
        original_pitch = 250.0  # Typical Coqui TTS pitch
        
        # Calculate pitch shift factor with conservative limits
        pitch_factor = normalized_pitch / original_pitch
        pitch_factor = max(0.8, min(1.4, pitch_factor))
        
        print(f"   🎵 Pitch mapping: {original_pitch:.1f} Hz → {normalized_pitch:.1f} Hz (factor: {pitch_factor:.2f})")
        
        # Apply pitch shift using resampling
        new_length = int(len(samples) / pitch_factor)
        if new_length > 1:
            shifted = resample(samples, new_length)
        else:
            shifted = samples
        
        return shifted
    
    def _normalize_to_vocal_octave(self, frequency: float) -> float:
        """
        Normalize musical frequency to comfortable vocal range.
        """
        TARGET_MIN = 180.0  # Hz
        TARGET_MAX = 450.0  # Hz
        
        # Transpose to comfortable vocal range
        while frequency < TARGET_MIN:
            frequency *= 2.0  # Go up an octave
        while frequency > TARGET_MAX:
            frequency /= 2.0  # Go down an octave
        
        return frequency
    
    def _apply_singing_effects(self, samples: np.ndarray, sr: int) -> np.ndarray:
        """Apply singing-specific audio effects."""
        if len(samples) < 2:
            return samples
            
        # 1. Add subtle vibrato for more natural singing
        vibrato_rate = 4.5  # Hz
        vibrato_depth = 0.015  # 1.5% pitch modulation
        
        t = np.arange(len(samples)) / sr
        vibrato = np.sin(2 * np.pi * vibrato_rate * t) * vibrato_depth
        
        # Apply vibrato using phase modulation
        phase = np.cumsum(vibrato)
        samples = samples * np.cos(phase) + np.roll(samples, 1) * np.sin(phase)
        
        # 2. Add subtle reverb for more natural sound
        reverb_length = int(0.08 * sr)  # 80ms reverb
        if reverb_length > 0:
            reverb_ir = np.exp(-np.arange(reverb_length) / (0.04 * sr))
            reverb_ir = reverb_ir / np.sum(reverb_ir)
            
            samples = np.convolve(samples, reverb_ir, mode='same')
        
        # 3. Apply gentle compression to even out dynamics
        threshold = 0.6
        ratio = 2.5
        
        # Simple soft-knee compression
        gain_reduction = np.where(
            np.abs(samples) > threshold,
            (np.abs(samples) - threshold) * (1 - 1/ratio),
            0
        )
        samples = samples * (1 - gain_reduction * 0.5)
        
        # 4. Add subtle breathiness (controlled high-frequency content)
        breath_noise = np.random.normal(0, 0.008, len(samples))
        # Simple high-pass effect
        breath_noise = breath_noise - np.roll(breath_noise, 1) * 0.95
        samples = samples + breath_noise
        
        return samples
    
    def _adjust_audio_duration(self, audio: AudioSegment, target_duration_ms: int) -> AudioSegment:
        """Adjust audio duration to match target duration."""
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
    
    def _enhance_for_singing(self, chord_name: str) -> str:
        """
        Enhance chord name text to sound more like singing.
        
        Args:
            chord_name: Original chord name
            
        Returns:
            Enhanced chord name with singing characteristics
        """
        # Convert to uppercase for consistency
        enhanced = chord_name.upper()
        
        # Add musical phrasing and elongation
        enhanced = enhanced.replace(' ', ' ... ')
        
        # Elongate vowels for singing effect (more subtly)
        enhanced = re.sub(r'([AEIOU])', r'\1\1', enhanced)
        
        # Add musical emphasis to common chord types
        enhanced = enhanced.replace('MAJOR', 'MAAY-JOR')
        enhanced = enhanced.replace('MINOR', 'MIIIN-OR')
        enhanced = enhanced.replace('SEVEN', 'SEV-EN')
        enhanced = enhanced.replace('NINE', 'NIIINE')
        enhanced = enhanced.replace('ELEVEN', 'ELEV-EN')
        enhanced = enhanced.replace('THIRTEEN', 'THIR-TEEN')
        
        # Add musical pauses for better rhythm
        enhanced = enhanced.replace('-', ' ... ')
        
        return enhanced
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices for Coqui TTS."""
        try:
            available_models = TTS.list_models()
            return [
                {
                    'id': model,
                    'name': model.split('/')[-1],
                    'language': 'en' if '/en/' in model else 'other',
                    'type': 'tts'
                }
                for model in available_models
                if 'tts_models' in model and '/en/' in model
            ]
        except Exception as e:
            print(f"Error getting Coqui TTS models: {e}")
            return []
    
    def set_voice_properties(self, rate: float = None, volume: float = None, model_name: str = None):
        """Update voice properties."""
        if rate is not None:
            self.rate = rate
            print(f"Rate updated to: {rate}")
        if volume is not None:
            self.volume = volume
            print(f"Volume updated to: {volume}")
        if model_name is not None:
            print(f"Note: Model switching requires reinitializing TTS engine")
            self.model_name = model_name
    
    def cleanup(self):
        """Clean up Coqui TTS resources."""
        if hasattr(self, 'tts'):
            self.tts = None
            print("✓ Coqui TTS resources cleaned up")
    
    async def synthesize_stable_chord_vocals(self, 
                                           chord_timeline: List[Tuple[str, float, float]],
                                           original_audio_duration_sec: float,
                                           output_path: str,
                                           original_audio_path: str) -> str:
        """
        Synthesize stable chord vocals without pitch mapping (easier to follow).
        
        Args:
            chord_timeline: List of (chord_name, start_time, end_time)
            original_audio_duration_sec: Total duration of the original audio
            output_path: Path where the output audio will be saved
            original_audio_path: Path to the original audio file for instrumental track
            
        Returns:
            Path to the generated audio file
        """
        print(f"🎵 Synthesizing stable chord vocals for {len(chord_timeline)} chords")
        
        # Load the original instrumental track
        try:
            instrumental_track = AudioSegment.from_file(original_audio_path)
            print(f"✓ Loaded instrumental track: {len(instrumental_track)} ms")
        except Exception as e:
            print(f"⚠️  Error loading original audio: {e}")
            instrumental_track = AudioSegment.silent(duration=int(original_audio_duration_sec * 1000))
        
        # Generate synthesized vocals
        vocals_track = AudioSegment.silent(duration=len(instrumental_track))
        
        for i, (chord_name, start_time, end_time) in enumerate(chord_timeline):
            print(f"🎼 Processing chord {i+1}/{len(chord_timeline)}: {chord_name}")
            
            chord_duration_ms = int((end_time - start_time) * 1000)
            
            # Phase 3: Generate filler words and timing (from plan_of_action.txt)
            filler_text = ""
            if i < len(chord_timeline) - 1:
                next_chord = chord_timeline[i + 1][0]
                time_gap = chord_timeline[i + 1][1] - end_time
                filler_text = self._generate_filler_words(
                    chord_name, next_chord, time_gap, i, len(chord_timeline)
                )
                print(f"   Filler text: '{filler_text}'")
            
            # Enhance chord name with filler words for natural flow
            enhanced_chord_name = self._enhance_for_singing_with_filler(chord_name, filler_text)
            print(f"   Enhanced text: '{enhanced_chord_name}'")
            
            try:
                # Generate audio with best available TTS (edge-tts preferred for naturalness)
                chord_audio = self._synthesize_with_best_tts(enhanced_chord_name)
                
                # Apply basic singing enhancements (no pitch mapping)
                chord_audio = self._apply_basic_singing_enhancements(chord_audio, chord_duration_ms)
                
                # Overlay at the correct position
                vocals_track = vocals_track.overlay(
                    chord_audio, position=int(start_time * 1000)
                )
                
                print(f"   ✓ Generated {len(chord_audio)} ms of stable audio")
                
            except Exception as e:
                print(f"   ✗ Error generating audio for '{chord_name}': {e}")
                continue
        
        # Mix instrumental and vocals
        instrumental_track = instrumental_track - 10  # Reduce instrumental volume more
        vocals_track = vocals_track + 5  # Boost vocals more for clarity
        
        combined_audio = instrumental_track.overlay(vocals_track)
        
        # Export the final audio
        combined_audio.export(output_path, format='wav')
        print(f"🎵 Successfully exported stable vocals to: {output_path}")
        
        return output_path
    
    def _enhance_for_singing_simple(self, chord_name: str) -> str:
        """
        Enhanced chord pronunciation system for stable chord vocals.
        Implements proper chord pronunciation mapping as per plan_of_action.txt:
        - A → "Aye" (not "Ah")
        - # → "Sharp" 
        - b → "Flat"
        - Natural singing pronunciation for all chord types
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
        
        # Phase 5: Combine all parts
        enhanced = ' '.join(chord_parts)
        
        # Clean up extra spaces
        enhanced = ' '.join(enhanced.split())
        
        return enhanced
    
    def _generate_filler_words(self, 
                             current_chord: str, 
                             next_chord: str, 
                             time_gap_sec: float,
                             chord_index: int,
                             total_chords: int) -> str:
        """
        Generate contextual filler words between chord changes.
        Implements Phase 3 of plan_of_action.txt: filler words and timing.
        
        Args:
            current_chord: Current chord name
            next_chord: Next chord name  
            time_gap_sec: Time available between chords
            chord_index: Current chord index (0-based)
            total_chords: Total number of chords
            
        Returns:
            Filler text appropriate for the context
        """
        # Determine context
        is_returning = (chord_index > 0 and current_chord == next_chord)
        is_staying = (current_chord == next_chord)
        is_first_chord = (chord_index == 0)
        is_last_chord = (chord_index == total_chords - 1)
        
        # Generate filler based on available time and context
        if time_gap_sec > 2.0:
            # Long gaps: full phrases
            if is_returning:
                return "Now we're back to"
            elif is_first_chord:
                return "We start with"
            elif is_last_chord:
                return "Finally we have"
            else:
                return "Now we're moving to"
                
        elif time_gap_sec > 1.0:
            # Medium gaps: shorter phrases
            if is_returning:
                return "Back to"
            elif is_staying:
                return "Stay on"
            else:
                return "Now go to"
                
        elif time_gap_sec > 0.5:
            # Short gaps: minimal filler
            if is_returning:
                return "Back to"
            else:
                return "To"
        else:
            # Very short gaps: just the chord
            return ""
    
    def _enhance_for_singing_with_filler(self, 
                                       chord_name: str, 
                                       filler_text: str = "") -> str:
        """
        Enhanced chord pronunciation with filler words for natural flow.
        
        Args:
            chord_name: The chord name to enhance
            filler_text: Optional filler text to prepend
            
        Returns:
            Enhanced text with filler words and proper pronunciation
        """
        # Get the properly pronounced chord name
        enhanced_chord = self._enhance_for_singing_simple(chord_name)
        
        # Combine with filler text if provided
        if filler_text:
            return f"{filler_text} {enhanced_chord}"
        else:
            return enhanced_chord
    
    def _apply_basic_singing_enhancements(self, audio: AudioSegment, duration_ms: int) -> AudioSegment:
        """
        Apply basic singing enhancements without pitch mapping.
        """
        # Convert to numpy array for processing
        samples = np.array(audio.get_array_of_samples()).astype(np.float32)
        sr = audio.frame_rate
        
        # Apply subtle singing effects
        samples = self._apply_subtle_singing_effects(samples, sr)
        
        # Convert back to AudioSegment
        enhanced_audio = AudioSegment(
            samples.astype(np.int16).tobytes(),
            frame_rate=int(sr),
            sample_width=audio.sample_width,
            channels=audio.channels
        )
        
        # Adjust duration to match target
        enhanced_audio = self._adjust_audio_duration(enhanced_audio, duration_ms)
        
        return enhanced_audio
    
    def _apply_subtle_singing_effects(self, samples: np.ndarray, sr: int) -> np.ndarray:
        """Apply subtle singing effects for stable vocals."""
        if len(samples) < 2:
            return samples
            
        # 1. Very subtle vibrato
        vibrato_rate = 3.5  # Hz
        vibrato_depth = 0.01  # 1% pitch modulation
        
        t = np.arange(len(samples)) / sr
        vibrato = np.sin(2 * np.pi * vibrato_rate * t) * vibrato_depth
        
        # Apply very light vibrato
        phase = np.cumsum(vibrato) * 0.5
        samples = samples * (1 + phase * 0.1)
        
        # 2. Light reverb
        reverb_length = int(0.05 * sr)  # 50ms reverb
        if reverb_length > 0:
            reverb_ir = np.exp(-np.arange(reverb_length) / (0.03 * sr))
            reverb_ir = reverb_ir / np.sum(reverb_ir)
            
            reverb_signal = np.convolve(samples, reverb_ir, mode='same')
            samples = samples * 0.8 + reverb_signal * 0.2
        
        # 3. Gentle compression
        threshold = 0.7
        ratio = 2.0
        
        gain_reduction = np.where(
            np.abs(samples) > threshold,
            (np.abs(samples) - threshold) * (1 - 1/ratio) * 0.3,
            0
        )
        samples = samples * (1 - gain_reduction)
        
        return samples


def synthesize_sung_chord_vocals_sync(chord_timeline: List[Tuple[str, float, float]],
                                     melody_contour: List[Tuple[float, float]],
                                     original_audio_duration_sec: float,
                                     output_path: str,
                                     original_audio_path: str,
                                     model_name: str = "tts_models/en/ljspeech/tacotron2-DDC",
                                     vocoder_name: str = "vocoder_models/en/ljspeech/hifigan_v2") -> str:
    """
    Synchronous wrapper for synthesize_sung_chord_vocals.
    
    Args:
        chord_timeline: List of (chord_name, start_time, end_time)
        melody_contour: List of (timestamp_sec, frequency_hz)
        original_audio_duration_sec: Duration of original audio
        output_path: Output file path
        original_audio_path: Original audio file path
        model_name: Coqui TTS model to use
        vocoder_name: Vocoder model to use
        
    Returns:
        Path to generated audio file
    """
    synthesizer = AdvancedVocalSynthesizer(
        model_name=model_name,
        vocoder_name=vocoder_name
    )
    
    try:
        # Run the async function
        result = asyncio.run(synthesizer.synthesize_sung_chord_vocals(
            chord_timeline, melody_contour, original_audio_duration_sec,
            output_path, original_audio_path
        ))
        return result
    finally:
        synthesizer.cleanup()


def synthesize_stable_chord_vocals_sync(chord_timeline: List[Tuple[str, float, float]],
                                       original_audio_duration_sec: float,
                                       output_path: str,
                                       original_audio_path: str,
                                       model_name: str = "tts_models/en/ljspeech/tacotron2-DDC",
                                       vocoder_name: str = "vocoder_models/en/ljspeech/hifigan_v2") -> str:
    """
    Synchronous wrapper for synthesize_stable_chord_vocals.
    
    Args:
        chord_timeline: List of (chord_name, start_time, end_time)
        original_audio_duration_sec: Duration of original audio
        output_path: Output file path
        original_audio_path: Original audio file path
        model_name: Coqui TTS model to use
        vocoder_name: Vocoder model to use
        
    Returns:
        Path to generated audio file
    """
    synthesizer = AdvancedVocalSynthesizer(
        model_name=model_name,
        vocoder_name=vocoder_name
    )
    
    try:
        # Run the async function
        result = asyncio.run(synthesizer.synthesize_stable_chord_vocals(
            chord_timeline, original_audio_duration_sec,
            output_path, original_audio_path
        ))
        return result
    finally:
        synthesizer.cleanup()
