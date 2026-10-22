from dotenv import load_dotenv
from gui.main_window import TransposerApp

# Load environment variables (.env)
load_dotenv()

if __name__ == "__main__":
    app = TransposerApp()
    app.mainloop()