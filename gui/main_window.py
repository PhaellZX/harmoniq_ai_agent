import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import unicodedata

from agent.tools import FERRAMENTAS_OLLAMA
from agent.client import OllamaAgentManager

# Importações dos módulos internos do projeto
from core.audio_processor import AudioProcessor
from core.chord_transposer import ChordTransposer
from core.vocal_range import VocalRangeAnalyzer
from core.setlist import SetlistFormatter
from core.downloader import AudioDownloader
from utils.export_manager import ExportManager

# Configuração global de tema
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TransposerApp(ctk.CTk):
    NOTAS_MAP = {
        'C': 0, 'C#': 1, 'DB': 1, 'D': 2, 'D#': 3, 'EB': 3,
        'E': 4, 'F': 5, 'F#': 6, 'GB': 6, 'G': 7, 'G#': 8,
        'AB': 8, 'A': 9, 'A#': 10, 'BB': 10, 'B': 11
    }

    def __init__(self):
        super().__init__()
        self.title("Harmoniq AI — Assistente de Produção Musical")
        self.geometry("900x650")
        self.minsize(800, 550)

        # Variáveis de Estado
        self.caminho_arquivo: str = ""
        self.caminho_audio_atual: str = ""
        self.tom_atual: str = "Não detectado"
        self.bpm_atual = None

        self._construir_interface()
        self._inicializar_agente()

    # ==========================================
    #  MÉTODOS AUXILIARES E INTERFACE
    # ==========================================
    def _construir_interface(self):
        # 1. Cabeçalho / Banner
        header_frame = ctk.CTkFrame(self, fg_color="#1E1E2E", corner_radius=10)
        header_frame.pack(fill="x", padx=15, pady=(15, 5))

        lbl_titulo = ctk.CTkLabel(
            header_frame, 
            text="🎵 HARMONIQ AI", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#89B4FA"
        )
        lbl_titulo.pack(side="left", padx=15, pady=12)

        lbl_subtitulo = ctk.CTkLabel(
            header_frame, 
            text="Copiloto Local de Processamento Musical & Cifras", 
            font=ctk.CTkFont(size=12),
            text_color="#A6ADC8"
        )
        lbl_subtitulo.pack(side="left", padx=5, pady=12)

        # 2. Área Central (Chat / Console Log)
        self.log_text = ctk.CTkTextbox(
            self, 
            corner_radius=10, 
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color="#181825",
            text_color="#CDD6F4"
        )
        self.log_text.pack(expand=True, fill="both", padx=15, pady=10)
        
        self.log_text.insert("1.0", "Sistema pronto! Modelo local conectado com suporte a áudio, cifras e metrônomo.\n" + ("—"*60) + "\n\n")
        self.log_text.configure(state="disabled")

        # 3. Painel de Entrada de Comandos e Ações
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.entry_prompt = ctk.CTkEntry(
            input_frame, 
            placeholder_text="Digite um comando (ex: 'Mude o tom para D' ou 'Gere um metrônomo 120 BPM')...",
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=13)
        )
        self.entry_prompt.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.entry_prompt.bind("<Return>", lambda e: self._enviar_prompt_agente())

        btn_carregar = ctk.CTkButton(
            input_frame, 
            text="📂 Selecionar Áudio", 
            command=self._selecionar_arquivo,
            height=42,
            fg_color="#313244",
            hover_color="#45475A",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        btn_carregar.pack(side="right", padx=(5, 0))

        btn_enviar = ctk.CTkButton(
            input_frame, 
            text="Enviar ➔", 
            command=self._enviar_prompt_agente,
            height=42,
            fg_color="#89B4FA",
            text_color="#11111B",
            hover_color="#B4BEFE",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        btn_enviar.pack(side="right")

        # 4. Barra de Status Inferior
        status_frame = ctk.CTkFrame(self, height=30, corner_radius=0, fg_color="#11111B")
        status_frame.pack(side="bottom", fill="x")

        self.status_label = ctk.CTkLabel(
            status_frame, 
            text="Status: Aguardando comandos...", 
            font=ctk.CTkFont(size=11),
            text_color="#A6ADC8",
            anchor="w"
        )
        self.status_label.pack(side="left", padx=15, pady=2)

    def _inicializar_agente(self):
        try:
            tools = [
                self.mudar_tom_audio,
                self.alterar_velocidade_audio,
                self.separar_stems_audio,
                self.detectar_tom_e_bpm_audio,
                self.normalizar_audio,
                self.cortar_audio,
                self.transpor_cifra_texto,
                self.sugerir_tom_ideal_vocal,
                self.gerar_setlist_formatada,
                self.baixar_audio_link,
                self.exportar_audio,
                self.exportar_cifra_pdf,
                self.gerar_click_track
            ]
            self.agent_manager = OllamaAgentManager(tools_list=tools, model_name="qwen2.5:3b")
            self.log("Sistema pronto! Modelo Ollama conectado com suporte a ferramentas de áudio, cifra, voz e setlists.")
        except Exception as e:
            messagebox.showerror("Erro Ollama", f"Falha ao conectar ao Ollama local:\n{e}")

    def log(self, mensagem: str):
        """Escreve mensagens no console/chat da interface."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", mensagem + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def atualizar_status(self, texto: str):
        """Atualiza o texto da barra de status inferior."""
        self.status_label.configure(text=f"Status: {texto}")
        self.update_idletasks()

    def _selecionar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo de áudio",
            filetypes=[("Arquivos de Áudio", "*.mp3 *.wav *.flac *.ogg *.m4a")]
        )
        if caminho:
            self.caminho_arquivo = caminho
            self.caminho_audio_atual = caminho
            self.log(f"[Arquivo Carregado]: {caminho}")
            self.atualizar_status(f"Áudio carregado: {os.path.basename(caminho)}")

            # Atualiza o contexto do agente no instante do carregamento do arquivo
            if hasattr(self, 'agent_manager') and self.agent_manager:
                self.agent_manager.atualizar_contexto_sistema(
                    caminho_audio=caminho,
                    tom=self.tom_atual,
                    bpm=self.bpm_atual
                )

    def _enviar_prompt_agente(self):
        prompt = self.entry_prompt.get().strip()
        if not prompt:
            return

        self.log(f"\n[Você]: {prompt}")
        self.entry_prompt.delete(0, tk.END)
        self.atualizar_status("Agente processando...")
        self.update_idletasks()

        try:
            print("\n--- INICIANDO ENVIO PARA O OLLAMA ---")
            resposta = self.agent_manager.enviar_mensagem(prompt)
            print("DEBUG RESPOSTA BRUTA OLLAMA:", resposta)
            self._processar_resposta_agente(resposta=resposta, mensagem_usuario=prompt)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.log(f"[Erro Agente]: {e}")
            self.atualizar_status("Erro na execução.")

    def _normalizar_texto(self, texto: str) -> str:
        if not texto:
            return ""
        texto = unicodedata.normalize('NFD', texto)
        texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
        return texto.lower().strip()

    def _processar_resposta_agente(self, resposta, mensagem_usuario: str = ""):
        ferramentas_map = {
            "mudar_tom_audio": self.mudar_tom_audio,
            "alterar_velocidade_audio": self.alterar_velocidade_audio,
            "separar_stems_audio": self.separar_stems_audio,
            "detectar_tom_e_bpm_audio": self.detectar_tom_e_bpm_audio,
            "normalizar_audio": self.normalizar_audio,
            "cortar_audio": self.cortar_audio,
            "baixar_audio_link": self.baixar_audio_link,
            "transpor_cifra_texto": self.transpor_cifra_texto,
            "sugerir_tom_ideal_vocal": self.sugerir_tom_ideal_vocal,
            "gerar_setlist_formatada": self.gerar_setlist_formatada,
            "exportar_audio": self.exportar_audio,
            "gerar_click_track": self.gerar_click_track,
            "exportar_cifra_pdf": self.exportar_cifra_pdf
        }

        if hasattr(resposta, 'model_dump'):
            resposta_dict = resposta.model_dump()
        elif isinstance(resposta, dict):
            resposta_dict = resposta
        else:
            resposta_dict = getattr(resposta, '__dict__', {})

        tool_calls = resposta_dict.get('tool_calls') or getattr(resposta, 'tool_calls', None)
        content = resposta_dict.get('content') or getattr(resposta, 'content', "")

        print(f"DEBUG TOOL_CALLS ENCONTRADAS: {tool_calls}")
        print(f"DEBUG CONTEÚDO TEXTO: '{content}'")

        msg_norm = self._normalizar_texto(mensagem_usuario)

        # Interceptações de Trava de Segurança
        if msg_norm:
            termos_exportacao_audio = ["exporta", "exportar", "wav", "mp3", "salvar", "converte", "convert"]
            if any(term in msg_norm for term in termos_exportacao_audio) and not any(term in msg_norm for term in ["pdf", "cifra"]):
                nome_tool_invocada = ""
                if tool_calls:
                    primeira_tool = tool_calls[0]
                    if isinstance(primeira_tool, dict):
                        nome_tool_invocada = primeira_tool.get('function', {}).get('name', '')
                    elif hasattr(primeira_tool, 'function'):
                        nome_tool_invocada = getattr(primeira_tool.function, 'name', '')

                if nome_tool_invocada == "mudar_tom_audio" or (not tool_calls and not content):
                    fmt_alvo = "mp3" if "mp3" in msg_norm else "wav"
                    self.log(f"[Agente Local]: Processando exportação direta para {fmt_alvo.upper()}...")
                    resultado = self.exportar_audio(formato=fmt_alvo)
                    self.log(f"[Agente Local]: {resultado}")
                    self.atualizar_status("Aguardando comandos...")
                    return

            if "pdf" in msg_norm or ("cifra" in msg_norm and "exportar" in msg_norm):
                if not tool_calls and not content:
                    titulo = "Cifra"
                    if "'" in mensagem_usuario:
                        titulo = mensagem_usuario.split("'")[1].strip().title()
                    elif '"' in mensagem_usuario:
                        titulo = mensagem_usuario.split('"')[1].strip().title()

                    tom = "C"
                    if "tom de " in mensagem_usuario.lower():
                        tom = mensagem_usuario.lower().split("tom de ")[1].split(",")[0].strip().upper()

                    ministro = "Não informado"
                    if "ministro " in mensagem_usuario.lower():
                        ministro = mensagem_usuario.lower().split("ministro ")[1].split(",")[0].title()

                    bpm = "70"
                    if "bpm " in mensagem_usuario.lower():
                        bpm = mensagem_usuario.lower().split("bpm ")[1].split(",")[0].strip()

                    texto_cifra = mensagem_usuario
                    if "cifra:" in mensagem_usuario.lower():
                        texto_cifra = mensagem_usuario.split("cifra:")[1].strip()

                    self.log("[Agente Local]: Processando exportação direta da Cifra para PDF...")
                    resultado = self.exportar_cifra_pdf(
                        titulo=titulo, tom=tom, texto_cifra=texto_cifra, ministro=ministro, bpm=bpm
                    )
                    self.log(f"[Agente Local]: {resultado}")
                    self.atualizar_status("Aguardando comandos...")
                    return

        # Execução das Chamadas de Ferramentas da LLM
        if tool_calls:
            for tool in tool_calls:
                nome_funcao = None
                argumentos = {}

                if isinstance(tool, dict):
                    funcao_info = tool.get('function', {})
                    nome_funcao = funcao_info.get('name')
                    argumentos = funcao_info.get('arguments', {})
                elif hasattr(tool, 'function'):
                    nome_funcao = tool.function.name
                    argumentos = tool.function.arguments

                if isinstance(argumentos, str):
                    try:
                        argumentos = json.loads(argumentos)
                    except Exception as parse_err:
                        print("Erro ao converter JSON de argumentos:", parse_err)

                print(f"DEBUG EXECUTANDO TOOL: {nome_funcao} COM ARGS: {argumentos}")

                if nome_funcao in ferramentas_map:
                    self.log(f"[Agente Local]: Invocando `{nome_funcao}`...")
                    self.update_idletasks()
                    
                    try:
                        resultado_tool = ferramentas_map[nome_funcao](**argumentos)
                        self.log(f"[Resultado Tool]:\n{resultado_tool}\n")
                    except Exception as err_tool:
                        resultado_tool = f"Erro ao executar a ferramenta {nome_funcao}: {err_tool}"
                        self.log(f"[Erro Tool]: {err_tool}")

                    self.update_idletasks()

                    try:
                        nova_resposta = self.agent_manager.enviar_resposta_ferramenta(nome_funcao, str(resultado_tool))
                        texto_final = nova_resposta.get('content', '') if isinstance(nova_resposta, dict) else getattr(nova_resposta, 'content', '')
                        if texto_final:
                            self.log(f"[Agente Local]: {texto_final}")
                    except Exception as err_ollama:
                        print(f"Erro ao re-enviar resposta ao Ollama: {err_ollama}")
                        self.log("[Agente Local]: Operação concluída com sucesso.")
                    
                    self.atualizar_status("Aguardando comandos...")
                    return

        if not tool_calls and not content:
            self.log("[Agente Local]: O modelo não retornou uma resposta válida. Tente reformular a solicitação.")
            self.atualizar_status("Aguardando comandos...")
            return

        if content:
            self.log(f"[Agente Local]: {content}")
        
        self.atualizar_status("Aguardando comandos...")

    # ==========================================
    #  FERRAMENTAS DE ÁUDIO & PROCESSAMENTO
    # ==========================================
    def _obter_caminho_valido(self, caminho_fornecido: str = "") -> str:
        if caminho_fornecido and os.path.exists(caminho_fornecido):
            return caminho_fornecido
        if hasattr(self, 'caminho_audio_atual') and self.caminho_audio_atual and os.path.exists(self.caminho_audio_atual):
            return self.caminho_audio_atual
        if hasattr(self, 'caminho_arquivo') and self.caminho_arquivo and os.path.exists(self.caminho_arquivo):
            return self.caminho_arquivo
        return ""

    def mudar_tom_audio(self, caminho_entrada: str = "", semitonos: int = 0, tom_origem: str = None, tom_destino: str = None) -> str:
        if str(caminho_entrada).strip().lower() in ["none", "null", "nenhum arquivo carregado", "tom identificado", ""]:
            caminho_entrada = None

        caminho_real = self._obter_caminho_valido(caminho_entrada)
        if not caminho_real:
            return "Erro: Nenhum arquivo de áudio válido carregado na interface."

        try:
            semitonos = int(semitonos)
        except (ValueError, TypeError):
            semitonos = 0

        pasta_output = os.path.join(os.getcwd(), "output")
        os.makedirs(pasta_output, exist_ok=True)

        nome_base, ext = os.path.splitext(os.path.basename(caminho_real))
        sufixo_tom = f"{'+' if semitonos > 0 else ''}{semitonos}st"
        nome_arquivo_saida = f"{nome_base}_{sufixo_tom}{ext}"
        caminho_saida = os.path.join(pasta_output, nome_arquivo_saida)

        print(f"[DEBUG PROCESSAMENTO AUDIO] Lendo: '{caminho_real}' | Gerando em: '{caminho_saida}' | Semitonos: {semitonos}")

        try:
            # Execução real do Pitch Shift chamando o AudioProcessor
            AudioProcessor.mudar_tom(caminho_entrada=caminho_real, semitonos=semitonos, caminho_saida=caminho_saida)
            
            # Atualiza os caminhos de áudio ativo
            self.caminho_audio_atual = caminho_saida
            self.caminho_arquivo = caminho_saida
            
            novo_tom = tom_destino if (tom_destino and tom_destino not in ["Não detectado", "Desconhecido"]) else self.tom_atual
            self.tom_atual = novo_tom

            # Notifica o agent_manager sobre a mudança do áudio ativo
            if hasattr(self, "agent_manager") and self.agent_manager:
                self.agent_manager.atualizar_contexto_sistema(
                    caminho_audio=caminho_saida,
                    tom=novo_tom,
                    bpm=self.bpm_atual
                )

            return f"Sucesso: Tom alterado em {semitonos} semitom(s). Arquivo salvo na pasta output: '{nome_arquivo_saida}'."

        except Exception as e:
            return f"Erro ao processar alteração de tom: {str(e)}"

    def alterar_velocidade_audio(self, caminho_entrada: str = "", fator_frequencia: float = 1.0) -> str:
        caminho_valido = self._obter_caminho_valido(caminho_entrada)
        if not caminho_valido:
            return "Erro: Nenhum arquivo de áudio válido para alteração de velocidade."

        self.atualizar_status(f"[TOOL] Alterando velocidade de '{os.path.basename(caminho_valido)}'...")
        return AudioProcessor.alterar_velocidade(caminho_valido, fator_frequencia)

    def separar_stems_audio(self, caminho_entrada: str = "", modo: str = "2stems") -> str:
        caminho_valido = self._obter_caminho_valido(caminho_entrada)
        if not caminho_valido:
            return "Erro: Nenhum arquivo de áudio válido para separação de stems."

        self.atualizar_status(f"[TOOL] Separando stems de '{os.path.basename(caminho_valido)}'...")
        return AudioProcessor.separar_stems(caminho_valido, modo)

    def detectar_tom_e_bpm_audio(self, caminho_entrada: str = "") -> str:
        caminho_valido = self._obter_caminho_valido(caminho_entrada)
        if not caminho_valido:
            return "Erro: Nenhum arquivo de áudio válido para detecção de tom/BPM."

        self.atualizar_status(f"[TOOL] Analisando tom e BPM de '{os.path.basename(caminho_valido)}'...")
        resultado = AudioProcessor.detectar_tom_e_bpm(caminho_valido)
        return resultado

    def normalizar_audio(self, caminho_entrada: str = "", decibeis_alvo: float = -14.0) -> str:
        caminho_valido = self._obter_caminho_valido(caminho_entrada)
        if not caminho_valido:
            return "Erro: Nenhum arquivo de áudio válido para normalização."

        self.atualizar_status(f"[TOOL] Normalizando '{os.path.basename(caminho_valido)}' para {decibeis_alvo} dBFS...")
        return AudioProcessor.normalizar_audio(caminho_entrada=caminho_valido, decibeis_alvo=decibeis_alvo)

    def cortar_audio(self, inicio_seg, fim_seg, caminho_entrada: str = None):
        caminho_valido = self._obter_caminho_valido(caminho_entrada)
        if not caminho_valido:
            return "Erro: Nenhum arquivo de áudio válido para corte."

        self.atualizar_status(f"[TOOL] Cortando áudio de {inicio_seg} até {fim_seg}...")
        return AudioProcessor.cortar_audio(
            caminho_entrada=caminho_valido, 
            inicio_seg=inicio_seg, 
            fim_seg=fim_seg
        )

    # ==========================================
    #  FERRAMENTAS DE CIFRA, VOCAL E SETLIST
    # ==========================================
    def transpor_cifra_texto(self, texto_cifra: str, semitonos: float = None, tom_origem: str = None, tom_destino: str = None) -> str:
        self.atualizar_status("[TOOL Cifra] Transpondo texto da cifra...")
        return ChordTransposer.transpor_texto(texto_cifra, semitonos=semitonos, tom_origem=tom_origem, tom_destino=tom_destino)

    def sugerir_tom_ideal_vocal(self, tom_original: str, nota_min_musica: str, nota_max_musica: str, tipo_voz_ou_min_cantor: str, max_cantor: str = None) -> str:
        self.atualizar_status("[TOOL Vocal] Calculando tom ideal com base na extensão vocal...")
        return VocalRangeAnalyzer.sugerir_tom_ideal(
            tom_original=tom_original,
            nota_min_musica=nota_min_musica,
            nota_max_musica=nota_max_musica,
            tipo_voz_ou_min_cantor=tipo_voz_ou_min_cantor,
            max_cantor=max_cantor
        )

    def gerar_setlist_formatada(self, json_musicas_str: str, titulo: str = "SETLIST DO CULTO / SHOW") -> str:
        self.atualizar_status("[TOOL Setlist] Gerando setlist padronizada...")
        return SetlistFormatter.parse_e_formatar(json_musicas_str, titulo)
    
    def baixar_audio_link(self, url: str) -> str:
        if "&list=" in url:
            url = url.split("&list=")[0]
        if "&start_radio=" in url:
            url = url.split("&start_radio=")[0]

        self.atualizar_status(f"[TOOL] Baixando áudio de: {url}...")
        try:
            caminho_baixado = AudioDownloader.baixar_audio_por_link(url)
            self.caminho_arquivo = caminho_baixado
            self.caminho_audio_atual = caminho_baixado
            nome_arquivo = os.path.basename(caminho_baixado)
            self.atualizar_status(f"Áudio ativo: {nome_arquivo}")

            if hasattr(self, 'agent_manager') and self.agent_manager:
                self.agent_manager.atualizar_contexto_sistema(
                    caminho_audio=caminho_baixado,
                    tom=self.tom_atual,
                    bpm=self.bpm_atual
                )

            return f"Sucesso: Áudio baixado e definido como ativo em '{caminho_baixado}'."
        except Exception as e:
            return f"Erro ao baixar áudio: {str(e)}"

    def exportar_audio(self, caminho_entrada: str = "", formato: str = "wav") -> str:
        caminho_real = self._obter_caminho_valido(caminho_entrada)
        if not caminho_real:
            return "Erro: Nenhum arquivo de áudio ativo para exportação."

        fmt = str(formato).lower().replace(".", "").strip()
        if fmt not in ["wav", "mp3"]:
            fmt = "wav"

        try:
            self.atualizar_status(f"[TOOL] Exportando áudio para {fmt.upper()}...")
            caminho_saida = ExportManager.converter_audio(caminho_real, formato_saida=fmt)
            self.caminho_arquivo = caminho_saida
            self.caminho_audio_atual = caminho_saida
            return f"Sucesso! Áudio exportado em formato {fmt.upper()} salvo em: '{caminho_saida}'"
        except Exception as e:
            return f"Erro ao exportar áudio: {str(e)}"

    def exportar_cifra_pdf(self, titulo: str = "Cifra de Louvor", tom: str = "", texto_cifra: str = "", ministro: str = "", bpm: str = "") -> str:
        if not texto_cifra.strip():
            return "Erro: Não há texto de cifra para gerar o PDF."
        try:
            self.atualizar_status("[TOOL] Gerando PDF da cifra...")
            caminho_pdf = ExportManager.gerar_pdf_cifra(
                titulo=titulo,
                tom=tom,
                texto_cifra=texto_cifra,
                ministro=ministro,
                bpm=bpm
            )
            return f"Sucesso! Cifra em PDF gerada em: '{caminho_pdf}'."
        except Exception as e:
            return f"Erro ao gerar PDF da cifra: {str(e)}"

    def gerar_click_track(self, bpm: int = 120, formula: str = "4/4", duracao_minutos: float = 3.0) -> str:
        try:
            bpm = int(bpm)
            duracao_minutos = float(duracao_minutos)
            formula = str(formula)
            
            caminho_saida = os.path.join(os.getcwd(), "output", "metronomo.wav")
            os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
            
            from tools.audio_tools import gerar_click_track as backend_gerar_click
            
            resultado = backend_gerar_click(
                bpm=bpm,
                formula=formula,
                duracao_minutos=duracao_minutos,
                caminho_saida=caminho_saida
            )
            return resultado

        except Exception as e:
            return f"Erro ao executar geração de click track: {str(e)}"

# ==========================================
#  EXECUÇÃO DIRETA
# ==========================================
if __name__ == "__main__":
    app = TransposerApp()
    app.mainloop()