"""
Chord detection module using madmom's DeepChromaProcessor and CRFChordRecognitionProcessor.
"""

# Apply madmom patch before importing madmom
from .madmom_patch import apply_patch
apply_patch()

import numpy as np
from typing import List, Tuple
from madmom.audio.chroma import DeepChromaProcessor
from madmom.features.chords import DeepChromaChordRecognitionProcessor

class ChordDetector:
    """
    A class for detecting chords in audio files using madmom.
    """
    def __init__(self):
        """
        Initialize the chord detector with madmom processors.
        """
        self.chroma_processor = DeepChromaProcessor()
        self.chord_recognizer = DeepChromaChordRecognitionProcessor()

    def detect_chords(self, audio_file_path: str) -> List[Tuple[str, float, float]]:
        """
        Detect chords in an audio file.
        Args:
            audio_file_path: Path to the audio file
        Returns:
            List of tuples: (chord_name, start_time_sec, end_time_sec)
        """
        try:
            # Extract chroma features
            print(f"Extracting chroma features from {audio_file_path}")
            chroma = self.chroma_processor(audio_file_path)
            print(f"Chroma shape: {chroma.shape if hasattr(chroma, 'shape') else 'No shape'}")
            print(f"Chroma type: {type(chroma)}")
            
            # Get chord predictions (label, start, end)
            print("Running chord recognition...")
            chords = self.chord_recognizer(chroma)
            print(f"Detected {len(chords)} chords")
            
            # Format output
            formatted = []
            for chord_label, start, end in chords:
                formatted.append((self.format_chord_name(chord_label), float(start), float(end)))
            return formatted
            
        except Exception as e:
            print(f"Error in chord detection: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            # Return empty list as fallback
            return []

    def format_chord_name(self, madmom_chord_label: str) -> str:
        """
        Convert madmom's chord label (e.g., 'C:maj') to a more readable format (e.g., 'C major').
        Args:
            madmom_chord_label: Chord label from madmom
        Returns:
            Readable chord name
        """
        if madmom_chord_label == 'N':
            return 'No Chord'
        # Split by ':' if present
        if ':' in madmom_chord_label:
            root, quality = madmom_chord_label.split(':', 1)
            # Map common qualities
            quality_map = {
                'maj': 'major',
                'min': 'minor',
                'dim': 'diminished',
                'aug': 'augmented',
                '7': '7th',
                'maj7': 'major 7th',
                'min7': 'minor 7th',
                'sus2': 'sus2',
                'sus4': 'sus4',
                'hdim7': 'half-diminished 7th',
                'minmaj7': 'minor major 7th',
                'dim7': 'diminished 7th',
            }
            pretty_quality = quality_map.get(quality, quality)
            return f"{root} {pretty_quality}"
        return madmom_chord_label 