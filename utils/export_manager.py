import os
import subprocess
from pathlib import Path
from weasyprint import HTML, CSS

class ExportManager:
    @staticmethod
    def convert_audio(input_path: str, target_format: str = "mp3", output_dir: str = "output") -> str:
        """
        Converts the provided audio to MP3 or WAV using FFmpeg.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        os.makedirs(output_dir, exist_ok=True)
        target_format = target_format.lower().strip()
        
        base_name = Path(input_path).stem
        output_path = os.path.join(output_dir, f"{base_name}_exported.{target_format}")

        # FFmpeg command for conversion
        cmd = ["ffmpeg", "-y", "-i", input_path]

        if target_format == "mp3":
            cmd.extend(["-b:a", "320k"])
        elif target_format == "wav":
            cmd.extend(["-ar", "44100", "-ac", "2"])
        else:
            raise ValueError("Unsupported format. Use 'mp3' or 'wav'.")

        cmd.append(output_path)

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg error converting audio: {result.stderr}")

        return output_path

    @staticmethod
    def export_chord_pdf(
        title: str,
        key: str,
        chord_text: str,
        minister: str = "",
        bpm: str = "",
        output_dir: str = "output"
    ) -> str:
        """
        Generates a professional, styled PDF with transposed chord chart and metadata.
        """
        os.makedirs(output_dir, exist_ok=True)
        clean_filename = "".join([c if c.isalnum() else "_" for c in title]).strip("_") or "chord_chart"
        pdf_path = os.path.join(output_dir, f"Chord_{clean_filename}.pdf")

        # Embedded HTML/CSS for chord chart rendering
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 15mm 12mm;
            background-color: #faf9f6;
        }}
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            color: #2b2d42;
            margin: 0;
            padding: 0;
        }}
        .header {{
            background-color: #1e293b;
            color: #ffffff;
            padding: 20px 24px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0 0 8px 0;
            font-size: 20pt;
            letter-spacing: -0.5px;
        }}
        .meta-grid {{
            display: table;
            width: 100%;
            margin-top: 10px;
            border-top: 1px solid #334155;
            padding-top: 10px;
        }}
        .meta-item {{
            display: table-cell;
            font-size: 10pt;
            color: #cbd5e1;
        }}
        .meta-item strong {{
            color: #38bdf8;
        }}
        .chord-container {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px 24px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 11pt;
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;
            color: #0f172a;
        }}
        .footer {{
            margin-top: 20px;
            text-align: center;
            font-size: 8pt;
            color: #94a3b8;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="meta-grid">
            <div class="meta-item"><strong>KEY:</strong> {key or 'N/A'}</div>
            <div class="meta-item"><strong>BPM:</strong> {bpm or 'N/A'}</div>
            <div class="meta-item"><strong>MINISTER:</strong> {minister or 'Worship'}</div>
        </div>
    </div>

    <div class="chord-container">
{chord_text}
    </div>

    <div class="footer">
        Generated automatically by Harmoniq AI — Music Production Copilot
    </div>
</body>
</html>
"""

        HTML(string=html_content).write_pdf(pdf_path)
        return pdf_path

    # =========================================================================
    # BACKWARD COMPATIBILITY ALIASES
    # =========================================================================
    @staticmethod
    def converter_audio(caminho_entrada: str, formato_saida: str = "mp3", diretorio_saida: str = "output") -> str:
        return ExportManager.convert_audio(input_path=caminho_entrada, target_format=formato_saida, output_dir=diretorio_saida)

    @staticmethod
    def gerar_pdf_cifra(
        titulo: str,
        tom: str,
        texto_cifra: str,
        ministro: str = "",
        bpm: str = "",
        diretorio_saida: str = "output"
    ) -> str:
        return ExportManager.export_chord_pdf(
            title=titulo,
            key=tom,
            chord_text=texto_cifra,
            minister=ministro,
            bpm=bpm,
            output_dir=diretorio_saida
        )