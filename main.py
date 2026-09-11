from dotenv import load_dotenv
from gui.main_window import TransposerApp

# Carrega as variáveis de ambiente (.env)
load_dotenv()

if __name__ == "__main__":
    app = TransposerApp()
    app.mainloop()