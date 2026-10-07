import ollama

class OllamaAgentManager:
    def __init__(self, tools_list, model_name: str = "qwen2.5:3b"):
        self.model_name = model_name
        self.tools = tools_list
        self.caminho_audio_atual = None
        self.tom_atual = None
        self.bpm_atual = None
        self.historico = []
        
        # Inicializa o prompt base do sistema
        self.atualizar_contexto_sistema()

    def atualizar_contexto_sistema(self, caminho_audio: str = None, tom: str = None, bpm: float = None):
        """Atualiza o estado atual do áudio e reconstrói a mensagem de sistema."""
        if caminho_audio is not None:
            self.caminho_audio_atual = caminho_audio
        if tom is not None:
            self.tom_atual = tom
        if bpm is not None:
            self.bpm_atual = bpm

        # Valores formatados para injeção direta (evita que o Qwen copie placeholders literais)
        audio_val = self.caminho_audio_atual or "Nenhum arquivo carregado"
        tom_val = self.tom_atual or "Não detectado"
        bpm_val = str(self.bpm_atual) if self.bpm_atual else "Não detectado"

        system_content = (
            "Você é um assistente de produção musical, arranjo e vocal direto, pragmático e conciso.\n\n"
            "=== ESTADO ATUAL DO ÁUDIO NA INTERFACE ===\n"
            f"- Arquivo Ativo: {audio_val}\n"
            f"- Tom Identificado: {tom_val}\n"
            f"- BPM Identificado: {bpm_val}\n\n"
            "REGRAS DE CONTEXTO OBRIGATÓRIAS:\n"
            f"- Sempre que chamar ferramentas de áudio, passe no argumento `caminho_entrada` o valor EXATO do Arquivo Ativo: '{audio_val}'. NUNCA passe 'None' ou caminhos genéricos como 'arquivo.mp3'.\n"
            f"- Para `mudar_tom_audio`, se o usuário não disser o tom original, use EXATAMENTE o Tom Identificado atual: '{tom_val}'. NUNCA passe a string literal 'Tom Identificado'.\n\n"
            "SUAS FERRAMENTAS DE ÁUDIO:\n"
            "1. `mudar_tom_audio(caminho_entrada, semitonos, tom_origem, tom_destino)` -> Use EXCLUSIVAMENTE quando o usuário pedir para alterar o tom, afinação ou semitonos do áudio.\n"
            "   ATENÇÃO À MATEMÁTICA DOS SEMITONOS (ESCALA CROMÁTICA: C, C#, D, D#, E, F, F#, G, G#, A, A#, B):\n"
            "   - Cada semitono equivale a meio tom. 1 semitono = C para C#.\n"
            "   - 2 semitonos equivalem a 1 tom inteiro (ex: C + 2 semitonos = D; G + 2 semitonos = A).\n"
            "   - DIMINUIR/BAIXAR o tom -> `semitonos` DEVE SER NEGATIVO (Ex: diminuir 1 semitono = -1; diminuir 1 tom = -2).\n"
            "   - AUMENTAR/SUBIR o tom -> `semitonos` DEVE SER POSITIVO (Ex: aumentar 1 semitono = 1; aumentar 1 tom = 2).\n"
            "   - Garanta que `tom_destino` corresponda EXATAMENTE à quantidade de `semitonos` em relação ao `tom_origem` (Ex: De Ab com semitonos -1, o tom_destino é G).\n\n"
            "2. `alterar_velocidade_audio(caminho_entrada, fator_frequencia)` -> Use para alterar a velocidade/tempo do áudio.\n"
            "3. `separar_stems_audio(caminho_entrada, modo)` -> Use para separar faixas/instrumentos de um áudio.\n"
            "4. `detectar_tom_e_bpm_audio(caminho_entrada)` -> Use para analisar o tom e o BPM de um arquivo de áudio.\n"
            "5. `normalizar_audio(caminho_entrada, decibeis_alvo)` -> Use para ajustar o volume relativo do áudio.\n"
            "6. `cortar_audio(caminho_entrada, inicio_seg, fim_seg)` -> Use para recortar trechos do arquivo de áudio.\n\n"
            "SUA FERRAMENTA DE DOWNLOAD:\n"
            "7. `baixar_audio_link(url)` -> Use para baixar áudios via URL/link de plataformas como YouTube ou Drive.\n\n"
            "SUAS FERRAMENTAS DE CIFRA E VOZ:\n"
            "8. `transpor_cifra_texto(texto_cifra, semitonos, tom_origem, tom_destino)` -> Use para alterar o tom de cifras em texto escrito.\n"
            "9. `sugerir_tom_ideal_vocal(tom_original, nota_min_musica, nota_max_musica, tipo_voz_ou_min_cantor, max_cantor)` -> Use APENAS quando o usuário pedir explicitamente análise da extensão ou alcance vocal de um cantor/cantora.\n\n"
            "SUA FERRAMENTA DE SETLIST:\n"
            "10. `gerar_setlist_formatada(json_musicas_str, titulo)` -> Use para formatar e organizar listas de músicas do culto.\n\n"
            "SUAS FERRAMENTAS DE EXPORTAÇÃO E METRÔNOMO:\n"
            "11. `exportar_audio(caminho_entrada, formato)` -> Use para converter ou salvar o áudio ativo nos formatos 'wav' ou 'mp3'. NÃO altera a afinação nem a velocidade do áudio.\n"
            "12. `exportar_cifra_pdf(titulo, tom, texto_cifra, ministro, bpm)` -> Use para gerar um arquivo PDF formatado e estilizado de uma cifra para ensaios.\n"
            "13. `gerar_click_track(bpm, formula, duracao_minutos)` -> Use para gerar um áudio de metrônomo/clique personalizado.\n\n"
            "REGRAS CRÍTICAS DE EXPORTAÇÃO E SELEÇÃO DE FERRAMENTAS (PRIORIDADE MÁXIMA):\n"
            "- Para qualquer pedido de 'exportar', 'salvar', 'converter' ou menção explícita aos formatos 'wav' ou 'mp3':\n"
            "  1. Sua ÚNICA ação deve ser chamar a ferramenta `exportar_audio(formato=...)` com o formato correto ('wav' ou 'mp3').\n"
            "  2. NUNCA chame `mudar_tom_audio` para pedidos de exportação, mesmo que o usuário faça referência a um áudio alterado, processado ou modificado anteriormente.\n\n"
            "- Sempre que houver uma URL/link na mensagem do usuário (ex: YouTube, Drive):\n"
            "  1. Extraia apenas a URL base do vídeo/arquivo (remova parâmetros de playlist como '&list=' ou '&start_radio=').\n"
            "  2. Sua ÚNICA ação deve ser chamar a ferramenta `baixar_audio_link(url)` com a URL limpa.\n"
            "  3. NUNCA chame ferramentas de edição na mesma etapa do download.\n"
            "  4. Após concluir o download, informe ao usuário que o arquivo está pronto e aguarde o próximo comando dele.\n\n"
            "- Para pedidos de 'mudar o tom', 'alterar a afinação' ou ajustar semitonos:\n"
            "  1. Chame SEMPRE a ferramenta `mudar_tom_audio` passando `tom_origem` e `tom_destino` respeitando rigorosamente a contagem de semitonos.\n"
            "  2. NUNCA chame `sugerir_tom_ideal_vocal` a menos que o usuário mencione explicitamente a extensão vocal de um cantor.\n\n"
            "- Para pedidos de 'gerar PDF da cifra' ou 'exportar cifra':\n"
            "  Chame a ferramenta `exportar_cifra_pdf`.\n\n"
            "- Para pedidos de 'gerar setlist', 'montar ordem do culto' ou 'formatar lista':\n"
            "  1. NUNCA chame ferramentas de processamento de áudio ou download.\n"
            "  2. Monte um JSON com a chave 'musicas' contendo os objetos e chame APENAS a ferramenta `gerar_setlist_formatada`.\n\n"
            "ESTRUTURA DO JSON PARA SETLIST:\n"
            "- Cada objeto na lista 'musicas' deve possuir as chaves: 'titulo', 'tom', 'bpm', 'ministro', 'observacoes'.\n\n"
            "REGRAS DE RESPOSTA:\n"
            "- Responda SEMPRE em no máximo 1 ou 2 frases curtas.\n"
            "- NUNCA ofereça explicações teóricas desnecessárias a menos que seja explicitamente solicitado.\n"
            "- NUNCA chame `exportar_audio` automaticamente logo após executar `mudar_tom_audio`, a menos que o usuário tenha pedido explicitamente para 'exportar' ou 'salvar' na mesma mensagem.\n"
        )

        system_msg = {"role": "system", "content": system_content}

        if not self.historico:
            self.historico = [system_msg]
        else:
            self.historico[0] = system_msg

    def enviar_mensagem(self, mensagem_usuario: str):
        self.historico.append({"role": "user", "content": mensagem_usuario})
        
        response = ollama.chat(
            model=self.model_name,
            messages=self.historico,
            tools=self.tools,
            options={
                "temperature": 0.1
            }
        )

        msg = response['message']
        self.historico.append(msg)
        return msg

    def enviar_resposta_ferramenta(self, nome_funcao: str, conteudo_resultado: str):
        self.historico.append({
            "role": "tool",
            "name": nome_funcao,
            "content": str(conteudo_resultado)
        })

        response = ollama.chat(
            model=self.model_name,
            messages=self.historico
        )
        
        msg = response['message']
        self.historico.append(msg)
        return msg

    def reiniciar_historico(self):
        """Limpa o histórico do chat mantendo apenas a instrução do sistema."""
        system_msg = self.historico[0]
        self.historico = [system_msg]