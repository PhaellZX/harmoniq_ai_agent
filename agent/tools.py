OLLAMA_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "change_audio_pitch",
            "description": "Changes the key/pitch of an audio file by semitones.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Path to the audio file."
                    },
                    "semitones": {
                        "type": "integer",
                        "description": "Number of semitones. Use a negative integer to lower pitch (e.g., -1 for half step down) and positive to raise pitch (e.g., 1 for half step up)."
                    },
                    "source_key": {
                        "type": "string",
                        "description": "Current original key of the audio (e.g., 'Ab', 'C', 'G#')."
                    },
                    "target_key": {
                        "type": "string",
                        "description": "Target key after applying semitones (e.g., from Ab with -1 semitone the target key is G)."
                    }
                },
                "required": ["semitones"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "change_audio_speed",
            "description": "Changes the tempo/speed of the audio playback without altering the pitch.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_path": {"type": "string", "description": "Path to the audio file."},
                    "speed_factor": {"type": "number", "description": "Speed factor (e.g., 1.1 for faster, 0.9 for slower)."}
                },
                "required": ["speed_factor"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "separate_audio_stems",
            "description": "Separates audio stems and instruments (vocals, drums, bass, accompaniment).",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_path": {"type": "string", "description": "Path to the audio file."},
                    "mode": {"type": "string", "description": "Separation mode: '2stems' (vocals/backing track) or '4stems'."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "detect_audio_key_and_bpm",
            "description": "Analyzes and detects the musical key and tempo (BPM) of an audio file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_path": {"type": "string", "description": "Path to the audio file."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "normalize_audio",
            "description": "Adjusts and normalizes audio gain/volume. ALWAYS use when the user asks to 'normalize', 'adjust volume', or 'equalize audio'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Path to the audio file."
                    },
                    "target_db": {
                        "type": "number",
                        "description": "Target volume in dBFS (default is -14.0)."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "trim_audio",
            "description": "Trims an audio segment given start and end times. Optionally accepts input audio path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Path to the audio file on system (optional if an active file is already loaded)."
                    },
                    "start_sec": {
                        "type": "string",
                        "description": "Start time in 'MM:SS' format or seconds. Example: '0:37'"
                    },
                    "end_sec": {
                        "type": "string",
                        "description": "End time in 'MM:SS' format or seconds. Example: '3:15'"
                    }
                },
                "required": ["start_sec", "end_sec"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "download_audio_link",
            "description": "Downloads audio from a YouTube or Google Drive URL/link for local processing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL/link of the video or audio source."}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "transpose_chord_text",
            "description": "Transposes text-based chord charts by changing chords from one key to another.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chord_text": {"type": "string", "description": "Full chord chart text."},
                    "semitones": {"type": "integer", "description": "Number of semitones."},
                    "source_key": {"type": "string", "description": "Current chord key."},
                    "target_key": {"type": "string", "description": "Target chord key."}
                },
                "required": ["chord_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_vocal_key",
            "description": "Analyzes the singer's vocal range against the song pitch to suggest the ideal key.",
            "parameters": {
                "type": "object",
                "properties": {
                    "original_key": {"type": "string", "description": "Original key of the song."},
                    "song_min_note": {"type": "string", "description": "Lowest note in the song."},
                    "song_max_note": {"type": "string", "description": "Highest note in the song."},
                    "vocal_type_or_min_singer": {"type": "string", "description": "Vocal type or singer's lowest note."},
                    "singer_max_note": {"type": "string", "description": "Singer's highest note."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_formatted_setlist",
            "description": "Generates a clean, formatted setlist for worship ministers and band musicians.",
            "parameters": {
                "type": "object",
                "properties": {
                    "songs_json_str": {"type": "string", "description": "JSON string containing songs list and metadata."},
                    "title": {"type": "string", "description": "Service or rehearsal title."}
                },
                "required": ["songs_json_str"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "export_audio",
            "description": "Converts and exports the current or modified audio file to a specified format (WAV or MP3). Does not alter pitch or tempo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_format": {
                        "type": "string",
                        "description": "Desired output format ('wav' or 'mp3')."
                    }
                },
                "required": ["target_format"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "export_chord_pdf",
            "description": "Generates a styled PDF file containing the transposed chord chart and rehearsal metadata.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Song title."},
                    "key": {"type": "string", "description": "Song key."},
                    "chord_text": {"type": "string", "description": "Chord chart text content."},
                    "minister": {"type": "string", "description": "Worship leader or minister name."},
                    "bpm": {"type": "string", "description": "Tempo in BPM."}
                },
                "required": ["chord_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_click_track",
            "description": "Generates a custom metronome/click track audio file with specified BPM, time signature, and duration.",
            "parameters": {
                "type": "object",
                "properties": {
                    "bpm": {"type": "integer", "description": "Tempo in BPM (e.g., 120, 70)."},
                    "time_signature": {"type": "string", "description": "Time signature (e.g., '4/4', '3/4', '6/8')."},
                    "duration_minutes": {"type": "number", "description": "Total audio duration in minutes."}
                }
            }
        }
    }
]