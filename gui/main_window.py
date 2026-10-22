import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import unicodedata

from agent.tools import OLLAMA_TOOLS
from agent.client import OllamaAgentManager

# Internal core module imports
from core.audio_processor import AudioProcessor
from core.chord_transposer import ChordTransposer
from core.vocal_range import VocalRangeAnalyzer
from core.setlist import SetlistFormatter
from core.downloader import AudioDownloader
from utils.export_manager import ExportManager

# Global theme configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TransposerApp(ctk.CTk):
    NOTES_MAP = {
        'C': 0, 'C#': 1, 'DB': 1, 'D': 2, 'D#': 3, 'EB': 3,
        'E': 4, 'F': 5, 'F#': 6, 'GB': 6, 'G': 7, 'G#': 8,
        'AB': 8, 'A': 9, 'A#': 10, 'BB': 10, 'B': 11
    }

    def __init__(self):
        super().__init__()
        self.title("Harmoniq AI — Music Production Assistant")
        self.geometry("900x650")
        self.minsize(800, 550)

        # State Variables
        self.file_path: str = ""
        self.current_audio_path: str = ""
        self.current_key: str = "Not detected"
        self.current_bpm = None

        self._build_interface()
        self._initialize_agent()

    # ==========================================
    #  HELPER METHODS AND INTERFACE BUILDER
    # ==========================================
    def _build_interface(self):
        # 1. Header / Banner
        header_frame = ctk.CTkFrame(self, fg_color="#1E1E2E", corner_radius=10)
        header_frame.pack(fill="x", padx=15, pady=(15, 5))

        lbl_title = ctk.CTkLabel(
            header_frame, 
            text="🎵 HARMONIQ AI", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#89B4FA"
        )
        lbl_title.pack(side="left", padx=15, pady=12)

        lbl_subtitle = ctk.CTkLabel(
            header_frame, 
            text="Local Copilot for Music Processing & Chord Charts", 
            font=ctk.CTkFont(size=12),
            text_color="#A6ADC8"
        )
        lbl_subtitle.pack(side="left", padx=5, pady=12)

        # 2. Central Area (Chat / Console Log)
        self.log_text = ctk.CTkTextbox(
            self, 
            corner_radius=10, 
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color="#181825",
            text_color="#CDD6F4"
        )
        self.log_text.pack(expand=True, fill="both", padx=15, pady=10)
        
        self.log_text.insert("1.0", "System ready! Local model connected with audio, chord chart, and metronome support.\n" + ("—"*60) + "\n\n")
        self.log_text.configure(state="disabled")

        # 3. Command Input Panel & Action Buttons
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.entry_prompt = ctk.CTkEntry(
            input_frame, 
            placeholder_text="Enter a command (e.g., 'Lower pitch by 1 semitone' or 'Generate click track at 120 BPM')...",
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=13)
        )
        self.entry_prompt.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.entry_prompt.bind("<Return>", lambda e: self._send_agent_prompt())

        btn_load = ctk.CTkButton(
            input_frame, 
            text="📂 Select Audio", 
            command=self._select_file,
            height=42,
            fg_color="#313244",
            hover_color="#45475A",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        btn_load.pack(side="right", padx=(5, 0))

        btn_send = ctk.CTkButton(
            input_frame, 
            text="Send ➔", 
            command=self._send_agent_prompt,
            height=42,
            fg_color="#89B4FA",
            text_color="#11111B",
            hover_color="#B4BEFE",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        btn_send.pack(side="right")

        # 4. Bottom Status Bar
        status_frame = ctk.CTkFrame(self, height=30, corner_radius=0, fg_color="#11111B")
        status_frame.pack(side="bottom", fill="x")

        self.status_label = ctk.CTkLabel(
            status_frame, 
            text="Status: Awaiting commands...", 
            font=ctk.CTkFont(size=11),
            text_color="#A6ADC8",
            anchor="w"
        )
        self.status_label.pack(side="left", padx=15, pady=2)

    def _initialize_agent(self):
        try:
            tools = [
                self.change_audio_pitch,
                self.change_audio_speed,
                self.separate_audio_stems,
                self.detect_audio_key_and_bpm,
                self.normalize_audio,
                self.trim_audio,
                self.transpose_chord_text,
                self.suggest_vocal_key,
                self.generate_formatted_setlist,
                self.download_audio_link,
                self.export_audio,
                self.export_chord_pdf,
                self.generate_click_track
            ]
            self.agent_manager = OllamaAgentManager(tools_list=tools, model_name="qwen2.5:3b")
            self.log("System ready! Ollama model connected supporting audio, chord chart, vocal, and setlist tools.")
        except Exception as e:
            messagebox.showerror("Ollama Error", f"Failed to connect to local Ollama instance:\n{e}")

    def log(self, message: str):
        """Writes messages to the interface console/chat box."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def update_status(self, text: str):
        """Updates status text on the bottom bar."""
        self.status_label.configure(text=f"Status: {text}")
        self.update_idletasks()

    def _select_file(self):
        path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.ogg *.m4a")]
        )
        if path:
            self.file_path = path
            self.current_audio_path = path
            self.log(f"[File Loaded]: {path}")
            self.update_status(f"Audio loaded: {os.path.basename(path)}")

            # Updates agent context upon file selection
            if hasattr(self, 'agent_manager') and self.agent_manager:
                self.agent_manager.update_system_context(
                    audio_path=path,
                    key=self.current_key,
                    bpm=self.current_bpm
                )

    def _send_agent_prompt(self):
        prompt = self.entry_prompt.get().strip()
        if not prompt:
            return

        self.log(f"\n[You]: {prompt}")
        self.entry_prompt.delete(0, tk.END)
        self.update_status("Agent processing...")
        self.update_idletasks()

        try:
            print("\n--- SENDING REQUEST TO OLLAMA ---")
            response = self.agent_manager.send_message(prompt)
            print("DEBUG RAW OLLAMA RESPONSE:", response)
            self._process_agent_response(response=response, user_message=prompt)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.log(f"[Agent Error]: {e}")
            self.update_status("Execution error.")

    def _normalize_text(self, text: str) -> str:
        if not text:
            return ""
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        return text.lower().strip()

    def _process_agent_response(self, response, user_message: str = ""):
        tools_map = {
            "change_audio_pitch": self.change_audio_pitch,
            "change_audio_speed": self.change_audio_speed,
            "separate_audio_stems": self.separate_audio_stems,
            "detect_audio_key_and_bpm": self.detect_audio_key_and_bpm,
            "normalize_audio": self.normalize_audio,
            "trim_audio": self.trim_audio,
            "download_audio_link": self.download_audio_link,
            "transpose_chord_text": self.transpose_chord_text,
            "suggest_vocal_key": self.suggest_vocal_key,
            "generate_formatted_setlist": self.generate_formatted_setlist,
            "export_audio": self.export_audio,
            "generate_click_track": self.generate_click_track,
            "export_chord_pdf": self.export_chord_pdf
        }

        if hasattr(response, 'model_dump'):
            response_dict = response.model_dump()
        elif isinstance(response, dict):
            response_dict = response
        else:
            response_dict = getattr(response, '__dict__', {})

        tool_calls = response_dict.get('tool_calls') or getattr(response, 'tool_calls', None)
        content = response_dict.get('content') or getattr(response, 'content', "")

        print(f"DEBUG TOOL_CALLS FOUND: {tool_calls}")
        print(f"DEBUG TEXT CONTENT: '{content}'")

        msg_norm = self._normalize_text(user_message)

        # Safety Fallback Interceptions
        if msg_norm:
            export_terms = ["export", "save", "convert", "wav", "mp3"]
            if any(term in msg_norm for term in export_terms) and not any(term in msg_norm for term in ["pdf", "cifra", "chord"]):
                invoked_tool = ""
                if tool_calls:
                    first_tool = tool_calls[0]
                    if isinstance(first_tool, dict):
                        invoked_tool = first_tool.get('function', {}).get('name', '')
                    elif hasattr(first_tool, 'function'):
                        invoked_tool = getattr(first_tool.function, 'name', '')

                if invoked_tool == "change_audio_pitch" or (not tool_calls and not content):
                    target_fmt = "mp3" if "mp3" in msg_norm else "wav"
                    self.log(f"[Local Agent]: Processing direct export to {target_fmt.upper()}...")
                    result = self.export_audio(target_format=target_fmt)
                    self.log(f"[Local Agent]: {result}")
                    self.update_status("Awaiting commands...")
                    return

            if "pdf" in msg_norm or (("cifra" in msg_norm or "chord" in msg_norm) and "export" in msg_norm):
                if not tool_calls and not content:
                    title = "Chord Chart"
                    if "'" in user_message:
                        title = user_message.split("'")[1].strip().title()
                    elif '"' in user_message:
                        title = user_message.split('"')[1].strip().title()

                    key = "C"
                    if "key of " in user_message.lower():
                        key = user_message.lower().split("key of ")[1].split(",")[0].strip().upper()
                    elif "tom de " in user_message.lower():
                        key = user_message.lower().split("tom de ")[1].split(",")[0].strip().upper()

                    minister = "Not informed"
                    if "minister " in user_message.lower():
                        minister = user_message.lower().split("minister ")[1].split(",")[0].title()

                    bpm = "70"
                    if "bpm " in user_message.lower():
                        bpm = user_message.lower().split("bpm ")[1].split(",")[0].strip()

                    chord_text = user_message
                    if "cifra:" in user_message.lower():
                        chord_text = user_message.split("cifra:")[1].strip()
                    elif "chords:" in user_message.lower():
                        chord_text = user_message.split("chords:")[1].strip()

                    self.log("[Local Agent]: Processing direct export of Chord Chart to PDF...")
                    result = self.export_chord_pdf(
                        title=title, key=key, chord_text=chord_text, minister=minister, bpm=bpm
                    )
                    self.log(f"[Local Agent]: {result}")
                    self.update_status("Awaiting commands...")
                    return

        # Execute LLM Tool Calls
        if tool_calls:
            for tool in tool_calls:
                func_name = None
                args = {}

                if isinstance(tool, dict):
                    func_info = tool.get('function', {})
                    func_name = func_info.get('name')
                    args = func_info.get('arguments', {})
                elif hasattr(tool, 'function'):
                    func_name = tool.function.name
                    args = tool.function.arguments

                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception as parse_err:
                        print("Error parsing arguments JSON:", parse_err)

                print(f"DEBUG EXECUTING TOOL: {func_name} WITH ARGS: {args}")

                if func_name in tools_map:
                    self.log(f"[Local Agent]: Invoking `{func_name}`...")
                    self.update_idletasks()
                    
                    try:
                        tool_result = tools_map[func_name](**args)
                        self.log(f"[Tool Result]:\n{tool_result}\n")
                    except Exception as err_tool:
                        tool_result = f"Error executing tool {func_name}: {err_tool}"
                        self.log(f"[Tool Error]: {err_tool}")

                    self.update_idletasks()

                    try:
                        new_response = self.agent_manager.send_tool_response(func_name, str(tool_result))
                        final_text = new_response.get('content', '') if isinstance(new_response, dict) else getattr(new_response, 'content', '')
                        if final_text:
                            self.log(f"[Local Agent]: {final_text}")
                    except Exception as err_ollama:
                        print(f"Error re-sending response to Ollama: {err_ollama}")
                        self.log("[Local Agent]: Operation completed successfully.")
                    
                    self.update_status("Awaiting commands...")
                    return

        if not tool_calls and not content:
            self.log("[Local Agent]: The model did not return a valid response. Try reformulating your request.")
            self.update_status("Awaiting commands...")
            return

        if content:
            self.log(f"[Local Agent]: {content}")
        
        self.update_status("Awaiting commands...")

    # ==========================================
    #  AUDIO & PROCESSING TOOLS
    # ==========================================
    def _get_valid_path(self, provided_path: str = "") -> str:
        if provided_path and os.path.exists(provided_path):
            return provided_path
        if hasattr(self, 'current_audio_path') and self.current_audio_path and os.path.exists(self.current_audio_path):
            return self.current_audio_path
        if hasattr(self, 'file_path') and self.file_path and os.path.exists(self.file_path):
            return self.file_path
        return ""

    def change_audio_pitch(self, input_path: str = "", semitones: int = 0, source_key: str = None, target_key: str = None) -> str:
        if str(input_path).strip().lower() in ["none", "null", "no file loaded", "identified key", "nenhum arquivo carregado", ""]:
            input_path = None

        real_path = self._get_valid_path(input_path)
        if not real_path:
            return "Error: No valid audio file loaded in interface."

        try:
            semitones = int(semitones)
        except (ValueError, TypeError):
            semitones = 0

        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)

        base_name, ext = os.path.splitext(os.path.basename(real_path))
        pitch_suffix = f"{'+' if semitones > 0 else ''}{semitones}st"
        output_filename = f"{base_name}_{pitch_suffix}{ext}"
        output_path = os.path.join(output_dir, output_filename)

        print(f"[DEBUG AUDIO PROCESSING] Reading: '{real_path}' | Writing: '{output_path}' | Semitones: {semitones}")

        try:
            # AudioProcessor Pitch Shift Execution
            AudioProcessor.mudar_tom(caminho_entrada=real_path, semitonos=semitones, caminho_saida=output_path)
            
            # Update active audio paths
            self.current_audio_path = output_path
            self.file_path = output_path
            
            new_key = target_key if (target_key and target_key not in ["Not detected", "Unknown", "Não detectado"]) else self.current_key
            self.current_key = new_key

            # Notify agent manager about context change
            if hasattr(self, "agent_manager") and self.agent_manager:
                self.agent_manager.update_system_context(
                    audio_path=output_path,
                    key=new_key,
                    bpm=self.current_bpm
                )

            return f"Success: Key shift applied by {semitones} semitone(s). File saved in output directory: '{output_filename}'."

        except Exception as e:
            return f"Error processing key shift: {str(e)}"

    def change_audio_speed(self, input_path: str = "", speed_factor: float = 1.0) -> str:
        valid_path = self._get_valid_path(input_path)
        if not valid_path:
            return "Error: No valid audio file for tempo alteration."

        self.update_status(f"[TOOL] Altering tempo of '{os.path.basename(valid_path)}'...")
        return AudioProcessor.alterar_velocidade(valid_path, speed_factor)

    def separate_audio_stems(self, input_path: str = "", mode: str = "2stems") -> str:
        valid_path = self._get_valid_path(input_path)
        if not valid_path:
            return "Error: No valid audio file for stem separation."

        self.update_status(f"[TOOL] Separating stems for '{os.path.basename(valid_path)}'...")
        return AudioProcessor.separar_stems(valid_path, mode)

    def detect_audio_key_and_bpm(self, input_path: str = "") -> str:
        valid_path = self._get_valid_path(input_path)
        if not valid_path:
            return "Error: No valid audio file for key/BPM detection."

        self.update_status(f"[TOOL] Analyzing key and BPM of '{os.path.basename(valid_path)}'...")
        result = AudioProcessor.detectar_tom_e_bpm(valid_path)
        return result

    def normalize_audio(self, input_path: str = "", target_db: float = -14.0) -> str:
        valid_path = self._get_valid_path(input_path)
        if not valid_path:
            return "Error: No valid audio file for volume normalization."

        self.update_status(f"[TOOL] Normalizing '{os.path.basename(valid_path)}' to {target_db} dBFS...")
        return AudioProcessor.normalizar_audio(caminho_entrada=valid_path, decibeis_alvo=target_db)

    def trim_audio(self, start_sec, end_sec, input_path: str = None):
        valid_path = self._get_valid_path(input_path)
        if not valid_path:
            return "Error: No valid audio file for trimming."

        self.update_status(f"[TOOL] Trimming audio from {start_sec} to {end_sec}...")
        return AudioProcessor.cortar_audio(
            caminho_entrada=valid_path, 
            inicio_seg=start_sec, 
            fim_seg=end_sec
        )

    # ==========================================
    #  CHORD, VOCAL AND SETLIST TOOLS
    # ==========================================
    def transpose_chord_text(self, chord_text: str, semitones: float = None, source_key: str = None, target_key: str = None) -> str:
        self.update_status("[TOOL Chord] Transposing chord text...")
        return ChordTransposer.transpor_texto(chord_text, semitonos=semitones, tom_origem=source_key, tom_destino=target_key)

    def suggest_vocal_key(self, original_key: str, song_min_note: str, song_max_note: str, vocal_type_or_min_singer: str, singer_max_note: str = None) -> str:
        self.update_status("[TOOL Vocal] Calculating ideal key based on vocal range...")
        return VocalRangeAnalyzer.sugerir_tom_ideal(
            tom_original=original_key,
            nota_min_musica=song_min_note,
            nota_max_musica=song_max_note,
            tipo_voz_ou_min_cantor=vocal_type_or_min_singer,
            max_cantor=singer_max_note
        )

    def generate_formatted_setlist(self, songs_json_str: str, title: str = "WORSHIP / SHOW SETLIST") -> str:
        self.update_status("[TOOL Setlist] Generating formatted setlist...")
        return SetlistFormatter.parse_e_formatar(songs_json_str, title)
    
    def download_audio_link(self, url: str) -> str:
        if "&list=" in url:
            url = url.split("&list=")[0]
        if "&start_radio=" in url:
            url = url.split("&start_radio=")[0]

        self.update_status(f"[TOOL] Downloading audio from: {url}...")
        try:
            downloaded_path = AudioDownloader.baixar_audio_por_link(url)
            self.file_path = downloaded_path
            self.current_audio_path = downloaded_path
            filename = os.path.basename(downloaded_path)
            self.update_status(f"Active audio: {filename}")

            if hasattr(self, 'agent_manager') and self.agent_manager:
                self.agent_manager.update_system_context(
                    audio_path=downloaded_path,
                    key=self.current_key,
                    bpm=self.current_bpm
                )

            return f"Success: Audio downloaded and set active at '{downloaded_path}'."
        except Exception as e:
            return f"Error downloading audio: {str(e)}"

    def export_audio(self, input_path: str = "", target_format: str = "wav") -> str:
        real_path = self._get_valid_path(input_path)
        if not real_path:
            return "Error: No active audio file to export."

        fmt = str(target_format).lower().replace(".", "").strip()
        if fmt not in ["wav", "mp3"]:
            fmt = "wav"

        try:
            self.update_status(f"[TOOL] Exporting audio to {fmt.upper()}...")
            output_path = ExportManager.converter_audio(real_path, formato_saida=fmt)
            self.file_path = output_path
            self.current_audio_path = output_path
            return f"Success! Audio exported to {fmt.upper()} format saved at: '{output_path}'"
        except Exception as e:
            return f"Error exporting audio: {str(e)}"

    def export_chord_pdf(self, title: str = "Worship Chord Chart", key: str = "", chord_text: str = "", minister: str = "", bpm: str = "") -> str:
        if not chord_text.strip():
            return "Error: No chord chart text provided to generate PDF."
        try:
            self.update_status("[TOOL] Generating Chord Chart PDF...")
            pdf_path = ExportManager.gerar_pdf_cifra(
                titulo=title,
                tom=key,
                texto_cifra=chord_text,
                ministro=minister,
                bpm=bpm
            )
            return f"Success! PDF Chord Chart generated at: '{pdf_path}'."
        except Exception as e:
            return f"Error generating PDF Chord Chart: {str(e)}"

    def generate_click_track(self, bpm: int = 120, time_signature: str = "4/4", duration_minutes: float = 3.0) -> str:
        try:
            bpm = int(bpm)
            duration_minutes = float(duration_minutes)
            time_signature = str(time_signature)
            
            output_path = os.path.join(os.getcwd(), "output", "metronome.wav")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            from tools.audio_tools import gerar_click_track as backend_gerar_click
            
            result = backend_gerar_click(
                bpm=bpm,
                formula=time_signature,
                duracao_minutos=duration_minutes,
                caminho_saida=output_path
            )
            return result

        except Exception as e:
            return f"Error generating click track: {str(e)}"

# ==========================================
#  DIRECT EXECUTION
# ==========================================
if __name__ == "__main__":
    app = TransposerApp()
    app.mainloop()