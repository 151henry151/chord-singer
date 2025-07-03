"""
Melody extraction module for extracting melodic content from audio using librosa's pyin algorithm.
"""

import numpy as np
import librosa
from typing import List, Tuple, Optional
import warnings


class MelodyExtractor:
    """
    A class for extracting melody from audio files using fundamental frequency estimation.
    """
    
    def __init__(self, 
                 fmin: float = None, 
                 fmax: float = None,
                 sr: int = 22050,
                 frame_length: int = 2048,
                 hop_length: int = 512,
                 fill_na: Optional[float] = None):
        """
        Initialize the melody extractor.
        
        Args:
            fmin: Minimum frequency in Hz (default: C2 ~ 65.41 Hz)
            fmax: Maximum frequency in Hz (default: C7 ~ 2093.00 Hz)
            sr: Target sample rate for processing
            frame_length: Length of each frame for analysis
            hop_length: Number of samples between frames
            fill_na: Value to fill unvoiced segments (None for no filling)
        """
        # Set default frequency range for human voice/melody
        self.fmin = fmin if fmin is not None else librosa.note_to_hz('C2')  # ~65.41 Hz
        self.fmax = fmax if fmax is not None else librosa.note_to_hz('C7')  # ~2093.00 Hz
        
        self.sr = sr
        self.frame_length = frame_length
        self.hop_length = hop_length
        self.fill_na = fill_na
        
        # Suppress warnings for better user experience
        warnings.filterwarnings('ignore', category=UserWarning, module='librosa')
    
    def extract_melody(self, audio_file_path: str) -> List[Tuple[float, float]]:
        """
        Extract melody from audio file using fundamental frequency estimation.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            List of (timestamp_sec, frequency_hz) tuples for voiced segments
        """
        try:
            # Load audio file
            audio, sr = librosa.load(audio_file_path, sr=self.sr)
            
            # Extract fundamental frequency using pyin
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y=audio,
                fmin=self.fmin,
                fmax=self.fmax,
                sr=self.sr,
                frame_length=self.frame_length,
                hop_length=self.hop_length,
                fill_na=self.fill_na
            )
            
            # Convert frame indices to timestamps
            timestamps = librosa.frames_to_time(
                np.arange(len(f0)), 
                sr=self.sr, 
                hop_length=self.hop_length
            )
            
            # Filter for voiced segments and create result
            melody_data = []
            for i, (timestamp, freq, is_voiced) in enumerate(zip(timestamps, f0, voiced_flag)):
                if is_voiced and not np.isnan(freq) and freq > 0:
                    melody_data.append((float(timestamp), float(freq)))
            
            return melody_data
            
        except Exception as e:
            print(f"Error extracting melody from {audio_file_path}: {e}")
            return []
    
    def extract_melody_from_array(self, audio: np.ndarray, sr: int) -> List[Tuple[float, float]]:
        """
        Extract melody from audio array.
        
        Args:
            audio: Audio signal array
            sr: Sample rate of the audio
            
        Returns:
            List of (timestamp_sec, frequency_hz) tuples for voiced segments
        """
        try:
            # Resample if necessary
            if sr != self.sr:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sr)
                sr = self.sr
            
            # Extract fundamental frequency using pyin
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y=audio,
                fmin=self.fmin,
                fmax=self.fmax,
                sr=self.sr,
                frame_length=self.frame_length,
                hop_length=self.hop_length,
                fill_na=self.fill_na
            )
            
            # Convert frame indices to timestamps
            timestamps = librosa.frames_to_time(
                np.arange(len(f0)), 
                sr=self.sr, 
                hop_length=self.hop_length
            )
            
            # Filter for voiced segments and create result
            melody_data = []
            for i, (timestamp, freq, is_voiced) in enumerate(zip(timestamps, f0, voiced_flag)):
                if is_voiced and not np.isnan(freq) and freq > 0:
                    melody_data.append((float(timestamp), float(freq)))
            
            return melody_data
            
        except Exception as e:
            print(f"Error extracting melody from audio array: {e}")
            return []
    
    def get_melody_notes(self, melody_data: List[Tuple[float, float]]) -> List[Tuple[float, str]]:
        """
        Convert frequency data to note names.
        
        Args:
            melody_data: List of (timestamp_sec, frequency_hz) tuples
            
        Returns:
            List of (timestamp_sec, note_name) tuples
        """
        notes = []
        for timestamp, freq in melody_data:
            if freq > 0:
                note_name = librosa.hz_to_note(freq)
                notes.append((timestamp, note_name))
        
        return notes
    
    def get_melody_statistics(self, melody_data: List[Tuple[float, float]]) -> dict:
        """
        Get statistics about the extracted melody.
        
        Args:
            melody_data: List of (timestamp_sec, frequency_hz) tuples
            
        Returns:
            Dictionary with melody statistics
        """
        if not melody_data:
            return {
                'total_frames': 0,
                'voiced_frames': 0,
                'min_frequency': 0,
                'max_frequency': 0,
                'mean_frequency': 0,
                'duration': 0
            }
        
        frequencies = [freq for _, freq in melody_data]
        timestamps = [time for time, _ in melody_data]
        
        return {
            'total_frames': len(melody_data),
            'voiced_frames': len(melody_data),
            'min_frequency': float(np.min(frequencies)),
            'max_frequency': float(np.max(frequencies)),
            'mean_frequency': float(np.mean(frequencies)),
            'duration': float(timestamps[-1] - timestamps[0]) if len(timestamps) > 1 else 0
        }
    
    def filter_melody_by_confidence(self, 
                                  melody_data: List[Tuple[float, float]], 
                                  voiced_probs: np.ndarray,
                                  confidence_threshold: float = 0.5) -> List[Tuple[float, float]]:
        """
        Filter melody data by confidence threshold.
        
        Args:
            melody_data: List of (timestamp_sec, frequency_hz) tuples
            voiced_probs: Array of voiced probabilities from pyin
            confidence_threshold: Minimum confidence threshold (0.0 to 1.0)
            
        Returns:
            Filtered list of (timestamp_sec, frequency_hz) tuples
        """
        if len(melody_data) != len(voiced_probs):
            return melody_data
        
        filtered_data = []
        for i, (timestamp, freq) in enumerate(melody_data):
            if voiced_probs[i] >= confidence_threshold:
                filtered_data.append((timestamp, freq))
        
        return filtered_data
    
    def get_melody_segments(self, 
                          melody_data: List[Tuple[float, float]], 
                          min_segment_duration: float = 0.1) -> List[List[Tuple[float, float]]]:
        """
        Group melody data into continuous segments.
        
        Args:
            melody_data: List of (timestamp_sec, frequency_hz) tuples
            min_segment_duration: Minimum duration for a segment in seconds
            
        Returns:
            List of melody segments
        """
        if not melody_data:
            return []
        
        segments = []
        current_segment = [melody_data[0]]
        
        for i in range(1, len(melody_data)):
            current_time, _ = melody_data[i]
            prev_time, _ = melody_data[i-1]
            
            # If gap is too large, start new segment
            if current_time - prev_time > 0.1:  # 100ms gap threshold
                if len(current_segment) > 0:
                    segment_duration = current_segment[-1][0] - current_segment[0][0]
                    if segment_duration >= min_segment_duration:
                        segments.append(current_segment)
                current_segment = [melody_data[i]]
            else:
                current_segment.append(melody_data[i])
        
        # Add final segment
        if len(current_segment) > 0:
            segment_duration = current_segment[-1][0] - current_segment[0][0]
            if segment_duration >= min_segment_duration:
                segments.append(current_segment)
        
        return segments 