import os
import subprocess
from pathlib import Path
from weasyprint import HTML, CSS

class ExportManager:
    @staticmethod
    def converter_audio(caminho_entrada: str, formato_saida: str = "mp3", diretorio_saida: str = "output") -> str:
        """
        Converte o áudio fornecido para MP3 ou WAV usando FFmpeg.
        """
        if not os.path.exists(caminho_entrada):
            raise FileNotFoundError(f"Arquivo de entrada não encontrado: {caminho_entrada}")

        os.makedirs(diretorio_saida, exist_ok=True)
        formato_saida = formato_saida.lower().strip()
        
        nome_base = Path(caminho_entrada).stem
        caminho_saida = os.path.join(diretorio_saida, f"{nome_base}_exportado.{formato_saida}")

        # Comando FFmpeg para conversão
        cmd = ["ffmpeg", "-y", "-i", caminho_entrada]

        if formato_saida == "mp3":
            cmd.extend(["-b:a", "320k"])
        elif formato_saida == "wav":
            cmd.extend(["-ar", "44100", "-ac", "2"])
        else:
            raise ValueError("Formato não suportado. Use 'mp3' ou 'wav'.")

        cmd.append(caminho_saida)

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Erro FFmpeg ao converter áudio: {result.stderr}")

        return caminho_saida

    @staticmethod
    def gerar_pdf_cifra(
        titulo: str,
        tom: str,
        texto_cifra: str,
        ministro: str = "",
        bpm: str = "",
        diretorio_saida: str = "output"
    ) -> str:
        """
        Gera um PDF profissional e estilizado com a cifra transposta e metadados.
        """
        os.makedirs(diretorio_saida, exist_ok=True)
        nome_arquivo_limpo = "".join([c if c.isalnum() else "_" for c in titulo]).strip("_") or "cifra"
        caminho_pdf = os.path.join(diretorio_saida, f"Cifra_{nome_arquivo_limpo}.pdf")

        # HTML e CSS embutidos para formatação de cifra musical
        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
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
        .cifra-container {{
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
        <h1>{titulo}</h1>
        <div class="meta-grid">
            <div class="meta-item"><strong>TOM:</strong> {tom or 'N/A'}</div>
            <div class="meta-item"><strong>BPM:</strong> {bpm or 'N/A'}</div>
            <div class="meta-item"><strong>MINISTRO:</strong> {ministro or 'Louvor'}</div>
        </div>
    </div>

    <div class="cifra-container">
{texto_cifra}
    </div>

    <div class="footer">
        Gerado automaticamente por Worship Agent AI - Sistema de Produção Musical
    </div>
</body>
</html>
"""

        HTML(string=html_content).write_pdf(caminho_pdf)
        return caminho_pdf