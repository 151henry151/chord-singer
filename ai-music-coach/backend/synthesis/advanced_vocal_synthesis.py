"""
Advanced vocal synthesis module for generating natural-sounding sung chord names.
Uses multiple TTS engines with singing-specific enhancements.
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

# TTS Engines
import pyttsx3
import edge_tts
from gtts import gTTS

# For better audio processing
from scipy import signal
import random


class AdvancedVocalSynthesizer:
    """
    Advanced vocal synthesizer using multiple TTS engines with singing enhancements.
    Produces much more natural-sounding vocals compared to basic pyttsx3.
    """
    
    def __init__(self, 
                 tts_engine: str = "edge-tts",
                 voice_name: str = "en-US-JennyNeural",
                 rate: float = 0.9,
                 volume: float = 0.9):
        """
        Initialize the advanced vocal synthesizer.
        
        Args:
            tts_engine: TTS engine to use ("edge-tts", "gtts", "pyttsx3")
            voice_name: Voice name for edge-tts (e.g., "en-US-JennyNeural")
            rate: Speech rate (0.5-2.0 for edge-tts, words/min for pyttsx3)
            volume: Volume level (0.0-1.0)
        """
        self.tts_engine = tts_engine
        self.voice_name = voice_name
        self.rate = rate
        self.volume = volume
        
        # Initialize the selected TTS engine
        if tts_engine == "pyttsx3":
            self._init_pyttsx3()
        elif tts_engine == "edge-tts":
            self._init_edge_tts()
        elif tts_engine == "gtts":
            self._init_gtts()
        else:
            raise ValueError(f"Unsupported TTS engine: {tts_engine}")
        
        print(f"✓ Advanced VocalSynthesizer initialized with {tts_engine}")
        print(f"  Voice: {voice_name}")
        print(f"  Rate: {rate}")
        print(f"  Volume: {volume}")
    
    def _init_pyttsx3(self):
        """Initialize pyttsx3 engine."""
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', int(self.rate * 200))  # Convert to words/min
        self.engine.setProperty('volume', self.volume)
        
        # Get available voices and set to a clear voice
        voices = self.engine.getProperty('voices')
        if voices:
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            else:
                self.engine.setProperty('voice', voices[0].id)
    
    def _init_edge_tts(self):
        """Initialize edge-tts engine."""
        # Edge-TTS is async, so we'll handle it in the synthesis methods
        pass
    
    def _init_gtts(self):
        """Initialize gTTS engine."""
        # gTTS is stateless, so no initialization needed
        pass
    
    async def synthesize_sung_chord_vocals(self, 
                                          chord_timeline: List[Tuple[str, float, float]],
                                          melody_contour: List[Tuple[float, float]],
                                          original_audio_duration_sec: float,
                                          output_path: str,
                                          original_audio_path: str) -> str:
        """
        Synthesize sung chord vocals with advanced TTS and singing enhancements.
        
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
        print(f"   TTS Engine: {self.tts_engine}")
        print(f"   Voice: {self.voice_name}")
        
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
                # Generate audio with the selected TTS engine
                if self.tts_engine == "edge-tts":
                    chord_audio = await self._synthesize_with_edge_tts(enhanced_chord_name)
                elif self.tts_engine == "gtts":
                    chord_audio = await self._synthesize_with_gtts(enhanced_chord_name)
                else:  # pyttsx3
                    chord_audio = self._synthesize_with_pyttsx3(enhanced_chord_name)
                
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
    
    async def _synthesize_with_edge_tts(self, text: str) -> AudioSegment:
        """Synthesize text using edge-tts (highest quality)."""
        try:
            # Fix rate format for edge-tts (should be like "+10%" or "-10%")
            rate_str = f"{int((self.rate - 1.0) * 100):+d}%"
            communicate = edge_tts.Communicate(text, self.voice_name, rate=rate_str)
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            await communicate.save(temp_path)
            
            # Load the generated audio
            audio = AudioSegment.from_wav(temp_path)
            
            # Clean up
            os.unlink(temp_path)
            
            return audio
            
        except Exception as e:
            print(f"Edge-TTS error: {e}")
            # Fallback to pyttsx3
            return self._synthesize_with_pyttsx3(text)
    
    async def _synthesize_with_gtts(self, text: str) -> AudioSegment:
        """Synthesize text using gTTS (Google TTS)."""
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name
            
            tts.save(temp_path)
            
            # Load the generated audio
            audio = AudioSegment.from_mp3(temp_path)
            
            # Clean up
            os.unlink(temp_path)
            
            return audio
            
        except Exception as e:
            print(f"gTTS error: {e}")
            # Fallback to pyttsx3
            return self._synthesize_with_pyttsx3(text)
    
    def _synthesize_with_pyttsx3(self, text: str) -> AudioSegment:
        """Synthesize text using pyttsx3 (fallback)."""
        try:
            # Make sure engine is initialized
            if not hasattr(self, 'engine') or self.engine is None:
                self._init_pyttsx3()
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            self.engine.save_to_file(text, temp_path)
            self.engine.runAndWait()
            
            # Load the generated audio
            audio = AudioSegment.from_wav(temp_path)
            
            # Clean up
            os.unlink(temp_path)
            
            return audio
            
        except Exception as e:
            print(f"pyttsx3 error: {e}")
            # Return silence as last resort
            return AudioSegment.silent(duration=1000)
    
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
        This fixes the extreme octave jumps and chipmunk effect.
        """
        if not melody_points or len(samples) < 2:
            return samples
        
        # Calculate average pitch for the segment
        valid_freqs = [f for _, f in melody_points if f > 0]
        if not valid_freqs:
            return samples
        
        target_pitch = np.mean(valid_freqs)
        
        # FIXED: Implement proper pitch range clamping for TTS
        # Human vocal range is roughly 80-400 Hz for comfortable speaking/singing
        MIN_VOCAL_PITCH = 80.0   # Hz (roughly E2)
        MAX_VOCAL_PITCH = 400.0  # Hz (roughly G4)
        
        # Normalize the target pitch to stay within vocal range
        normalized_pitch = self._normalize_to_vocal_octave(target_pitch)
        
        # Clamp to reasonable vocal range
        normalized_pitch = max(MIN_VOCAL_PITCH, min(MAX_VOCAL_PITCH, normalized_pitch))
        
        # Estimate original TTS pitch (typical speaking pitch around 220 Hz)
        original_pitch = 220.0
        
        # Calculate pitch shift factor (much more conservative now)
        pitch_factor = normalized_pitch / original_pitch
        
        # FIXED: Use much more conservative pitch shift limits
        # Instead of 0.5-2.0 (which allows 2 octaves), use 0.8-1.5 (about 1 octave)
        pitch_factor = max(0.8, min(1.5, pitch_factor))
        
        print(f"   🎵 Pitch mapping: {original_pitch:.1f} Hz → {normalized_pitch:.1f} Hz (factor: {pitch_factor:.2f})")
        print(f"   🎵 Original melody pitch: {target_pitch:.1f} Hz (normalized to vocal range)")
        
        # Apply pitch shift using resampling
        new_length = int(len(samples) / pitch_factor)
        if new_length > 1:  # Ensure we have at least 2 samples
            shifted = resample(samples, new_length)
        else:
            shifted = samples
        
        return shifted
    
    def _normalize_to_vocal_octave(self, frequency: float) -> float:
        """
        Normalize musical frequency to comfortable vocal range (4th octave).
        This prevents extreme octave jumps.
        """
        # Target vocal range: C4 (261.63 Hz) to C5 (523.25 Hz)
        TARGET_MIN = 200.0  # Hz (below C4)
        TARGET_MAX = 500.0  # Hz (above C5)
        
        # Transpose to comfortable vocal range
        while frequency < TARGET_MIN:
            frequency *= 2.0  # Go up an octave
        while frequency > TARGET_MAX:
            frequency /= 2.0  # Go down an octave
        
        return frequency
    
    def _smooth_pitch_transition(self, current_pitch: float, target_pitch: float, smoothing_factor: float = 0.3) -> float:
        """
        Smooth pitch transitions to prevent sudden jumps.
        """
        return current_pitch + (target_pitch - current_pitch) * smoothing_factor
    
    def _apply_singing_effects(self, samples: np.ndarray, sr: int) -> np.ndarray:
        """Apply singing-specific audio effects."""
        if len(samples) < 2:
            return samples
            
        # 1. Add slight vibrato for more natural singing
        vibrato_rate = 5.0  # Hz
        vibrato_depth = 0.02  # 2% pitch modulation
        
        t = np.arange(len(samples)) / sr
        vibrato = np.sin(2 * np.pi * vibrato_rate * t) * vibrato_depth
        
        # Apply vibrato using phase modulation
        phase = np.cumsum(vibrato)
        samples = samples * np.cos(phase) + np.roll(samples, 1) * np.sin(phase)
        
        # 2. Add subtle reverb for more natural sound
        # Simple convolution with a short impulse response
        reverb_length = int(0.1 * sr)  # 100ms reverb
        if reverb_length > 0:
            reverb_ir = np.exp(-np.arange(reverb_length) / (0.05 * sr))
            reverb_ir = reverb_ir / np.sum(reverb_ir)
            
            samples = np.convolve(samples, reverb_ir, mode='same')
        
        # 3. Apply gentle compression to even out dynamics
        threshold = 0.7
        ratio = 3.0
        
        # Simple soft-knee compression
        gain_reduction = np.where(
            np.abs(samples) > threshold,
            (np.abs(samples) - threshold) * (1 - 1/ratio),
            0
        )
        samples = samples * (1 - gain_reduction)
        
        # 4. Add subtle breathiness (high-frequency noise)
        breath_noise = np.random.normal(0, 0.01, len(samples))
        try:
            breath_filter = signal.butter(4, 0.3, btype='high')[0]
            breath_noise = signal.filtfilt(breath_filter[0], breath_filter[1], breath_noise)
            samples = samples + breath_noise
        except:
            # If filtering fails, just add the noise
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
        
        # Elongate vowels for singing effect (but more subtly than before)
        enhanced = re.sub(r'([AEIOU])', r'\1\1', enhanced)  # Double vowels instead of triple
        
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
        """Get list of available voices for the current TTS engine."""
        if self.tts_engine == "edge-tts":
            try:
                # Use a new event loop for edge-tts
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                voices = loop.run_until_complete(edge_tts.list_voices())
                loop.close()
                
                return [
                    {
                        'id': voice['ShortName'],
                        'name': f"{voice['ShortName']} ({voice['Gender']})",
                        'language': voice['Locale'],
                        'gender': voice['Gender']
                    }
                    for voice in voices
                ]
            except Exception as e:
                print(f"Error getting edge-tts voices: {e}")
                return []
        elif self.tts_engine == "pyttsx3":
            try:
                if not hasattr(self, 'engine') or self.engine is None:
                    self._init_pyttsx3()
                voices = self.engine.getProperty('voices')
                return [{'id': voice.id, 'name': voice.name} for voice in voices]
            except Exception as e:
                print(f"Error getting pyttsx3 voices: {e}")
                return []
        else:
            return []
    
    def set_voice_properties(self, rate: float = None, volume: float = None, voice_name: str = None):
        """Update voice properties."""
        if rate is not None:
            self.rate = rate
        if volume is not None:
            self.volume = volume
        if voice_name is not None:
            self.voice_name = voice_name
        
        # Update the engine if it's pyttsx3
        if self.tts_engine == "pyttsx3" and hasattr(self, 'engine') and self.engine is not None:
            self.engine.setProperty('rate', int(self.rate * 200))
            self.engine.setProperty('volume', self.volume)
    
    def cleanup(self):
        """Clean up resources."""
        if self.tts_engine == "pyttsx3" and hasattr(self, 'engine'):
            self.engine = None
    
    async def synthesize_stable_chord_vocals(self, 
                                           chord_timeline: List[Tuple[str, float, float]],
                                           original_audio_duration_sec: float,
                                           output_path: str,
                                           original_audio_path: str) -> str:
        """
        Synthesize chord vocals WITHOUT pitch mapping - stable, clear voice for learning.
        This is much more usable than trying to follow the melody.
        
        Args:
            chord_timeline: List of (chord_name, start_time, end_time)
            original_audio_duration_sec: Total duration of the original audio
            output_path: Path where the output audio will be saved
            original_audio_path: Path to the original audio file for instrumental track
            
        Returns:
            Path to the generated audio file
        """
        print(f"🎵 Synthesizing STABLE vocals for {len(chord_timeline)} chords (no pitch mapping)")
        print(f"   TTS Engine: {self.tts_engine}")
        print(f"   Voice: {self.voice_name}")
        print(f"   Note: Using stable pitch for clear chord name pronunciation")
        
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
            
            # Enhance chord name for singing (but keep it simple)
            enhanced_chord_name = self._enhance_for_singing_simple(chord_name)
            print(f"   Enhanced text: '{enhanced_chord_name}'")
            
            try:
                # Generate audio with the selected TTS engine (no pitch mapping)
                if self.tts_engine == "edge-tts":
                    chord_audio = await self._synthesize_with_edge_tts(enhanced_chord_name)
                elif self.tts_engine == "gtts":
                    chord_audio = await self._synthesize_with_gtts(enhanced_chord_name)
                else:  # pyttsx3
                    chord_audio = self._synthesize_with_pyttsx3(enhanced_chord_name)
                
                # Apply only basic singing enhancements (no pitch mapping)
                chord_audio = self._apply_basic_singing_enhancements(chord_audio, chord_duration_ms)
                
                # Overlay at the correct position
                vocals_track = vocals_track.overlay(
                    chord_audio, position=int(start_time * 1000)
                )
                
                print(f"   ✓ Generated {len(chord_audio)} ms of stable audio")
                
            except Exception as e:
                print(f"   ✗ Error generating audio for '{chord_name}': {e}")
                continue
        
        # Mix instrumental and vocals with better balance
        instrumental_track = instrumental_track - 8  # Reduce instrumental volume
        vocals_track = vocals_track + 3  # Boost vocals slightly
        
        combined_audio = instrumental_track.overlay(vocals_track)
        
        # Export the final audio
        combined_audio.export(output_path, format='wav')
        print(f"🎵 Successfully exported stable vocals to: {output_path}")
        
        return output_path
    
    def _enhance_for_singing_simple(self, chord_name: str) -> str:
        """
        Simple enhancement for chord names - clear and understandable.
        """
        # Convert to uppercase for consistency
        enhanced = chord_name.upper()
        
        # Add clear spacing between syllables
        enhanced = enhanced.replace(' ', ' ... ')
        
        # Simple vowel elongation (not as extreme)
        enhanced = re.sub(r'([AEIOU])', r'\1', enhanced)  # Single vowels for clarity
        
        # Clear pronunciation for common chord types
        enhanced = enhanced.replace('MAJOR', 'MAY-JOR')
        enhanced = enhanced.replace('MINOR', 'MIN-OR')
        enhanced = enhanced.replace('SEVEN', 'SEV-EN')
        enhanced = enhanced.replace('NINE', 'NINE')
        enhanced = enhanced.replace('ELEVEN', 'ELEV-EN')
        enhanced = enhanced.replace('THIRTEEN', 'THIR-TEEN')
        
        # Add clear pauses
        enhanced = enhanced.replace('-', ' ... ')
        
        return enhanced
    
    def _apply_basic_singing_enhancements(self, audio: AudioSegment, duration_ms: int) -> AudioSegment:
        """
        Apply only basic singing enhancements without pitch mapping.
        """
        # Convert to numpy array for processing
        samples = np.array(audio.get_array_of_samples()).astype(np.float32)
        sr = audio.frame_rate
        
        # Apply only subtle effects (no pitch mapping)
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
        """Apply only subtle singing effects (no pitch manipulation)."""
        if len(samples) < 2:
            return samples
            
        # 1. Very subtle vibrato for naturalness
        vibrato_rate = 3.0  # Hz (slower)
        vibrato_depth = 0.01  # 1% pitch modulation (very subtle)
        
        t = np.arange(len(samples)) / sr
        vibrato = np.sin(2 * np.pi * vibrato_rate * t) * vibrato_depth
        
        # Apply vibrato using phase modulation
        phase = np.cumsum(vibrato)
        samples = samples * np.cos(phase) + np.roll(samples, 1) * np.sin(phase)
        
        # 2. Very subtle reverb
        reverb_length = int(0.05 * sr)  # 50ms reverb (shorter)
        if reverb_length > 0:
            reverb_ir = np.exp(-np.arange(reverb_length) / (0.025 * sr))
            reverb_ir = reverb_ir / np.sum(reverb_ir)
            
            samples = np.convolve(samples, reverb_ir, mode='same')
        
        # 3. Gentle compression
        threshold = 0.8
        ratio = 2.0
        
        gain_reduction = np.where(
            np.abs(samples) > threshold,
            (np.abs(samples) - threshold) * (1 - 1/ratio),
            0
        )
        samples = samples * (1 - gain_reduction)
        
        return samples


# Convenience function for non-async usage
def synthesize_sung_chord_vocals_sync(chord_timeline: List[Tuple[str, float, float]],
                                     melody_contour: List[Tuple[float, float]],
                                     original_audio_duration_sec: float,
                                     output_path: str,
                                     original_audio_path: str,
                                     tts_engine: str = "edge-tts",
                                     voice_name: str = "en-US-JennyNeural") -> str:
    """
    Synchronous wrapper for synthesize_sung_chord_vocals.
    
    Args:
        chord_timeline: List of (chord_name, start_time, end_time)
        melody_contour: List of (timestamp_sec, frequency_hz)
        original_audio_duration_sec: Total duration of the original audio
        output_path: Path where the output audio will be saved
        original_audio_path: Path to the original audio file
        tts_engine: TTS engine to use
        voice_name: Voice name for edge-tts
        
    Returns:
        Path to the generated audio file
    """
    synthesizer = AdvancedVocalSynthesizer(tts_engine=tts_engine, voice_name=voice_name)
    
    try:
        # Use a new event loop for the async call
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(synthesizer.synthesize_sung_chord_vocals(
            chord_timeline, melody_contour, original_audio_duration_sec, 
            output_path, original_audio_path
        ))
        loop.close()
        return result
    finally:
        synthesizer.cleanup()


# Convenience function for stable vocals (no pitch mapping)
def synthesize_stable_chord_vocals_sync(chord_timeline: List[Tuple[str, float, float]],
                                       original_audio_duration_sec: float,
                                       output_path: str,
                                       original_audio_path: str,
                                       tts_engine: str = "edge-tts",
                                       voice_name: str = "en-US-JennyNeural") -> str:
    """
    Synchronous wrapper for synthesize_stable_chord_vocals (no pitch mapping).
    This produces stable, clear vocals perfect for learning chord progressions.
    
    Args:
        chord_timeline: List of (chord_name, start_time, end_time)
        original_audio_duration_sec: Total duration of the original audio
        output_path: Path where the output audio will be saved
        original_audio_path: Path to the original audio file
        tts_engine: TTS engine to use
        voice_name: Voice name for edge-tts
        
    Returns:
        Path to the generated audio file
    """
    synthesizer = AdvancedVocalSynthesizer(tts_engine=tts_engine, voice_name=voice_name)
    
    try:
        # Use a new event loop for the async call
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(synthesizer.synthesize_stable_chord_vocals(
            chord_timeline, original_audio_duration_sec, 
            output_path, original_audio_path
        ))
        loop.close()
        return result
    finally:
        synthesizer.cleanup()
