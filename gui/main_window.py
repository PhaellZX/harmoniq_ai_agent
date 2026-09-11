import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import json
import unicodedata

from agent.tools import FERRAMENTAS_OLLAMA
from agent.client import OllamaAgentManager

# Importações dos módulos internos do projeto
from core.audio_processor import AudioProcessor
from core.chord_transposer import ChordTransposer
from core.vocal_range import VocalRangeAnalyzer
from core.setlist import SetlistFormatter
from agent.client import OllamaAgentManager
from core.downloader import AudioDownloader
from utils.export_manager import ExportManager

# Configuração global de tema
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")  # Opções: "blue", "dark-blue", "green"

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

        self.caminho_arquivo: str = ""
        # Passa a lista de ferramentas declaradas para o agente
        self.agente_manager = OllamaAgentManager(tools_list=FERRAMENTAS_OLLAMA)
        
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
        
        # Mensagem inicial com visual limpo
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
                self.baixar_audio_link
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
            self.log(f"[Arquivo Carregado]: {caminho}")
            self.atualizar_status(f"Áudio carregado: {os.path.basename(caminho)}")

    def _enviar_prompt_agente(self):
        prompt = self.entry_prompt.get().strip()
        if not prompt:
            return

        self.log(f"\n[Você]: {prompt}")
        self.entry_prompt.delete(0, tk.END)
        self.atualizar_status("Agente processando...")

        # Força a atualização da interface gráfica imediatamente
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
        """Remove acentos e converte para minúsculas para facilitar checagens."""
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

        # 1. Extração segura de tool_calls e content
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

        # 2. INTERCEPTAÇÃO E TRAVA DE SEGURANÇA - EXPORTAÇÃO DE ÁUDIO E PDF
        if msg_norm:
            # A) TRAVA DE ÁUDIO
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
                    print(f"DEBUG INTERCEPTAÇÃO ÁUDIO: Executando exportar_audio(formato='{fmt_alvo}')")
                    self.log(f"[Agente Local]: Processando exportação direta para {fmt_alvo.upper()}...")
                    resultado = self.exportar_audio(formato=fmt_alvo)
                    self.log(f"[Agente Local]: {resultado}")
                    self.atualizar_status("Aguardando comandos...")
                    return

            # B) TRAVA DE CIFRA EM PDF
            if "pdf" in msg_norm or ("cifra" in msg_norm and "exportar" in msg_norm):
                if not tool_calls and not content:
                    print("DEBUG INTERCEPTAÇÃO PDF: LLM retornou vazio. Extraindo dados via fallback...")
                    
                    # Extração aprimorada do título da música
                    titulo = "Cifra"
                    msg_lower = mensagem_usuario.lower()
                    
                    if "'" in mensagem_usuario:
                        titulo = mensagem_usuario.split("'")[1].strip().title()
                    elif '"' in mensagem_usuario:
                        titulo = mensagem_usuario.split('"')[1].strip().title()
                    elif "musica " in msg_lower:
                        titulo = msg_lower.split("musica ")[1].split(",")[0].strip().title()

                    tom = "C"
                    if "tom de " in mensagem_usuario.lower():
                        tom = mensagem_usuario.lower().split("tom de ")[1].split(",")[0].strip().upper()

                    ministro = "Não informado"
                    if "ministro " in mensagem_usuario.lower():
                        ministro = mensagem_usuario.lower().split("ministro ")[1].split(",")[0].title()

                    bpm = "70"
                    if "bpm " in mensagem_usuario.lower():
                        bpm = mensagem_usuario.lower().split("bpm ")[1].split(",")[0].strip()

                    # Separa o texto da cifra (tudo após o 'cifra:')
                    texto_cifra = mensagem_usuario
                    if "cifra:" in mensagem_usuario.lower():
                        texto_cifra = mensagem_usuario.split("cifra:")[1].strip()

                    self.log("[Agente Local]: Processando exportação direta da Cifra para PDF...")
                    resultado = self.exportar_cifra_pdf(
                        titulo=titulo,
                        tom=tom,
                        texto_cifra=texto_cifra,
                        ministro=ministro,
                        bpm=bpm
                    )
                    self.log(f"[Agente Local]: {resultado}")
                    self.atualizar_status("Aguardando comandos...")
                    return

            # C) TRAVA DE METRÔNOMO / CLICK TRACK
            if any(term in msg_norm for term in ["metronomo", "metronomo", "click", "clique"]):
                if not tool_calls and not content:
                    print("DEBUG INTERCEPTAÇÃO METRÔNOMO: LLM retornou vazio. Executando fallback...")
                    import re
                    
                    bpm = 120
                    formula = "4/4"
                    duracao = 3.0

                    # Extrai BPM
                    match_bpm = re.search(r'(\d+)\s*bpm', msg_norm)
                    if match_bpm:
                        bpm = int(match_bpm.group(1))

                    # Extrai Fórmula de Compasso
                    match_formula = re.search(r'(\d+/\d+)', msg_norm)
                    if match_formula:
                        formula = match_formula.group(1)

                    # Extrai Duração em minutos
                    match_duracao = re.search(r'(\d+(?:\.\d+)?)\s*minuto', msg_norm)
                    if match_duracao:
                        duracao = float(match_duracao.group(1))

                    self.log(f"[Agente Local]: Gerando Click Track ({bpm} BPM, {formula}, {duracao} min)...")
                    resultado = self.gerar_click_track(bpm=bpm, formula=formula, duracao_minutos=duracao)
                    self.log(f"[Agente Local]: {resultado}")
                    self.atualizar_status("Aguardando comandos...")
                    return

            # D) TRAVA DE NORMALIZAÇÃO DE ÁUDIO
            if any(term in msg_norm for term in ["normaliza", "normalize", "normalizar", "normalizacao"]):
                if not tool_calls and not content:
                    print("DEBUG INTERCEPTAÇÃO NORMALIZAÇÃO: LLM retornou vazio. Executando fallback...")
                    self.log("[Agente Local]: Normalizando volume do áudio ativo...")
                    
                    # Tenta extrair decibéis se o usuário mencionou um número (ex: -14 dB)
                    import re
                    decibeis = -14.0
                    match_db = re.search(r'(-?\d+(?:\.\d+)?)\s*(?:db|decibeis)', msg_norm)
                    if match_db:
                        decibeis = float(match_db.group(1))

                    resultado = self.normalizar_audio(caminho_entrada=getattr(self, 'arquivo_ativo', ''), decibeis_alvo=decibeis)
                    self.log(f"[Agente Local]: {resultado}")
                    self.atualizar_status("Aguardando comandos...")
                    return

        # 3. EXECUÇÃO NORMAL DE TOOL CALLS DA LLM
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

                    print("DEBUG ENVIANDO RESPOSTA DA TOOL DE VOLTA PARA O OLLAMA...")
                    try:
                        # Envia a resposta para o Ollama gerar apenas a mensagem de texto final
                        nova_resposta = self.agente_manager.enviar_resposta_ferramenta(nome_funcao, str(resultado_tool))
                        
                        # Exibe o texto final retornado sem processar chamadas de ferramentas novamente
                        texto_final = nova_resposta.get('content', '') if isinstance(nova_resposta, dict) else getattr(nova_resposta, 'content', '')
                        if texto_final:
                            self.log(f"[Agente Local]: {texto_final}")
                    except Exception as err_ollama:
                        print(f"Erro ao re-enviar resposta ao Ollama: {err_ollama}")
                        self.log("[Agente Local]: Operação concluída com sucesso.")
                    
                    self.atualizar_status("Aguardando comandos...")
                    return # Interrompe imediatamente para evitar qualquer loop

        # 4. FALLBACK GENERALIZADO
        if not tool_calls and not content:
            self.log("[Agente Local]: O modelo não retornou uma resposta válida. Tente reformular a solicitação.")
            self.atualizar_status("Aguardando comandos...")
            return

        # 5. EXIBIÇÃO DE TEXTO NORMAL
        if content:
            self.log(f"[Agente Local]: {content}")
        
        self.atualizar_status("Aguardando comandos...")

    # ==========================================
    #  MÉTODO PRIVADO DE VALIDAÇÃO DE ÁUDIO
    # ==========================================
    def _validar_caminho_audio(self, caminho_entrada: str) -> str:
        """
        Valida se o caminho fornecido existe. Caso a LLM tenha inventado
        um caminho ou o valor seja inválido, busca o arquivo ativo selecionado na GUI.
        """
        if not caminho_entrada or not os.path.exists(caminho_entrada):
            if hasattr(self, 'caminho_arquivo') and self.caminho_arquivo and os.path.exists(self.caminho_arquivo):
                return self.caminho_arquivo
            return ""
        return caminho_entrada

    # ==========================================
    #  FERRAMENTAS DE ÁUDIO (COM TRAVA DE SEGURANÇA)
    # ==========================================

    def _obter_caminho_valido(self, caminho_fornecido: str = "") -> str:
        """
        Retorna o caminho de áudio válido.
        Se a LLM não passar um caminho existente, utiliza o arquivo ativo retido em self.caminho_arquivo.
        """
        import os
        if caminho_fornecido and os.path.exists(caminho_fornecido):
            return caminho_fornecido
        if hasattr(self, 'caminho_arquivo') and self.caminho_arquivo and os.path.exists(self.caminho_arquivo):
            return self.caminho_arquivo
        return ""

    def mudar_tom_audio(self, caminho_entrada: str = "", semitonos: int = 0, tom_origem: str = None, tom_destino: str = None) -> str:
        caminho_real = self._obter_caminho_valido(caminho_entrada)
        if not caminho_real:
            return "Erro: Nenhum arquivo de áudio válido foi carregado na interface para alteração de tom."

        # Mapeamento cromático expandido (Cifras e Português)
        NOTAS_MAP = {
            'C': 0, 'DO': 0,
            'C#': 1, 'DO#': 1, 'DB': 1, 'REB': 1,
            'D': 2, 'RE': 2,
            'D#': 3, 'RE#': 3, 'EB': 3, 'MIB': 3,
            'E': 4, 'MI': 4,
            'F': 5, 'FA': 5,
            'F#': 6, 'FA#': 6, 'GB': 6, 'SOLB': 6,
            'G': 7, 'SOL': 7,
            'G#': 8, 'SOL#': 8, 'AB': 8, 'LALB': 8,
            'A': 9, 'LA': 9,
            'A#': 10, 'LA#': 10, 'BB': 10, 'SIB': 10,
            'B': 11, 'SI': 11
        }

        semitonos_finais = semitonos

        if tom_origem and tom_destino:
            # Sanitiza a string (remove acentos, 'maior', 'menor', espaços)
            import unicodedata
            def normalizar_nota(nota_str: str) -> str:
                s = unicodedata.normalize('NFD', str(nota_str))
                s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
                s = s.upper().replace("MAIOR", "").replace("MENOR", "").replace("M", "").strip()
                return s

            origem_clean = normalizar_nota(tom_origem)
            destino_clean = normalizar_nota(tom_destino)

            if origem_clean in NOTAS_MAP and destino_clean in NOTAS_MAP:
                pos_origem = NOTAS_MAP[origem_clean]
                pos_destino = NOTAS_MAP[destino_clean]
                
                diferenca = pos_destino - pos_origem

                # Busca o caminho de afinação mais próximo (-5 ou +7)
                if diferenca > 6:
                    diferenca -= 12
                elif diferenca < -6:
                    diferenca += 12

                semitonos_finais = diferenca

        if semitonos_finais == 0 and not (tom_origem and tom_destino):
            return "Erro: Informe a quantidade de semitonos ou os tons de origem e destino."

        try:
            self.atualizar_status(f"[TOOL] Transpondo áudio em {semitonos_finais} semitonos...")
            caminho_saida = AudioProcessor.mudar_tom(caminho_real, semitonos_finais)
            
            # Retorna apenas o caminho limpo sem concatenar a string 'Sucesso!' duas vezes
            return f"Sucesso! Tom do áudio ajustado em {semitonos} semitonos e salvo em: '{caminho_saida}'"
        except Exception as e:
            return f"Erro ao processar áudio: {str(e)}"

    def alterar_velocidade_audio(self, caminho_entrada: str, fator_frequencia: float = 1.0) -> str:
        caminho_valido = self._validar_caminho_audio(caminho_entrada)
        if not caminho_valido:
            return "Erro: Nenhum arquivo de áudio válido foi carregado na interface para alteração de velocidade."

        self.atualizar_status(f"[TOOL] Alterando velocidade de '{os.path.basename(caminho_valido)}' (Fator: {fator_frequencia}x)...")
        return AudioProcessor.alterar_velocidade(caminho_valido, fator_frequencia)

    def separar_stems_audio(self, caminho_entrada: str, modo: str = "2stems") -> str:
        caminho_valido = self._validar_caminho_audio(caminho_entrada)
        if not caminho_valido:
            return "Erro: Nenhum arquivo de áudio válido foi carregado na interface para separação de stems."

        self.atualizar_status(f"[TOOL] Separando stems de '{os.path.basename(caminho_valido)}' (Modo: {modo})...")
        return AudioProcessor.separar_stems(caminho_valido, modo)

    def detectar_tom_e_bpm_audio(self, caminho_entrada: str) -> str:
        caminho_valido = self._validar_caminho_audio(caminho_entrada)
        if not caminho_valido:
            return "Erro: Nenhum arquivo de áudio válido foi carregado na interface para detecção de tom/BPM."

        self.atualizar_status(f"[TOOL] Analisando tom e BPM de '{os.path.basename(caminho_valido)}'...")
        return AudioProcessor.detectar_tom_e_bpm(caminho_valido)

    def normalizar_audio(self, caminho_entrada: str, decibeis_alvo: float = -14.0) -> str:
        caminho_valido = self._validar_caminho_audio(caminho_entrada)
        if not caminho_valido:
            return "Erro: Nenhum arquivo de áudio válido foi carregado na interface para normalização."

        self.atualizar_status(f"[TOOL] Normalizando '{os.path.basename(caminho_valido)}' para {decibeis_alvo} dBFS...")
        return AudioProcessor.normalizar_audio(caminho_entrada=caminho_valido, decibeis_alvo=decibeis_alvo)

    def cortar_audio(self, caminho_entrada: str, inicio_seg: float, fim_seg: float) -> str:
        caminho_valido = self._validar_caminho_audio(caminho_entrada)
        if not caminho_valido:
            return "Erro: Nenhum arquivo de áudio válido foi carregado na interface para corte."

        self.atualizar_status(f"[TOOL] Cortando '{os.path.basename(caminho_valido)}' de {inicio_seg}s a {fim_seg}s...")
        return AudioProcessor.cortar(caminho_valido, inicio_seg, fim_seg)

    # ==========================================
    #  FERRAMENTAS DE CIFRA, VOCAL E SETLIST
    # ==========================================
    def transpor_cifra_texto(self, texto_cifra: str, semitonos: float = None, tom_origem: str = None, tom_destino: str = None) -> str:
        self.atualizar_status("[TOOL Cifra] Transpondo texto da cifra...")
        # Corrigido: usa ChordTransposer conforme o import
        return ChordTransposer.transpor_texto(texto_cifra, semitonos=semitonos, tom_origem=tom_origem, tom_destino=tom_destino)

    def sugerir_tom_ideal_vocal(self, tom_original: str, nota_min_musica: str, nota_max_musica: str, tipo_voz_ou_min_cantor: str, max_cantor: str = None) -> str:
        self.atualizar_status("[TOOL Vocal] Calculando tom ideal com base na extensão vocal...")
        # Corrigido: usa VocalRangeAnalyzer conforme o import
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
        # Sanitiza a URL removendo parâmetros de playlist/rádio
        if "&list=" in url:
            url = url.split("&list=")[0]
        if "&start_radio=" in url:
            url = url.split("&start_radio=")[0]

        self.atualizar_status(f"[TOOL] Baixando áudio de: {url}...")
        try:
            caminho_baixado = AudioDownloader.baixar_audio_por_link(url)
            
            # Registra o arquivo baixado como o ativo na interface
            self.caminho_arquivo = caminho_baixado
            nome_arquivo = os.path.basename(caminho_baixado)
            self.atualizar_status(f"Áudio ativo: {nome_arquivo}")

            return f"Sucesso: Áudio baixado e definido como ativo em '{caminho_baixado}'."
        except Exception as e:
            return f"Erro ao baixar áudio: {str(e)}"

    def exportar_audio(self, caminho_entrada: str = "", formato: str = "wav") -> str:
        caminho_real = self._obter_caminho_valido(caminho_entrada)
        if not caminho_real:
            return "Erro: Nenhum arquivo de áudio ativo para exportação."

        # Sanitiza o formato informado (garante minusculas e remove pontos)
        fmt = str(formato).lower().replace(".", "").strip()
        if fmt not in ["wav", "mp3"]:
            fmt = "wav"  # Padrão de saída do ensaio

        try:
            self.atualizar_status(f"[TOOL] Exportando áudio para {fmt.upper()}...")
            caminho_saida = ExportManager.converter_audio(caminho_real, formato_saida=fmt)
            
            # Atualiza o arquivo ativo para a nova versão exportada
            self.caminho_arquivo = caminho_saida
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
        """
        Método chamado pela GUI / LLM para gerar o arquivo de metrônomo.
        """
        try:
            # Garante a conversão dos tipos de dados
            bpm = int(bpm)
            duracao_minutos = float(duracao_minutos)
            formula = str(formula)
            
            caminho_saida = "output/metronomo.wav"
            
            # Chama a função técnica do backend de áudio
            # (Ajuste a importação/chamada conforme o módulo onde você colocou a função técnica)
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

    def reiniciar_historico(self):
        """Reseta o histórico de conversas mantendo apenas o System Prompt original."""
        system_msg = self.historico[0]
        self.historico = [system_msg]

# ==========================================
#  EXECUÇÃO DIRETA
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = TransposerApp(root)
    root.mainloop()