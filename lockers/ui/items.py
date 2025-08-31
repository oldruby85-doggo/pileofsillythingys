# lockers/ui/items.py
import random
from PyQt5.QtCore import Qt, QPointF, pyqtSignal, QObject
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QGraphicsRectItem, QMenu, QAction

class LockerItem(QGraphicsRectItem):
    class Signals(QObject):
        requestEditOwner = pyqtSignal(object)
        requestEditNumber = pyqtSignal(object)
        requestEditInvno  = pyqtSignal(object)
        requestDuplicate  = pyqtSignal(object)
        requestDelete     = pyqtSignal(object)

        def __init__(self, parent=None):
            super().__init__(parent)

    GRID = 10

    def __init__(self, main_window, number=None, owner="", invno="", pos=None):
        super().__init__(0, 0, 34, 34)
        self.sig = LockerItem.Signals()
        self.main_window = main_window
        self.number = number
        self.owner = owner.strip()
        self.invno = str(invno).strip()

        self.setFlags(QGraphicsRectItem.ItemIsMovable | QGraphicsRectItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self._update_color()

        if pos is not None:
            if isinstance(pos, QPointF):
                self.setPos(pos)
            else:
                self.setPos(float(pos[0]), float(pos[1]))

    def _update_color(self):
        self.setBrush(QBrush(QColor("gray" if self.owner else "green")))

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self.number is not None:
            painter.drawText(self.rect(), Qt.AlignCenter, str(self.number))

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemPositionChange and self.main_window and self.main_window.snap_to_grid:
            x = round(value.x() / self.GRID) * self.GRID
            y = round(value.y() / self.GRID) * self.GRID
            return QPointF(x, y)
        return super().itemChange(change, value)

    def contextMenuEvent(self, event):
        menu = QMenu()
        a_owner  = QAction("Изменить владельца", menu)
        a_number = QAction("Изменить номер", menu)
        a_inv    = QAction("Изменить инв. №", menu)
        a_dup    = QAction("Дублировать", menu)
        a_delete = QAction("Удалить", menu)
        for a in (a_owner, a_number, a_inv, a_dup, a_delete):
            menu.addAction(a)

        a_owner.triggered.connect(lambda: self.sig.requestEditOwner.emit(self))
        a_number.triggered.connect(lambda: self.sig.requestEditNumber.emit(self))
        a_inv.triggered.connect(lambda: self.sig.requestEditInvno.emit(self))
        a_dup.triggered.connect(lambda: self.sig.requestDuplicate.emit(self))
        a_delete.triggered.connect(lambda: self.sig.requestDelete.emit(self))
        menu.exec_(event.screenPos())
