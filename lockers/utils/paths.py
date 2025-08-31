from pathlib import Path

def autosave_path(filename: str = ".locker_gui_autosave.json") -> str:
    return str(Path.home() / filename)
