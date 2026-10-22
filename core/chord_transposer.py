import re

class ChordTransposer:
    # Chromatic mapping using sharps and flats
    SHARP_NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    FLAT_NOTES  = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

    POSITION_MAP = {
        'C': 0, 'C#': 1, 'DB': 1,
        'D': 2, 'D#': 3, 'EB': 3,
        'E': 4,
        'F': 5, 'F#': 6, 'GB': 6,
        'G': 7, 'G#': 8, 'AB': 8,
        'A': 9, 'A#': 10, 'BB': 10,
        'B': 11
    }

    # Regex to capture root note (e.g., C#, Bb, F)
    NOTE_REGEX = re.compile(r'^[A-G](?:#|b)?')

    # Regex to identify if a line contains predominantly chords
    CHORD_REGEX = re.compile(r'\b[A-G](?:#|b)?(?:m|maj|min|dim|aug|sus\d?|add\d?|\d)*(?:\/[A-G](?:#|b)?)?\b')

    @classmethod
    def _transpose_note(cls, note: str, semitones: int, use_flats: bool = False) -> str:
        note_upper = note.upper()
        if note_upper not in cls.POSITION_MAP:
            return note

        original_pos = cls.POSITION_MAP[note_upper]
        new_pos = (original_pos + semitones) % 12

        scale = cls.FLAT_NOTES if use_flats else cls.SHARP_NOTES
        return scale[new_pos]

    @classmethod
    def _transpose_single_chord(cls, chord: str, semitones: int, use_flats: bool = False) -> str:
        """Transposes root note and bass note (if slash chord exists '/')."""
        if '/' in chord:
            parts = chord.split('/')
            root_part = cls._transpose_single_chord(parts[0], semitones, use_flats)
            bass_part = cls._transpose_single_chord(parts[1], semitones, use_flats)
            return f"{root_part}/{bass_part}"

        # Match root note at the beginning of the chord string
        match = cls.NOTE_REGEX.match(chord)
        if not match:
            return chord

        root_note = match.group(0)
        suffix = chord[len(root_note):]
        new_root = cls._transpose_note(root_note, semitones, use_flats)

        return new_root + suffix

    @classmethod
    def transpose_text(cls, chord_text: str, semitones: int = 0, source_key: str = None, target_key: str = None) -> str:
        """
        Transposes full chord chart text while preserving spaces and layout.
        Accepts direct semitone steps or source and target key names.
        """
        # If source and target keys are provided (e.g., C to D), calculate semitones
        if source_key and target_key:
            source_clean = source_key.upper().replace("MAJOR", "").replace("MINOR", "").replace("MAIOR", "").replace("MENOR", "").strip()
            target_clean = target_key.upper().replace("MAJOR", "").replace("MINOR", "").replace("MAIOR", "").replace("MENOR", "").strip()

            if source_clean in cls.POSITION_MAP and target_clean in cls.POSITION_MAP:
                semitones = cls.POSITION_MAP[target_clean] - cls.POSITION_MAP[source_clean]

        if semitones == 0:
            return chord_text

        # Determine flat/sharp preference based on target key
        use_flats = "b" in target_key.lower() if target_key else False

        lines = chord_text.split('\n')
        transposed_lines = []

        for line in lines:
            # Replace chords while attempting to maintain visual alignment
            def replace_match(match):
                original_chord = match.group(0)
                new_chord = cls._transpose_single_chord(original_chord, semitones, use_flats)
                
                # Adjust spacing if chord length changes to keep alignment with lyrics
                len_diff = len(original_chord) - len(new_chord)
                if len_diff > 0:
                    return new_chord + (" " * len_diff)
                return new_chord

            processed_line = cls.CHORD_REGEX.sub(replace_match, line)
            transposed_lines.append(processed_line)

        return "\n".join(transposed_lines)

    # =========================================================================
    # BACKWARD COMPATIBILITY ALIASES
    # =========================================================================
    @classmethod
    def transpor_cifra_texto(cls, texto_cifra: str, semitonos: int = 0, tom_origem: str = None, tom_destino: str = None) -> str:
        return cls.transpose_text(chord_text=texto_cifra, semitones=semitonos, source_key=tom_origem, target_key=tom_destino)

    @classmethod
    def transpor_texto(cls, texto_cifra: str, semitonos: int = 0, tom_origem: str = None, tom_destino: str = None) -> str:
        return cls.transpose_text(chord_text=texto_cifra, semitones=semitonos, source_key=tom_origem, target_key=tom_destino)