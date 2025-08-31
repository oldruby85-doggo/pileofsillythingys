# legacy_app.py — тонкий лаунчер для обратной совместимости
import sys
from PyQt5.QtWidgets import QApplication
from lockers.ui import LockerApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LockerApp()
    win.show()
    sys.exit(app.exec_())
