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
    def _converter_para_segundos(tempo: Union[str, float, int]) -> float:
        """Converte formatos 'MM:SS', 'HH:MM:SS', strings numéricas ou floats/ints para segundos (float)."""
        if isinstance(tempo, (int, float)):
            return float(tempo)

        if isinstance(tempo, str):
            tempo = tempo.strip()
            if ":" in tempo:
                partes = tempo.split(":")
                try:
                    if len(partes) == 2:  # MM:SS
                        return float(partes[0]) * 60 + float(partes[1])
                    elif len(partes) == 3:  # HH:MM:SS
                        return float(partes[0]) * 3600 + float(partes[1]) * 60 + float(partes[2])
                except ValueError:
                    return 0.0
            try:
                return float(tempo)
            except ValueError:
                return 0.0

        return 0.0

    @staticmethod
    def normalizar_audio(caminho_entrada: str, caminho_saida: str = "output/saida_normalizada.wav", decibeis_alvo: Union[float, str] = -1.0) -> str:
        """Ajusta o ganho do áudio para que o pico máximo atinja o valor em dBFS especificado (evita clipping/distorção)."""
        if not os.path.exists(caminho_entrada):
            return f"Erro: O arquivo '{caminho_entrada}' não foi encontrado."

        try:
            decibeis_alvo = float(decibeis_alvo)
            os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
            y, sr = librosa.load(caminho_entrada, sr=None)

            pico_maximo = np.max(np.abs(y))
            if pico_maximo == 0:
                return "Erro: O arquivo de áudio está completamente silencioso."

            alvo_linear = 10 ** (decibeis_alvo / 20.0)
            fator_ganho = alvo_linear / pico_maximo
            y_normalizado = y * fator_ganho

            sf.write(caminho_saida, y_normalizado, sr)
            return f"Sucesso! Áudio normalizado para {decibeis_alvo} dBFS. Salvo em '{caminho_saida}'."
        except Exception as e:
            return f"Erro ao normalizar o áudio: {str(e)}"

    @staticmethod
    def cortar_audio(caminho_entrada: str, inicio_seg: Union[float, str], fim_seg: Union[float, str], caminho_saida: str = "output/saida_cortada.wav") -> str:
        """Corta um trecho do áudio especificando o tempo inicial e final em segundos ou formato MM:SS."""
        if not os.path.exists(caminho_entrada):
            return f"Erro: O arquivo '{caminho_entrada}' não foi encontrado."

        inicio = AudioProcessor._converter_para_segundos(inicio_seg)
        fim = AudioProcessor._converter_para_segundos(fim_seg)

        if inicio < 0 or fim <= inicio:
            return f"Erro: Parâmetros de corte inválidos ({inicio_seg} até {fim_seg}). O tempo final deve ser maior que o inicial."

        try:
            os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
            duracao = fim - inicio
            y, sr = librosa.load(caminho_entrada, sr=None, offset=inicio, duration=duracao)

            sf.write(caminho_saida, y, sr)
            return f"Sucesso! Trecho de {inicio_seg} ({inicio}s) até {fim_seg} ({fim}s) cortado com sucesso. Salvo em '{caminho_saida}'."
        except Exception as e:
            return f"Erro ao cortar o áudio: {str(e)}"

    @staticmethod
    def detectar_tom_e_bpm(caminho_entrada: str) -> str:
        """Estimativa de BPM e Tonality (Key) usando Chromagrama e Krumhansl-Schmuckler profiles."""
        if not os.path.exists(caminho_entrada):
            return f"Erro: O arquivo '{caminho_entrada}' não foi encontrado."

        try:
            y, sr = librosa.load(caminho_entrada, sr=None, offset=15.0, duration=60.0)

            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm = float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)

            y_harmonic, _ = librosa.effects.hpss(y)
            chroma = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)
            chroma_avg = np.mean(chroma, axis=1)

            notas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            perfil_maior = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
            perfil_menor = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 2.69, 3.34, 3.17, 3.28]

            melhor_correlacao = -1
            tom_detectado = "Desconhecido"

            for i in range(12):
                chroma_rot = np.roll(chroma_avg, -i)
                corr_maior = np.corrcoef(chroma_rot, perfil_maior)[0, 1]
                corr_menor = np.corrcoef(chroma_rot, perfil_menor)[0, 1]

                if corr_maior > melhor_correlacao:
                    melhor_correlacao = corr_maior
                    tom_detectado = f"{notas[i]} Maior"

                if corr_menor > melhor_correlacao:
                    melhor_correlacao = corr_menor
                    tom_detectado = f"{notas[i]} menor"

            return f"Análise concluída: Tom estimado: {tom_detectado} | Andamento: {round(bpm)} BPM."

        except Exception as e:
            return f"Erro ao analisar o áudio: {str(e)}"

    @staticmethod
    def mudar_tom(caminho_entrada: str, semitonos: Union[float, str], caminho_saida: str = "output/saida_transposta.wav") -> str:
        """Altera o tom (pitch shift) de um áudio sem alterar a velocidade."""
        if not os.path.exists(caminho_entrada):
            return f"Erro: O arquivo '{caminho_entrada}' não foi encontrado."

        try:
            semitonos_val = float(semitonos)
            os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
            y, sr = librosa.load(caminho_entrada, sr=None)
            y_shifted = librosa.effects.pitch_shift(y=y, sr=sr, n_steps=semitonos_val)
            sf.write(caminho_saida, y_shifted, sr)
            return f"Sucesso! Áudio transposto em {semitonos_val} semitonos e salvo em '{caminho_saida}'."
        except Exception as e:
            return f"Erro ao alterar o tom do áudio: {str(e)}"

    @staticmethod
    def alterar_velocidade(caminho_entrada: str, fator_frequencia: Union[float, str], caminho_saida: str = "output/saida_velocidade.wav") -> str:
        """Altera a velocidade (time stretch) de um áudio sem alterar o tom."""
        if not os.path.exists(caminho_entrada):
            return f"Erro: O arquivo '{caminho_entrada}' não foi encontrado."

        try:
            fator_val = float(fator_frequencia)
            if fator_val <= 0:
                return "Erro: O fator de velocidade deve ser maior que zero."

            os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
            y, sr = librosa.load(caminho_entrada, sr=None)
            y_stretched = librosa.effects.time_stretch(y=y, rate=fator_val)
            sf.write(caminho_saida, y_stretched, sr)
            
            percentual = int((fator_val - 1.0) * 100)
            status_str = f"{abs(percentual)}% mais rápido" if percentual >= 0 else f"{abs(percentual)}% mais lento"
            return f"Sucesso! Velocidade alterada em {fator_val}x ({status_str}). Salvo em '{caminho_saida}'."
        except Exception as e:
            return f"Erro ao alterar a velocidade do áudio: {str(e)}"

    @staticmethod
    def separar_stems(caminho_entrada: str, modo: str = "playback") -> str:
        """Separa os instrumentos do áudio usando Demucs."""
        if not os.path.exists(caminho_entrada):
            return f"Erro: O arquivo '{caminho_entrada}' não foi encontrado."

        pasta_saida = "output/stems"
        os.makedirs(pasta_saida, exist_ok=True)

        try:
            comando = [
                "demucs",
                "-n", "htdemucs",
                "--two-stems=vocals",
                "-o", pasta_saida,
                caminho_entrada
            ]

            resultado_proc = subprocess.run(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if resultado_proc.returncode != 0:
                return f"Erro na execução do Demucs:\n{resultado_proc.stderr}"

            nome_base = os.path.splitext(os.path.basename(caminho_entrada))[0]
            pasta_resultado = os.path.join(pasta_saida, "htdemucs", nome_base)

            caminho_vocal = os.path.join(pasta_resultado, "vocals.wav")
            caminho_playback = os.path.join(pasta_resultado, "no_vocals.wav")

            if modo == "vocal" and os.path.exists(caminho_vocal):
                return f"Sucesso! Voz isolada salva em: '{caminho_vocal}'."
            elif modo == "playback" and os.path.exists(caminho_playback):
                return f"Sucesso! Playback (sem voz) salvo em: '{caminho_playback}'."
            elif os.path.exists(pasta_resultado):
                return f"Sucesso! Faixas processadas em: '{pasta_resultado}'."
            else:
                return f"Processamento concluído. Verifique os arquivos na pasta: '{pasta_saida}'"

        except Exception as e:
            return f"Erro ao executar a separação de stems: {str(e)}"