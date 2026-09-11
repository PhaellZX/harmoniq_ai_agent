import os
import math
import numpy as np
from scipy.io import wavfile

def gerar_click_track(bpm: int = 120, formula: str = "4/4", duracao_minutos: float = 3.0, caminho_saida: str = "output/metronomo.wav") -> str:
    """
    Gera um arquivo de áudio WAV de click track / metrônomo personalizado.
    
    :param bpm: Batidas por minuto (ex: 120).
    :param formula: Fórmula de compasso ("4/4", "3/4", "6/8").
    :param duracao_minutos: Duração total do clique em minutos.
    :param caminho_saida: Caminho para salvar o arquivo de saída.
    :return: Mensagem de sucesso ou erro.
    """
    try:
        os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
        sample_rate = 44100
        
        # Define tempos por compasso
        partes = formula.split('/')
        num_tempos = int(partes[0]) if len(partes) > 0 else 4
        
        # Duração total e intervalos
        intervalo_tempo = 60.0 / float(bpm)
        total_segundos = float(duracao_minutos) * 60.0
        total_batidas = int(total_segundos / intervalo_tempo)
        
        # Duração de cada bipe (100ms)
        duracao_bipe = 0.1
        t_bipe = np.linspace(0, duracao_bipe, int(sample_rate * duracao_bipe), False)
        
        # Frequências: Agudo no tempo 1 (cabeça do compasso), Médio nos demais
        bipe_forte = 0.5 * np.sin(2 * np.pi * 1200 * t_bipe) # 1200Hz
        bipe_fraco = 0.3 * np.sin(2 * np.pi * 800 * t_bipe)  # 800Hz
        
        # Envoltória de suavização (Fade out rápido para evitar 'clicks' secos)
        envelope = np.exp(-t_bipe * 30)
        bipe_forte = (bipe_forte * envelope * 32767).astype(np.int16)
        bipe_fraco = (bipe_fraco * envelope * 32767).astype(np.int16)
        
        # Buffer de áudio total
        amostras_totais = int(sample_rate * total_segundos)
        audio_buffer = np.zeros(amostras_totais, dtype=np.int16)
        
        for idx in range(total_batidas):
            posicao_amostra = int(idx * intervalo_tempo * sample_rate)
            eh_cabeca_compasso = (idx % num_tempos == 0)
            bipe_atual = bipe_forte if eh_cabeca_compasso else bipe_fraco
            
            fim_pos = posicao_amostra + len(bipe_atual)
            if fim_pos < amostras_totais:
                audio_buffer[posicao_amostra:fim_pos] = bipe_atual

        wavfile.write(caminho_saida, sample_rate, audio_buffer)
        return f"Sucesso! Metrônomo ({bpm} BPM, {formula}) gerado em: '{caminho_saida}'"
        
    except Exception as e:
        return f"Erro ao gerar click track: {str(e)}"