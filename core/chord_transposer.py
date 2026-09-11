import re

class ChordTransposer:
    # Mapeamento cromático com sustenidos e bemóis
    NOTAS_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    NOTAS_FLAT  = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

    MAP_POSICAO = {
        'C': 0, 'C#': 1, 'DB': 1,
        'D': 2, 'D#': 3, 'EB': 3,
        'E': 4,
        'F': 5, 'F#': 6, 'GB': 6,
        'G': 7, 'G#': 8, 'AB': 8,
        'A': 9, 'A#': 10, 'BB': 10,
        'B': 11
    }

    # Regex para capturar notas fundamentais (ex: C#, Bb, F)
    REGEX_NOTA = re.compile(r'^[A-G](?:#|b)?')

    # Regex para identificar se uma linha do texto contém predominantemente acordes
    REGEX_ACORDE = re.compile(r'\b[A-G](?:#|b)?(?:m|maj|min|dim|aug|sus\d?|add\d?|\d)*(?:\/[A-G](?:#|b)?)?\b')

    @classmethod
    def _transpor_nota(cls, nota: str, semitonos: int, usar_bemoles: bool = False) -> str:
        nota_upper = nota.upper()
        if nota_upper not in cls.MAP_POSICAO:
            return nota

        pos_original = cls.MAP_POSICAO[nota_upper]
        nova_pos = (pos_original + semitonos) % 12

        escala = cls.NOTAS_FLAT if usar_bemoles else cls.NOTAS_SHARP
        nova_nota = escala[nova_pos]

        # Mantém a capitalização original se necessário
        return nova_nota

    @classmethod
    def _transpor_acorde_individual(cls, acorde: str, semitonos: int, usar_bemoles: bool = False) -> str:
        """Transpõe a nota fundamental e a nota do baixo (se houver inversão com barra '/')."""
        if '/' in acorde:
            partes = acorde.split('/')
            principal = cls._transpor_acorde_individual(partes[0], semitonos, usar_bemoles)
            baixo = cls._transpor_acorde_individual(partes[1], semitonos, usar_bemoles)
            return f"{principal}/{baixo}"

        # Encontra a nota raiz no início do acorde
        match = cls.REGEX_NOTA.match(acorde)
        if not match:
            return acorde

        nota_raiz = match.group(0)
        sufixo = acorde[len(nota_raiz):]
        nova_raiz = cls._transpor_nota(nota_raiz, semitonos, usar_bemoles)

        return nova_raiz + sufixo

    @classmethod
    def transpor_cifra_texto(cls, texto_cifra: str, semitonos: int = 0, tom_origem: str = None, tom_destino: str = None) -> str:
        """
        Transpõe todo o texto de uma cifra preservando espaços e formatação.
        Aceita a variação em semitonos direta ou o tom de origem e destino.
        """
        # Se foram passados tons em texto (ex: C para D), calcula os semitonos
        if tom_origem and tom_destino:
            origem_clean = tom_origem.upper().replace("MAIOR", "").replace("MENOR", "").strip()
            destino_clean = tom_destino.upper().replace("MAIOR", "").replace("MENOR", "").strip()

            if origem_clean in cls.MAP_POSICAO and destino_clean in cls.MAP_POSICAO:
                semitonos = cls.MAP_POSICAO[destino_clean] - cls.MAP_POSICAO[origem_clean]

        if semitonos == 0:
            return texto_cifra

        # Determina preferências de acidentes (bemóis ou sustenidos) com base no destino
        usar_bemoles = "b" in tom_destino.lower() if tom_destino else False

        linhas = texto_cifra.split('\n')
        linhas_transpostas = []

        for linha in linhas:
            # Substitui cada acorde mantendo o alinhamento de colunas/espaços
            def substituir(match):
                acorde_original = match.group(0)
                acorde_novo = cls._transpor_acorde_individual(acorde_original, semitonos, usar_bemoles)
                # Ajusta espaçamento se o tamanho do acorde mudar para não desalinhá-lo da letra
                diferenca_tamanho = len(acorde_original) - len(acorde_novo)
                if diferenca_tamanho > 0:
                    return acorde_novo + (" " * diferenca_tamanho)
                return acorde_novo

            linha_processada = cls.REGEX_ACORDE.sub(substituir, linha)
            linhas_transpostas.append(linha_processada)

        return "\n".join(linhas_transpostas)