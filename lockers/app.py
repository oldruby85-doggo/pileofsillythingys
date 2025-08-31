# lockers/app.py
import sys
from PyQt5.QtWidgets import QApplication
from lockers.ui import LockerApp

def main():
    app = QApplication(sys.argv)
    win = LockerApp()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
