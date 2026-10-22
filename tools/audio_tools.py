import os
import math
import numpy as np
from scipy.io import wavfile

def generate_click_track(bpm: int = 120, time_signature: str = "4/4", duration_minutes: float = 3.0, output_path: str = "output/metronome.wav") -> str:
    """
    Generates a custom metronome/click track WAV audio file.
    
    :param bpm: Beats per minute (e.g., 120).
    :param time_signature: Time signature formula ("4/4", "3/4", "6/8").
    :param duration_minutes: Total click duration in minutes.
    :param output_path: Output file destination path.
    :return: Success or error message.
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        sample_rate = 44100
        
        # Parse beats per measure
        parts = time_signature.split('/')
        beats_per_measure = int(parts[0]) if len(parts) > 0 else 4
        
        # Total duration and beat intervals
        beat_interval = 60.0 / float(bpm)
        total_seconds = float(duration_minutes) * 60.0
        total_beats = int(total_seconds / beat_interval)
        
        # Beep duration (100ms)
        beep_duration = 0.1
        t_beep = np.linspace(0, beep_duration, int(sample_rate * beep_duration), False)
        
        # Frequencies: High pitch on beat 1 (downbeat), Medium pitch on remaining beats
        strong_beep = 0.5 * np.sin(2 * np.pi * 1200 * t_beep)  # 1200Hz
        weak_beep = 0.3 * np.sin(2 * np.pi * 800 * t_beep)     # 800Hz
        
        # Smoothing envelope (Fast fade-out to prevent clipping pops)
        envelope = np.exp(-t_beep * 30)
        strong_beep = (strong_beep * envelope * 32767).astype(np.int16)
        weak_beep = (weak_beep * envelope * 32767).astype(np.int16)
        
        # Total audio sample buffer
        total_samples = int(sample_rate * total_seconds)
        audio_buffer = np.zeros(total_samples, dtype=np.int16)
        
        for idx in range(total_beats):
            sample_position = int(idx * beat_interval * sample_rate)
            is_downbeat = (idx % beats_per_measure == 0)
            current_beep = strong_beep if is_downbeat else weak_beep
            
            end_position = sample_position + len(current_beep)
            if end_position < total_samples:
                audio_buffer[sample_position:end_position] = current_beep

        wavfile.write(output_path, sample_rate, audio_buffer)
        return f"Success! Click track ({bpm} BPM, {time_signature}) generated at: '{output_path}'"
        
    except Exception as e:
        return f"Error generating click track: {str(e)}"

# =========================================================================
# BACKWARD COMPATIBILITY ALIAS
# =========================================================================
def gerar_click_track(bpm: int = 120, formula: str = "4/4", duracao_minutos: float = 3.0, caminho_saida: str = "output/metronomo.wav") -> str:
    return generate_click_track(bpm=bpm, time_signature=formula, duration_minutes=duracao_minutos, output_path=caminho_saida)