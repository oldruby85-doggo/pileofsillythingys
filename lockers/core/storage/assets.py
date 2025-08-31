import os, sys

def get_asset(name: str) -> str:
    """Абсолютный путь к ассету рядом с exe (PyInstaller) или рядом со скриптом."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, name)
    base = os.path.dirname(getattr(sys.modules.get("__main__"), "__file__", os.getcwd()))
    return os.path.join(base, name)
