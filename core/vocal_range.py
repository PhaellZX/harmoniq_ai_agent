import re

class VocalRangeAnalyzer:
    NOTAS_INDEX = {
        'C': 0, 'C#': 1, 'DB': 1, 'D': 2, 'D#': 3, 'EB': 3,
        'E': 4, 'F': 5, 'F#': 6, 'GB': 6, 'G': 7, 'G#': 8,
        'AB': 8, 'A': 9, 'A#': 10, 'BB': 10, 'B': 11
    }
    
    INDEX_PARA_NOTA = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # Extensões vocais confortáveis padrão (Oitavas MIDI)
    CLASSIFICACOES_VOCAIS = {
        "soprano":   ("C4", "A5"),
        "mezzo":     ("A3", "F5"),
        "contralto": ("F3", "D5"),
        "tenor":     ("C3", "A4"),
        "baritono":  ("G2", "E4"),
        "baixo":     ("E2", "C4")
    }

    @classmethod
    def _normalizar_nota(cls, nota_str: str, oitava_padrao: int = 4) -> str:
        """Garante que a nota tenha a oitava especificada (ex: 'D' vira 'D3' se necessário)."""
        nota_str = str(nota_str).strip().upper()
        # Se veio apenas a nota sem oitava (ex: 'D' ou 'B')
        match = re.match(r'^([A-G][#B]?)$', nota_str)
        if match:
            return f"{match.group(1)}{oitava_padrao}"
        return nota_str

    @classmethod
    def nota_para_midi(cls, nota_str: str) -> int:
        nota_clean = str(nota_str).strip().upper()
        match = re.match(r'^([A-G][#B]?)(-?\d+)$', nota_clean)
        if not match:
            raise ValueError(f"Formato inválido: '{nota_str}'")
        
        nome_nota, oitava = match.groups()
        return (int(oitava) + 1) * 12 + cls.NOTAS_INDEX[nome_nota]

    @classmethod
    def midi_para_nota(cls, midi_val: int) -> str:
        oitava = (midi_val // 12) - 1
        nota = cls.INDEX_PARA_NOTA[midi_val % 12]
        return f"{nota}{oitava}"

    @classmethod
    def sugerir_tom_ideal(cls, tom_original: str, nota_min_musica: str, nota_max_musica: str, 
                           tipo_voz_ou_min_cantor: str, max_cantor: str = None) -> str:
        try:
            # Sanitiza as entradas
            nota_min_musica = cls._normalizar_nota(nota_min_musica, oitava_padrao=3)
            nota_max_musica = cls._normalizar_nota(nota_max_musica, oitava_padrao=4)

            tipo_voz = str(tipo_voz_ou_min_cantor).lower().strip()

            if tipo_voz in cls.CLASSIFICACOES_VOCAIS:
                cantor_min_str, cantor_max_str = cls.CLASSIFICACOES_VOCAIS[tipo_voz]
            else:
                cantor_min_str = cls._normalizar_nota(tipo_voz_ou_min_cantor, oitava_padrao=3)
                cantor_max_str = cls._normalizar_nota(max_cantor if max_cantor else "A4", oitava_padrao=4)

            cantor_min = cls.nota_para_midi(cantor_min_str)
            cantor_max = cls.nota_para_midi(cantor_max_str)

            musica_min = cls.nota_para_midi(nota_min_musica)
            musica_max = cls.nota_para_midi(nota_max_musica)

            if musica_min >= cantor_min and musica_max <= cantor_max:
                return (f"A música já está confortável no tom atual ({tom_original}). "
                        f"Alcance da música: {nota_min_musica}-{nota_max_musica} | Alcance do vocal: {cantor_min_str}-{cantor_max_str}.")

            deslocamento = 0
            if musica_max > cantor_max:
                deslocamento = cantor_max - musica_max
            elif musica_min < cantor_min:
                deslocamento = cantor_min - musica_min

            match_tom = re.match(r'^[A-G][#B]?', tom_original.strip().upper())
            if not match_tom:
                return f"Erro: Não foi possível identificar o tom original '{tom_original}'."
            
            raiz_original = match_tom.group(0)
            midi_raiz_original = cls.NOTAS_INDEX[raiz_original]
            midi_nova_raiz = (midi_raiz_original + deslocamento) % 12
            nova_raiz = cls.INDEX_PARA_NOTA[midi_nova_raiz]

            sufixo_tom = tom_original.strip()[len(raiz_original):]
            novo_tom = f"{nova_raiz}{sufixo_tom}"

            sinal = "+" if deslocamento > 0 else ""
            
            return (
                f"Sugestão de Tom Ideal: **{novo_tom}** ({sinal}{deslocamento} semitonos).\n"
                f"- Tom Original: {tom_original}\n"
                f"- Alcance da Música Original: {nota_min_musica} até {nota_max_musica}\n"
                f"- Alcance Recomendado ({tipo_voz.capitalize()}): {cantor_min_str} até {cantor_max_str}\n"
                f"- Novo Alcance Ajustado: {cls.midi_para_nota(musica_min + deslocamento)} até {cls.midi_para_nota(musica_max + deslocamento)}"
            )

        except Exception as e:
            return f"Erro ao calcular encaixe vocal: {str(e)}"