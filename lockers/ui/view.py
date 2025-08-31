# lockers/ui/view.py
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGraphicsView

class LockerView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self._zoom = 0
        self.setToolTip(
            "Колёсико: прокрутка. Ctrl+колёсико: масштаб. "
            "Зажми ЛКМ и тяни — панорамирование."
        )

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            angle = event.angleDelta().y()
            factor = 1.25 if angle > 0 else 1 / 1.25
            self._zoom += 1 if angle > 0 else -1
            self.scale(factor, factor)
        else:
            super().wheelEvent(event)
