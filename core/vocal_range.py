import re

class VocalRangeAnalyzer:
    NOTE_INDEX = {
        'C': 0, 'C#': 1, 'DB': 1, 'D': 2, 'D#': 3, 'EB': 3,
        'E': 4, 'F': 5, 'F#': 6, 'GB': 6, 'G': 7, 'G#': 8,
        'AB': 8, 'A': 9, 'A#': 10, 'BB': 10, 'B': 11
    }
    
    INDEX_TO_NOTE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # Standard comfortable vocal ranges (MIDI Octaves)
    VOCAL_CLASSIFICATIONS = {
        "soprano":   ("C4", "A5"),
        "mezzo":     ("A3", "F5"),
        "alto":      ("F3", "D5"),
        "contralto": ("F3", "D5"),
        "tenor":     ("C3", "A4"),
        "baritone":  ("G2", "E4"),
        "baritono":  ("G2", "E4"),
        "bass":      ("E2", "C4"),
        "baixo":     ("E2", "C4")
    }

    @classmethod
    def _normalize_note(cls, note_str: str, default_octave: int = 4) -> str:
        """Ensures the note string includes an octave (e.g., 'D' becomes 'D4' if unspecified)."""
        note_str = str(note_str).strip().upper()
        match = re.match(r'^([A-G][#B]?)$', note_str)
        if match:
            return f"{match.group(1)}{default_octave}"
        return note_str

    @classmethod
    def note_to_midi(cls, note_str: str) -> int:
        clean_note = str(note_str).strip().upper()
        match = re.match(r'^([A-G][#B]?)(-?\d+)$', clean_note)
        if not match:
            raise ValueError(f"Invalid note format: '{note_str}'")
        
        note_name, octave = match.groups()
        return (int(octave) + 1) * 12 + cls.NOTE_INDEX[note_name]

    @classmethod
    def midi_to_note(cls, midi_val: int) -> str:
        octave = (midi_val // 12) - 1
        note = cls.INDEX_TO_NOTE[midi_val % 12]
        return f"{note}{octave}"

    @classmethod
    def suggest_ideal_key(cls, original_key: str, song_min_note: str, song_max_note: str, 
                          vocal_type_or_min_singer: str, singer_max_note: str = None) -> str:
        """
        Calculates optimal key transposition to fit song pitch within singer range or vocal type.
        """
        try:
            song_min_note = cls._normalize_note(song_min_note, default_octave=3)
            song_max_note = cls._normalize_note(song_max_note, default_octave=4)

            vocal_type = str(vocal_type_or_min_singer).lower().strip()

            if vocal_type in cls.VOCAL_CLASSIFICATIONS:
                singer_min_str, singer_max_str = cls.VOCAL_CLASSIFICATIONS[vocal_type]
            else:
                singer_min_str = cls._normalize_note(vocal_type_or_min_singer, default_octave=3)
                singer_max_str = cls._normalize_note(singer_max_note if singer_max_note else "A4", default_octave=4)

            singer_min = cls.note_to_midi(singer_min_str)
            singer_max = cls.note_to_midi(singer_max_str)

            song_min = cls.note_to_midi(song_min_note)
            song_max = cls.note_to_midi(song_max_note)

            if song_min >= singer_min and song_max <= singer_max:
                return (f"The song is already comfortable in its current key ({original_key}). "
                        f"Song range: {song_min_note}-{song_max_note} | Vocal range: {singer_min_str}-{singer_max_str}.")

            shift = 0
            if song_max > singer_max:
                shift = singer_max - song_max
            elif song_min < singer_min:
                shift = singer_min - song_min

            match_key = re.match(r'^[A-G][#B]?', original_key.strip().upper())
            if not match_key:
                return f"Error: Could not identify original root key from '{original_key}'."
            
            original_root = match_key.group(0)
            original_root_midi = cls.NOTE_INDEX[original_root]
            new_root_midi = (original_root_midi + shift) % 12
            new_root = cls.INDEX_TO_NOTE[new_root_midi]

            key_suffix = original_key.strip()[len(original_root):]
            new_key = f"{new_root}{key_suffix}"

            sign = "+" if shift > 0 else ""
            
            return (
                f"Suggested Ideal Key: **{new_key}** ({sign}{shift} semitones).\n"
                f"- Original Key: {original_key}\n"
                f"- Original Song Range: {song_min_note} to {song_max_note}\n"
                f"- Target Vocal Range ({vocal_type.capitalize()}): {singer_min_str} to {singer_max_str}\n"
                f"- Adjusted Song Range: {cls.midi_to_note(song_min + shift)} to {cls.midi_to_note(song_max + shift)}"
            )

        except Exception as e:
            return f"Error calculating vocal fit: {str(e)}"

    # =========================================================================
    # BACKWARD COMPATIBILITY ALIASES
    # =========================================================================
    @classmethod
    def sugerir_tom_ideal(cls, tom_original: str, nota_min_musica: str, nota_max_musica: str, 
                           tipo_voz_ou_min_cantor: str, max_cantor: str = None) -> str:
        return cls.suggest_ideal_key(
            original_key=tom_original,
            song_min_note=nota_min_musica,
            song_max_note=nota_max_musica,
            vocal_type_or_min_singer=tipo_voz_ou_min_cantor,
            singer_max_note=max_cantor
        )