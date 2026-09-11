import os
import yt_dlp

class AudioDownloader:
    @staticmethod
    def baixar_audio_por_link(url: str, output_dir: str = "downloads") -> str:
        """
        Baixa o áudio a partir de um link suportado pelo yt-dlp e converte para MP3/WAV.
        Retorna o caminho absoluto do arquivo baixado.
        """
        os.makedirs(output_dir, exist_ok=True)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                # Garante a extensão .mp3 gerada pelo postprocessor
                base_path, _ = os.path.splitext(filename)
                final_filepath = f"{base_path}.mp3"

                if os.path.exists(final_filepath):
                    return os.path.abspath(final_filepath)
                return os.path.abspath(filename)
        except Exception as e:
            raise RuntimeError(f"Falha ao baixar áudio da URL '{url}': {e}")