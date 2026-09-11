FERRAMENTAS_OLLAMA = [
    {
        "type": "function",
        "function": {
            "name": "mudar_tom_audio",
            "description": "Altera a afinação/tom do áudio por semitonos. ATENÇÃO À MATEMÁTICA DOS INTERVALOS: +1 semitom = meio tom (ex: C para C#), +2 semitonos = um tom inteiro (ex: C para D), +3 semitonos = uma terça menor (ex: C para D#).",
            "parameters": {
                "type": "object",
                "properties": {
                    "caminho_entrada": {
                        "type": "string",
                        "description": "Caminho do arquivo de áudio."
                    },
                    "semitonos": {
                        "type": "integer",
                        "description": "Número exato de semitonos (ex: 2 para subir um tom inteiro)."
                    },
                    "tom_origem": {
                        "type": "string",
                        "description": "Tom original da música (ex: 'C')."
                    },
                    "tom_destino": {
                        "type": "string",
                        "description": "Tom de destino correto baseado nos semitonos (ex: se origem C e semitonos 2, destino é D)."
                    }
                },
                "required": ["semitonos"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "alterar_velocidade_audio",
            "description": "Altera o tempo/velocidade da execução do áudio sem alterar a afinação.",
            "parameters": {
                "type": "object",
                "properties": {
                    "caminho_entrada": {"type": "string", "description": "Caminho do arquivo de áudio."},
                    "fator_frequencia": {"type": "number", "description": "Fator de velocidade (ex: 1.1 para mais rápido, 0.9 para mais lento)."}
                },
                "required": ["fator_frequencia"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "separar_stems_audio",
            "description": "Separa faixas e instrumentos do áudio (vocal, bateria, baixo, acompanhamento).",
            "parameters": {
                "type": "object",
                "properties": {
                    "caminho_entrada": {"type": "string", "description": "Caminho do arquivo de áudio."},
                    "modo": {"type": "string", "description": "Modo de separação: '2stems' (vocal/playback) ou '4stems'."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "detectar_tom_e_bpm_audio",
            "description": "Analisa e detecta o tom musical e o andamento (BPM) de um arquivo de áudio.",
            "parameters": {
                "type": "object",
                "properties": {
                    "caminho_entrada": {"type": "string", "description": "Caminho do arquivo de áudio."}
                }
            }
        }
    },
   {
    "type": "function",
    "function": {
        "name": "normalizar_audio",
        "description": "Ajusta e equaliza o volume/ganho do áudio. Use SEMPRE que o usuário disser 'normalize', 'normalizar', 'ajuste o volume' ou 'equalize o áudio'.",
        "parameters": {
            "type": "object",
            "properties": {
                "caminho_entrada": {
                    "type": "string",
                    "description": "Caminho do arquivo de áudio."
                },
                "decibeis_alvo": {
                    "type": "number",
                    "description": "Volume alvo em dBFS (padrão -14.0)."
                }
            },
            "required": []
        }
    }
},
    {
        "type": "function",
        "function": {
            "name": "cortar_audio",
            "description": "Corta um trecho do arquivo de áudio informando o tempo de início e fim.",
            "parameters": {
                "type": "object",
                "properties": {
                    "caminho_entrada": {"type": "string", "description": "Caminho do arquivo de áudio."},
                    "inicio_seg": {"type": "number", "description": "Tempo inicial em segundos."},
                    "fim_seg": {"type": "number", "description": "Tempo final em segundos."}
                },
                "required": ["inicio_seg", "fim_seg"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "baixar_audio_link",
            "description": "Baixa o áudio de uma URL/link do YouTube ou drive para uso local.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL/link do vídeo ou áudio."}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "transpor_cifra_texto",
            "description": "Transpõe o texto de uma cifra musical alterando os acordes de um tom para outro.",
            "parameters": {
                "type": "object",
                "properties": {
                    "texto_cifra": {"type": "string", "description": "Texto completo da cifra."},
                    "semitonos": {"type": "integer", "description": "Quantidade de semitonos."},
                    "tom_origem": {"type": "string", "description": "Tom atual da cifra."},
                    "tom_destino": {"type": "string", "description": "Tom desejado da cifra."}
                },
                "required": ["texto_cifra"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sugerir_tom_ideal_vocal",
            "description": "Analisa a tessitura vocal do cantor em relação à música para sugerir o tom ideal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tom_original": {"type": "string", "description": "Tom original da música."},
                    "nota_min_musica": {"type": "string", "description": "Nota mais grave da música."},
                    "nota_max_musica": {"type": "string", "description": "Nota mais aguda da música."},
                    "tipo_voz_ou_min_cantor": {"type": "string", "description": "Tipo de voz ou nota mínima do cantor."},
                    "max_cantor": {"type": "string", "description": "Nota máxima do cantor."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "gerar_setlist_formatada",
            "description": "Gera uma setlist organizada e formatada para os ministros e músicos do culto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "json_musicas_str": {"type": "string", "description": "String JSON contendo a lista de músicas e detalhes."},
                    "titulo": {"type": "string", "description": "Título do culto/ensaio."}
                },
                "required": ["json_musicas_str"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "exportar_audio",
            "description": "Converte e exporta o arquivo de áudio atual/modificado para o formato especificado (WAV ou MP3). Não altera afinação ou velocidade.",
            "parameters": {
                "type": "object",
                "properties": {
                    "formato": {
                        "type": "string",
                        "description": "Formato de saída desejado ('wav' ou 'mp3')"
                    }
                },
                "required": ["formato"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "exportar_cifra_pdf",
            "description": "Gera um arquivo PDF estilizado contendo a cifra transposta e os dados para ensaio.",
            "parameters": {
                "type": "object",
                "properties": {
                    "titulo": {"type": "string", "description": "Título da música."},
                    "tom": {"type": "string", "description": "Tom da cifra."},
                    "texto_cifra": {"type": "string", "description": "Texto da cifra."},
                    "ministro": {"type": "string", "description": "Nome do ministro ou líder de louvor."},
                    "bpm": {"type": "string", "description": "Andamento em BPM."}
                },
                "required": ["texto_cifra"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "gerar_click_track",
            "description": "Gera um arquivo de áudio de metrônomo/click track personalizado com BPM, fórmula de compasso e duração.",
            "parameters": {
                "type": "object",
                "properties": {
                    "bpm": {"type": "integer", "description": "Andamento em BPM (ex: 120, 70)."},
                    "formula": {"type": "string", "description": "Fórmula de compasso (ex: '4/4', '3/4', '6/8')."},
                    "duracao_minutos": {"type": "number", "description": "Duração total do áudio em minutos."}
                }
            }
        }
    }
]