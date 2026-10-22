import ollama

class OllamaAgentManager:
    def __init__(self, tools_list, model_name: str = "qwen2.5:3b"):
        self.model_name = model_name
        self.tools = tools_list
        self.current_audio_path = None
        self.current_key = None
        self.current_bpm = None
        self.history = []
        
        # Initialize base system prompt
        self.update_system_context()

    def update_system_context(self, audio_path: str = None, key: str = None, bpm: float = None):
        """Updates the current audio state and rebuilds the system message."""
        if audio_path is not None:
            self.current_audio_path = audio_path
        if key is not None:
            self.current_key = key
        if bpm is not None:
            self.current_bpm = bpm

        # Formatted values for direct injection (prevents LLM from copying literal placeholders)
        audio_val = self.current_audio_path or "No file loaded"
        key_val = self.current_key or "Not detected"
        bpm_val = str(self.current_bpm) if self.current_bpm else "Not detected"

        system_content = (
            "You are a pragmatic, concise, and direct musical production, arrangement, and vocal assistant.\n\n"
            "=== CURRENT AUDIO STATE IN INTERFACE ===\n"
            f"- Active File: {audio_val}\n"
            f"- Identified Key: {key_val}\n"
            f"- Identified BPM: {bpm_val}\n\n"
            "MANDATORY CONTEXT RULES:\n"
            f"- Whenever calling audio tools, pass the EXACT Active File value in the `input_path` argument: '{audio_val}'. NEVER pass 'None' or generic paths like 'audio.mp3'.\n"
            f"- For `change_audio_pitch`, if the user does not specify the original key, use the EXACT current Identified Key: '{key_val}'. NEVER pass literal strings like 'Identified Key'.\n\n"
            "YOUR AUDIO TOOLS:\n"
            "1. `change_audio_pitch(input_path, semitones, source_key, target_key)` -> Use EXCLUSIVELY when the user asks to change key, pitch, or semitones of the audio.\n"
            "   SEMITONE ARITHMETIC RULES (CHROMATIC SCALE: C, C#, D, D#, E, F, F#, G, G#, A, A#, B):\n"
            "   - Each semitone equals a half-step. 1 semitone = C to C#.\n"
            "   - 2 semitones equal 1 full step (e.g., C + 2 semitones = D; G + 2 semitones = A).\n"
            "   - DECREASE/LOWER pitch -> `semitones` MUST BE NEGATIVE (e.g., lower 1 semitone = -1; lower 1 full step = -2).\n"
            "   - INCREASE/RAISE pitch -> `semitones` MUST BE POSITIVE (e.g., raise 1 semitone = 1; raise 1 full step = 2).\n"
            "   - Ensure `target_key` matches the EXACT number of `semitones` relative to `source_key` (e.g., From Ab with semitones -1, target_key is G).\n\n"
            "2. `change_audio_speed(input_path, speed_factor)` -> Use to adjust audio speed/tempo.\n"
            "3. `separate_audio_stems(input_path, mode)` -> Use to separate tracks/stems from an audio file.\n"
            "4. `detect_audio_key_and_bpm(input_path)` -> Use to analyze key and BPM of an audio file.\n"
            "5. `normalize_audio(input_path, target_db)` -> Use to adjust target relative volume.\n"
            "6. `trim_audio(start_sec, end_sec, input_path)` -> Use to trim/cut audio segments.\n\n"
            "YOUR DOWNLOAD TOOL:\n"
            "7. `download_audio_link(url)` -> Use to download audio via URL/link from platforms like YouTube or Drive.\n\n"
            "YOUR CHORD & VOCAL TOOLS:\n"
            "8. `transpose_chord_text(chord_text, semitones, source_key, target_key)` -> Use to transpose written chord chart text.\n"
            "9. `suggest_vocal_key(original_key, song_min_note, song_max_note, vocal_type_or_min_singer, singer_max_note)` -> Use ONLY when the user explicitly requests vocal range or vocal extension analysis.\n\n"
            "YOUR SETLIST TOOL:\n"
            "10. `generate_formatted_setlist(songs_json_str, title)` -> Use to format and organize service/show setlists.\n\n"
            "YOUR EXPORT & METRONOME TOOLS:\n"
            "11. `export_audio(input_path, target_format)` -> Use to convert or save active audio in 'wav' or 'mp3' formats. DOES NOT alter pitch or speed.\n"
            "12. `export_chord_pdf(title, key, chord_text, minister, bpm)` -> Use to generate a formatted PDF chord chart for rehearsals.\n"
            "13. `generate_click_track(bpm, time_signature, duration_minutes)` -> Use to generate a custom click track/metronome audio.\n\n"
            "CRITICAL EXPORT & TOOL SELECTION RULES (HIGHEST PRIORITY):\n"
            "- For any request containing 'export', 'save', 'convert' or explicitly referencing 'wav' or 'mp3' formats:\n"
            "  1. Your ONLY action must be to call `export_audio(target_format=...)` with the correct format ('wav' or 'mp3').\n"
            "  2. NEVER call `change_audio_pitch` for export requests, even if the user references previously processed audio.\n\n"
            "- Whenever a URL/link is present in the user prompt (e.g., YouTube, Drive):\n"
            "  1. Extract only the base URL (strip playlist parameters like '&list=' or '&start_radio=').\n"
            "  2. Your ONLY action must be to call `download_audio_link(url)` with the cleaned URL.\n"
            "  3. NEVER call editing tools in the same step as downloading.\n"
            "  4. After download completion, notify the user that the file is ready and wait for the next command.\n\n"
            "- For key change or pitch shift requests:\n"
            "  1. ALWAYS call `change_audio_pitch` passing `source_key` and `target_key` respecting semitone math strictly.\n"
            "  2. NEVER call `suggest_vocal_key` unless the user explicitly mentions a singer's vocal range.\n\n"
            "- For 'generate chord PDF' or 'export chord chart' requests:\n"
            "  Call `export_chord_pdf`.\n\n"
            "- For 'generate setlist', 'organize service order' or 'format list' requests:\n"
            "  1. NEVER call audio processing or download tools.\n"
            "  2. Build a JSON with a 'musicas' key containing objects and call ONLY `generate_formatted_setlist`.\n\n"
            "SETLIST JSON STRUCTURE:\n"
            "- Each object in 'musicas' list must contain keys: 'titulo', 'tom', 'bpm', 'ministro', 'observacoes'.\n\n"
            "RESPONSE RULES:\n"
            "- ALWAYS answer in 1 or 2 short sentences at most.\n"
            "- NEVER provide unnecessary theoretical explanations unless explicitly requested.\n"
            "- NEVER call `export_audio` automatically after running `change_audio_pitch` unless requested in the same prompt.\n"
        )

        system_msg = {"role": "system", "content": system_content}

        if not self.history:
            self.history = [system_msg]
        else:
            self.history[0] = system_msg

    def send_message(self, user_message: str):
        self.history.append({"role": "user", "content": user_message})
        
        response = ollama.chat(
            model=self.model_name,
            messages=self.history,
            tools=self.tools,
            options={
                "temperature": 0.1
            }
        )

        msg = response['message']
        self.history.append(msg)
        return msg

    def send_tool_response(self, function_name: str, result_content: str):
        self.history.append({
            "role": "tool",
            "name": function_name,
            "content": str(result_content)
        })

        response = ollama.chat(
            model=self.model_name,
            messages=self.history
        )
        
        msg = response['message']
        self.history.append(msg)
        return msg

    def reset_history(self):
        """Clears chat history while keeping the updated system prompt."""
        system_msg = self.history[0]
        self.history = [system_msg]