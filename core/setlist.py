import json
from typing import List, Dict, Optional

class SetlistFormatter:
    @staticmethod
    def generate_setlist_text(songs: List[Dict[str, str]], title: str = "WORSHIP / SHOW SETLIST") -> str:
        """
        Generates a formatted text/markdown setlist from a list of dictionaries.
        Each dictionary should contain: 'title', 'key', 'bpm', 'minister', 'notes' (or legacy keys 'titulo', 'tom', 'observacoes').
        """
        if not songs:
            return "No songs provided for the setlist."

        lines = []
        lines.append("════════════════════════════════════════")
        lines.append(f"   📋 {title.upper()}")
        lines.append("════════════════════════════════════════\n")

        for idx, song in enumerate(songs, start=1):
            name = song.get("title") or song.get("titulo", "Untitled Song")
            key = song.get("key") or song.get("tom", "N/I")
            bpm = song.get("bpm", "N/I")
            minister = song.get("minister") or song.get("ministro", "Team")
            obs = song.get("notes") or song.get("observacoes", "")

            lines.append(f"  {idx}. {name.upper()}")
            lines.append(f"     • Key: {key}  |  BPM: {bpm}  |  Vocal: {minister}")
            if obs:
                lines.append(f"     • Notes: {obs}")
            lines.append("")

        lines.append("════════════════════════════════════════")
        return "\n".join(lines)

    @staticmethod
    def parse_and_format(songs_json_str: str, title: str = "WORSHIP / SHOW SETLIST") -> str:
        """
        Converts a JSON string of songs into a formatted setlist string.
        """
        try:
            data = json.loads(songs_json_str)
            if isinstance(data, dict):
                data = data.get("songs") or data.get("musicas", [])
            if not isinstance(data, list):
                return "Error: The provided format must be a JSON array of songs."
            
            return SetlistFormatter.generate_setlist_text(data, title)
        except Exception as e:
            return f"Error processing song setlist: {str(e)}"

    # =========================================================================
    # BACKWARD COMPATIBILITY ALIASES
    # =========================================================================
    @staticmethod
    def gerar_setlist_texto(músicas: List[Dict[str, str]], titulo: str = "SETLIST DO CULTO / SHOW") -> str:
        return SetlistFormatter.generate_setlist_text(songs=músicas, title=titulo)

    @staticmethod
    def parse_e_formatar(json_músicas_str: str, titulo: str = "SETLIST DO CULTO / SHOW") -> str:
        return SetlistFormatter.parse_and_format(songs_json_str=json_músicas_str, title=titulo)