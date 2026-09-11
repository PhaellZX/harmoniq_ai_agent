# 🎵 Harmonic AI - Agente Local de Processamento de Áudio e Cifras

Aplicação desktop interativa desenvolvida em Python para manipulação, processamento de áudio e gerenciamento de cifras. Utiliza **Ollama** com **Qwen 2.5 3B** para interpretar comandos em linguagem natural e invocar ferramentas automaticamente de forma local.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10+
* **Interface Gráfica:** Tkinter / CustomTkinter
* **LLM Local & Tools:** Ollama (`qwen2.5:3b`)
* **Processamento de Áudio:** Librosa, SoundFile, PyDub, Demucs (Separação de Stems)
* **Geração de PDF:** ReportLab

---

## 📋 Pré-requisitos

Antes de iniciar, certifique-se de ter os seguintes programas instalados no sistema:

1. **Python 3.10 ou superior:** [Download Python](https://www.python.org/downloads/)
2. **FFmpeg:** Necessário para manipular diferentes formatos de áudio via PyDub/Librosa.
   * *Linux (Ubuntu/Debian):* `sudo apt install ffmpeg`
   * *Windows:* Baixar pelo site oficial e adicionar o executável à variável de ambiente `PATH`.
3. **Ollama:** [Download Ollama](https://ollama.com/)

---

## 🚀 Instalação e Configuração

### 1. Clonar o Repositório
```bash
git clone [https://github.com/PhaellZX/harmoniq_ai_agent.git](https://github.com/PhaellZX/harmoniq_ai_agent.git)
cd seu-repositorio
```

### 2. Criar e Ativar o Ambiente Virtual

* Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

* Windows (PowerShell):
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Baixar o Modelo no Ollama

Garanta que o serviço do Ollama esteja rodando em segundo plano e execute:
```bash
ollama pull qwen2.5:3b
```

### 5. Executar a Aplicação
```bash
python main.py
```

## 🧪 Guia de Testes e Prompts Sugeridos

Com o áudio carregado ou com o sistema pronto, você pode enviar comandos diretamente pelo chat da interface.

### 🎛️ Processamento de Áudio

| Funcionalidade | Descrição | Exemplo de Prompt |
| :--- | :--- | :--- |
| **Normalização** | Ajusta o ganho do áudio para um volume padrão. | `"Normalize o áudio atual"` ou `"Normalize para -14 dB"` |
| **Mudança de Tom** | Altera a altura (pitch) do áudio em semitonos. | `"Aumente o tom em 2 semitonos"` ou `"Abaixo o tom em 1 semitono"` |
| **Alteração de Velocidade** | Altera a velocidade sem modificar o tom. | `"Deixe o áudio 10% mais rápido"` ou `"Acelere em 1.2x"` |
| **Corte de Áudio** | Recorta um trecho específico do arquivo. | `"Corte o áudio dos 10 segundos até 45 segundos"` |
| **Análise de Tom e BPM** | Detecta a tonalidade e a velocidade da música. | `"Qual é o tom e o BPM dessa música?"` |
| **Separação de Stems** | Separa o áudio em faixas isoladas (vocal e instrumental). | `"Separe a voz do instrumental"` ou `"Remova os vocais da música"` |
| **Exportação Direta** | Exporta a faixa para formatos específicos de áudio. | `"Exportar para MP3"` ou `"Salvar como WAV"` |

---

### 🎼 Cifras, Metrônomo e Utilitários

| Funcionalidade | Descrição | Exemplo de Prompt |
| :--- | :--- | :--- |
| **Transposição de Cifra** | Transpõe o texto de uma cifra para outro tom. | `"Transponha esta cifra de C para E: C G Am F"` |
| **Exportação de PDF** | Gera um documento PDF formatado com a cifra. | `"Exportar cifra em PDF título 'Porque Ele Vive', tom de G, ministro 'Harpa', bpm 70, cifra: G C D G"` |
| **Gerar Metrônomo / Click** | Cria uma faixa de metrônomo personalizada. | `"Gere um click track com 120 bpm, fórmula 4/4 por 3 minutos"` |
| **Sugestão Vocal** | Recomenda ajustes de tom com base na extensão. | `"Qual o tom ideal para vocal feminino se a música original está em G?"` |
| **Gerar Setlist** | Formata e organiza uma lista de músicas para apresentação. | `"Gere uma setlist formatada com as músicas: Ninguém Explica Deus, Ligar Aos Céus e Me Atraiu"` |

## 📁 Estrutura das Pastas

```bash
├── core/                   # Módulos de processamento (AudioProcessor, PDF, etc.)
├── agent/                  # Integração com a LLM e ferramentas
├── gui/                    # Interface gráfica Tkinter
├── output/                 # Diretório onde são salvos os arquivos gerados (áudio/PDF)
├── requirements.txt        # Lista de dependências Python
├── main.py                 # Ponto de entrada da aplicação
└── README.md               # Documentação do projeto
```