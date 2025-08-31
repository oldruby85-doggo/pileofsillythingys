import sys
from PyQt5.QtWidgets import QApplication

# проверяем, что пакет собирается (заодно подгружаем подмодули)
from lockers.core.storage import get_asset, load_layout, save_layout, export_txt, export_xlsx  # noqa: F401
from lockers.utils.paths import autosave_path  # noqa: F401

# запускаем твой GUI из legacy_app.py
import legacy_app as legacy  # файл лежит рядом с папкой lockers/

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = legacy.LockerApp()
    win.show()
    sys.exit(app.exec_())
