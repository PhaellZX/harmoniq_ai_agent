# 🎵 Harmoniq AI — Local Audio Processing & Chord Chart Assistant

An interactive desktop application built in Python for audio manipulation, digital signal processing (DSP), and chord chart management. It leverages a local **Ollama** instance running **Qwen 2.5 3B** to interpret natural language commands and invoke system tools automatically.

---

## 🛠️ Built With

* **Language:** Python 3.10+
* **GUI Framework:** Tkinter / CustomTkinter
* **Local LLM & Tool Calling:** Ollama (`qwen2.5:3b`)
* **Audio Processing & DSP:** Librosa, SoundFile, PyDub, Demucs (Stem Separation), Scipy
* **PDF Export & Rendering:** WeasyPrint / ReportLab
* **Media Downloader:** `yt-dlp`

---

## 📋 Prerequisites

Before starting, ensure you have the following installed on your system:

1. **Python 3.10 or higher:** [Download Python](https://www.python.org/downloads/)
2. **FFmpeg:** Required for multi-format audio conversion via Librosa and PyDub.
   * *Linux (Ubuntu/Debian):* `sudo apt install ffmpeg`
   * *Windows:* Download from the official website and add the binary directory to your `PATH` environment variable.
3. **Ollama:** [Download Ollama](https://ollama.com/)

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/PhaellZX/harmoniq_ai_agent.git](https://github.com/PhaellZX/harmoniq_ai_agent.git)
cd harmoniq_ai_agent
```

### 2. Create and Activate a Virtual Environment

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

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Pull the Local Ollama Model

Ensure the Ollama service is running in the background and execute:
```bash
ollama pull qwen2.5:3b
```

### 5. Run the Application
```bash
python main.py
```

## 🧪 Prompt & Feature Testing Guide

Once an audio file is loaded into the interface or when issuing standalone commands, you can converse directly with the agent through the application chat box.

### 🎛️ Audio Processing & DSP

| Feature | Description | Example Prompt |
| :--- | :--- | :--- |
| **Audio Normalization** | Adjusts peak audio gain to a target dBFS level without distortion. | `"Normalize current audio"` or `"Normalize audio to -14 dBFS"` |
| **Pitch Shift / Key Change** | Transposes audio pitch by semitones without affecting speed. | `"Lower pitch by 2 semitones"` or `"Raise key by 1 semitone"` |
| **Tempo / Speed Control** | Changes playback speed (time stretch) without altering pitch. | `"Make audio 10% faster"` or `"Set playback speed to 0.9x"` |
| **Audio Trimming** | Cuts a specific time segment from the active audio file. | `"Trim audio from 0:10 to 1:45"` |
| **Key & BPM Analysis** | Detects musical key signature and tempo from audio. | `"What is the key and BPM of this song?"` |
| **Stem Separation** | Isolates vocals, instruments, or backing tracks using Demucs. | `"Separate vocals from instrumental"` or `"Remove vocals from track"` |
| **Direct Audio Export** | Converts and exports active audio into WAV or MP3. | `"Export to MP3"` or `"Save active track as WAV"` |
| **Audio Downloader** | Downloads audio directly from YouTube or web URLs. | `"Download audio from https://www.youtube.com/watch?v=..."` |

---

### 🎼 Chord Charts, Metronome & Utilities

| Feature | Description | Example Prompt |
| :--- | :--- | :--- |
| **Chord Chart Transposition** | Transposes written chord chart text into a target key. | `"Transpose this chord chart from C to E: C G Am F"` |
| **PDF Export** | Generates a styled rehearsal PDF document with chord charts. | `"Export chord PDF title 'Because He Lives', key G, minister 'Band', bpm 70, chords: G C D G"` |
| **Click Track / Metronome** | Generates a custom WAV metronome audio file. | `"Generate click track at 120 BPM, 4/4 time signature for 3 minutes"` |
| **Vocal Range Analyzer** | Recommends optimal key shifts based on singer classification. | `"Suggest ideal key for tenor vocal if original song is in Ab"` |
| **Setlist Formatter** | Formats and structures worship/gig song list orders. | `"Generate setlist with songs: Amazing Grace, Way Maker, How Great Is Our God"` |

## 📁 Repository Structure

```bash
harmoniq_ai_agent/
├── agent/                  # Ollama client manager and tool definition definitions
│   ├── client.py
│   └── tools.py
├── core/                   # Core processing modules (Audio, Chords, Vocal, Setlist)
│   ├── audio_processor.py
│   ├── chord_transposer.py
│   ├── downloader.py
│   ├── setlist.py
│   └── vocal_range.py
├── gui/                    # CustomTkinter interface components
│   └── main_window.py
├── tools/                  # Utility scripts (Click track generator)
│   └── audio_tools.py
├── utils/                  # Export and conversion pipelines
│   └── export_manager.py
├── output/                 # Default output directory for generated audio and PDF files
├── main.py                 # Application entry point
├── requirements.txt        # Python dependency manifest
└── README.md               # Project documentation
```