from typing import List, Dict, Optional
import json

class SetlistFormatter:
    @staticmethod
    def gerar_setlist_texto(músicas: List[Dict[str, str]], titulo: str = "SETLIST DO CULTO / SHOW") -> str:
        """
        Gera uma setlist formatada em texto/markdown a partir de uma lista de dicionários.
        Cada dicionário deve conter: 'titulo', 'tom', 'bpm', 'ministro', 'observacoes'.
        """
        if not músicas:
            return "Nenhuma música fornecida para a setlist."

        linhas = []
        linhas.append(f"════════════════════════════════════════")
        linhas.append(f"   📋 {titulo.upper()}")
        linhas.append(f"════════════════════════════════════════\n")

        for idx, m in enumerate(músicas, start=1):
            nome = m.get("titulo", "Música sem título")
            tom = m.get("tom", "N/I")
            bpm = m.get("bpm", "N/I")
            ministro = m.get("ministro", "Equipe")
            obs = m.get("observacoes", "")

            linhas.append(f"  {idx}. {nome.upper()}")
            linhas.append(f"     • Tom: {tom}  |  BPM: {bpm}  |  Voz: {ministro}")
            if obs:
                linhas.append(f"     • Obs: {obs}")
            linhas.append("")

        linhas.append("════════════════════════════════════════")
        return "\n".join(linhas)

    @staticmethod
    def parse_e_formatar(json_músicas_str: str, titulo: str = "SETLIST DO CULTO / SHOW") -> str:
        """
        Converte uma string JSON de músicas em uma setlist formatada.
        """
        try:
            dados = json.loads(json_músicas_str)
            if isinstance(dados, dict) and "musicas" in dados:
                dados = dados["musicas"]
            if not isinstance(dados, list):
                return "Erro: O formato fornecido deve ser uma lista de músicas em JSON."
            
            return SetlistFormatter.gerar_setlist_texto(dados, titulo)
        except Exception as e:
            return f"Erro ao processar lista de músicas: {str(e)}"