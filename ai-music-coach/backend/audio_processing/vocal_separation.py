"""
Vocal separation module using Spleeter CLI to separate vocals from instrumental tracks.
"""

import os
import tempfile
import subprocess
from typing import Tuple

class VocalSeparator:
    """
    A class for separating vocals from instrumental tracks using the Spleeter CLI.
    """
    def __init__(self):
        pass

    def separate_vocals(self, audio_file_path: str) -> Tuple[str, str]:
        """
        Separate vocals from instrumental in an audio file using the Spleeter CLI.
        Args:
            audio_file_path: Path to the input audio file
        Returns:
            Tuple of (instrumental_path, vocals_path) - paths to separated audio files
        """
        try:
            print(f"Separating vocals from: {audio_file_path} (using Spleeter CLI)")
            # Create a temporary directory for Spleeter output
            temp_dir = tempfile.mkdtemp()
            # Run Spleeter CLI
            cmd = [
                "spleeter", "separate",
                "-p", "spleeter:2stems",
                "-o", temp_dir,
                audio_file_path
            ]
            print(f"Running command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            # Spleeter outputs to temp_dir/<basename>/accompaniment.wav and vocals.wav
            base_name = os.path.splitext(os.path.basename(audio_file_path))[0]
            output_folder = os.path.join(temp_dir, base_name)
            instrumental_path = os.path.join(output_folder, "accompaniment.wav")
            vocals_path = os.path.join(output_folder, "vocals.wav")
            if not os.path.exists(instrumental_path):
                raise FileNotFoundError(f"Instrumental file not found: {instrumental_path}")
            if not os.path.exists(vocals_path):
                raise FileNotFoundError(f"Vocals file not found: {vocals_path}")
            print(f"Separation complete. Instrumental: {instrumental_path}, Vocals: {vocals_path}")
            return instrumental_path, vocals_path
        except Exception as e:
            print(f"Error in vocal separation: {e}")
            import traceback
            traceback.print_exc()
            # Return original file as fallback
            return audio_file_path, None

    def get_instrumental_only(self, audio_file_path: str) -> str:
        instrumental_path, _ = self.separate_vocals(audio_file_path)
        return instrumental_path

    def cleanup(self):
        pass 