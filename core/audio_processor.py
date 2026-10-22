import os
import subprocess
import warnings
from typing import Union
import librosa
import numpy as np
import soundfile as sf

warnings.filterwarnings("ignore", category=FutureWarning)

class AudioProcessor:
    @staticmethod
    def _convert_to_seconds(time_val: Union[str, float, int]) -> float:
        """Converts 'MM:SS', 'HH:MM:SS', numeric strings, or floats/ints into seconds (float)."""
        if isinstance(time_val, (int, float)):
            return float(time_val)

        if isinstance(time_val, str):
            time_val = time_val.strip()
            if ":" in time_val:
                parts = time_val.split(":")
                try:
                    if len(parts) == 2:  # MM:SS
                        return float(parts[0]) * 60 + float(parts[1])
                    elif len(parts) == 3:  # HH:MM:SS
                        return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                except ValueError:
                    return 0.0
            try:
                return float(time_val)
            except ValueError:
                return 0.0

        return 0.0

    @staticmethod
    def normalize_audio(input_path: str, output_path: str = "output/normalized_output.wav", target_db: Union[float, str] = -1.0) -> str:
        """Adjusts audio gain so peak level reaches specified dBFS (prevents clipping/distortion)."""
        if not os.path.exists(input_path):
            return f"Error: File '{input_path}' was not found."

        try:
            target_db_val = float(target_db)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            y, sr = librosa.load(input_path, sr=None)

            max_peak = np.max(np.abs(y))
            if max_peak == 0:
                return "Error: The audio file is completely silent."

            target_linear = 10 ** (target_db_val / 20.0)
            gain_factor = target_linear / max_peak
            y_normalized = y * gain_factor

            sf.write(output_path, y_normalized, sr)
            return f"Success! Audio normalized to {target_db_val} dBFS. Saved at '{output_path}'."
        except Exception as e:
            return f"Error normalizing audio: {str(e)}"

    @staticmethod
    def trim_audio(input_path: str, start_sec: Union[float, str], end_sec: Union[float, str], output_path: str = "output/trimmed_output.wav") -> str:
        """Trims a section of audio given start and end time in seconds or MM:SS format."""
        if not os.path.exists(input_path):
            return f"Error: File '{input_path}' was not found."

        start = AudioProcessor._convert_to_seconds(start_sec)
        end = AudioProcessor._convert_to_seconds(end_sec)

        if start < 0 or end <= start:
            return f"Error: Invalid trim parameters ({start_sec} to {end_sec}). End time must be greater than start time."

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            duration = end - start
            y, sr = librosa.load(input_path, sr=None, offset=start, duration=duration)

            sf.write(output_path, y, sr)
            return f"Success! Segment from {start_sec} ({start}s) to {end_sec} ({end}s) trimmed successfully. Saved at '{output_path}'."
        except Exception as e:
            return f"Error trimming audio: {str(e)}"

    @staticmethod
    def detect_key_and_bpm(input_path: str) -> str:
        """Estimates BPM and Tonality (Key) using Chromagram and Krumhansl-Schmuckler profiles."""
        if not os.path.exists(input_path):
            return f"Error: File '{input_path}' was not found."

        try:
            y, sr = librosa.load(input_path, sr=None, offset=15.0, duration=60.0)

            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm = float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)

            y_harmonic, _ = librosa.effects.hpss(y)
            chroma = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)
            chroma_avg = np.mean(chroma, axis=1)

            notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            major_profile = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
            minor_profile = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 2.69, 3.34, 3.17, 3.28]

            best_corr = -1
            detected_key = "Unknown"

            for i in range(12):
                chroma_rot = np.roll(chroma_avg, -i)
                corr_major = np.corrcoef(chroma_rot, major_profile)[0, 1]
                corr_minor = np.corrcoef(chroma_rot, minor_profile)[0, 1]

                if corr_major > best_corr:
                    best_corr = corr_major
                    detected_key = f"{notes[i]} Major"

                if corr_minor > best_corr:
                    best_corr = corr_minor
                    detected_key = f"{notes[i]} minor"

            return f"Analysis complete: Estimated Key: {detected_key} | Tempo: {round(bpm)} BPM."

        except Exception as e:
            return f"Error analyzing audio: {str(e)}"

    @staticmethod
    def change_pitch(input_path: str, semitones: Union[float, str], output_path: str = "output/transposed_output.wav") -> str:
        """Alters audio pitch by semitones without changing tempo."""
        if not os.path.exists(input_path):
            return f"Error: File '{input_path}' was not found."

        try:
            semitones_val = float(semitones)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            y, sr = librosa.load(input_path, sr=None)
            y_shifted = librosa.effects.pitch_shift(y=y, sr=sr, n_steps=semitones_val)
            sf.write(output_path, y_shifted, sr)
            return f"Success! Audio transposed by {semitones_val} semitone(s) and saved at '{output_path}'."
        except Exception as e:
            return f"Error changing audio pitch: {str(e)}"

    @staticmethod
    def change_speed(input_path: str, speed_factor: Union[float, str], output_path: str = "output/speed_output.wav") -> str:
        """Alters audio playback speed (time stretch) without changing pitch."""
        if not os.path.exists(input_path):
            return f"Error: File '{input_path}' was not found."

        try:
            speed_val = float(speed_factor)
            if speed_val <= 0:
                return "Error: Speed factor must be greater than zero."

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            y, sr = librosa.load(input_path, sr=None)
            y_stretched = librosa.effects.time_stretch(y=y, rate=speed_val)
            sf.write(output_path, y_stretched, sr)
            
            percentage = int((speed_val - 1.0) * 100)
            status_str = f"{abs(percentage)}% faster" if percentage >= 0 else f"{abs(percentage)}% slower"
            return f"Success! Speed changed by {speed_val}x ({status_str}). Saved at '{output_path}'."
        except Exception as e:
            return f"Error changing audio speed: {str(e)}"

    @staticmethod
    def separate_stems(input_path: str, mode: str = "playback") -> str:
        """Separates audio stems and instruments using Demucs."""
        if not os.path.exists(input_path):
            return f"Error: File '{input_path}' was not found."

        output_folder = "output/stems"
        os.makedirs(output_folder, exist_ok=True)

        try:
            command = [
                "demucs",
                "-n", "htdemucs",
                "--two-stems=vocals",
                "-o", output_folder,
                input_path
            ]

            proc_result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if proc_result.returncode != 0:
                return f"Error executing Demucs:\n{proc_result.stderr}"

            base_name = os.path.splitext(os.path.basename(input_path))[0]
            result_folder = os.path.join(output_folder, "htdemucs", base_name)

            vocal_path = os.path.join(result_folder, "vocals.wav")
            playback_path = os.path.join(result_folder, "no_vocals.wav")

            if mode == "vocal" and os.path.exists(vocal_path):
                return f"Success! Isolated vocals saved at: '{vocal_path}'."
            elif mode == "playback" and os.path.exists(playback_path):
                return f"Success! Playback (no vocals) saved at: '{playback_path}'."
            elif os.path.exists(result_folder):
                return f"Success! Processed tracks saved at: '{result_folder}'."
            else:
                return f"Processing completed. Check files in directory: '{output_folder}'"

        except Exception as e:
            return f"Error executing stem separation: {str(e)}"

    # =========================================================================
    # BACKWARD COMPATIBILITY ALIASES (EVITA BREAKING CHANGES EM SCRIPTS ANTIGOS)
    # =========================================================================
    @staticmethod
    def normalizar_audio(caminho_entrada: str, caminho_saida: str = "output/normalized_output.wav", decibeis_alvo: Union[float, str] = -1.0) -> str:
        return AudioProcessor.normalize_audio(input_path=caminho_entrada, output_path=caminho_saida, target_db=decibeis_alvo)

    @staticmethod
    def cortar_audio(caminho_entrada: str, inicio_seg: Union[float, str], fim_seg: Union[float, str], caminho_saida: str = "output/trimmed_output.wav") -> str:
        return AudioProcessor.trim_audio(input_path=caminho_entrada, start_sec=inicio_seg, end_sec=fim_seg, output_path=caminho_saida)

    @staticmethod
    def detectar_tom_e_bpm(caminho_entrada: str) -> str:
        return AudioProcessor.detect_key_and_bpm(input_path=caminho_entrada)

    @staticmethod
    def mudar_tom(caminho_entrada: str, semitonos: Union[float, str], caminho_saida: str = "output/transposed_output.wav") -> str:
        return AudioProcessor.change_pitch(input_path=caminho_entrada, semitones=semitonos, output_path=caminho_saida)

    @staticmethod
    def alterar_velocidade(caminho_entrada: str, fator_frequencia: Union[float, str], caminho_saida: str = "output/speed_output.wav") -> str:
        return AudioProcessor.change_speed(input_path=caminho_entrada, speed_factor=fator_frequencia, output_path=caminho_saida)

    @staticmethod
    def separar_stems(caminho_entrada: str, modo: str = "playback") -> str:
        return AudioProcessor.separate_stems(input_path=caminho_entrada, mode=modo)