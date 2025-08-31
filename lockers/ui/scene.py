# lockers/ui/scene.py
import os
import random
from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QGraphicsScene, QMenu, QAction, QFileDialog, QMessageBox, QInputDialog
)

from lockers.ui.items import LockerItem
from lockers.core.storage.assets import get_asset


class LockerScene(QGraphicsScene):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._bg_item = None
        self.load_default_background()

    def clear_lockers_only(self):
        for it in list(self.items()):
            if isinstance(it, LockerItem):
                self.removeItem(it)

    # ---------- фон ----------
    def set_background_pixmap(self, pixmap: QPixmap):
        if self._bg_item:
            self.removeItem(self._bg_item)
            self._bg_item = None
        if not pixmap.isNull():
            self._bg_item = self.addPixmap(pixmap)
            self._bg_item.setZValue(-1000)
            self.setSceneRect(QRectF(pixmap.rect()))

    def load_default_background(self):
        path = get_asset("background.png")
        if os.path.exists(path):
            pm = QPixmap(path)
            if not pm.isNull():
                self.set_background_pixmap(pm)
                return

        question_variants = [
            "Загрузить схему помещения?",
            "Фон не найден. Выбрать изображение для схемы?",
            "Без фона пустовато. Укажем картинку сейчас?",
            "Не вижу background.png. Подхватить фон из файла?",
        ]
        choice = QMessageBox.question(
            None, "Фон", random.choice(question_variants),
            QMessageBox.Yes | QMessageBox.No
        )
        if choice == QMessageBox.Yes:
            self.load_background_via_dialog()
        else:
            QMessageBox.information(None, "Фон", random.choice([
                "Ок, но с фоном удобнее ;)",
                "Ну смотри, потом не жалуйся.",
                "Без фона как без обоев — жить можно, но скучно.",
                "Ладно, но атмосфера пострадает.",
            ]))

    def load_background_via_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            None, "Выбрать фон", "", "Images (*.png *.jpg *.bmp)"
        )
        if not path:
            return
        pm = QPixmap(path)
        if pm.isNull():
            QMessageBox.warning(None, "Ошибка", "Не удалось загрузить изображение.")
            return
        self.set_background_pixmap(pm)

    # ---------- контекстное меню сцены ----------
    def contextMenuEvent(self, event):
        item = self.itemAt(event.scenePos(), self.views()[0].transform()) if self.views() else None
        if isinstance(item, LockerItem):
            return super().contextMenuEvent(event)

        menu = QMenu()
        a_add = QAction("Добавить локер", menu)
        a_grid = QAction("Добавить сетку локеров…", menu)
        menu.addAction(a_add)
        menu.addAction(a_grid)

        chosen = menu.exec_(event.screenPos())
        if chosen == a_add:
            self.add_locker(event.scenePos())
        elif chosen == a_grid:
            self.add_locker_grid(event.scenePos())

    # ---------- создание локеров ----------
    def add_locker(self, pos, number=None, owner="", invno=""):
        if number is None:
            number = self.main_window.next_free_number()

        locker = LockerItem(
            self.main_window, number=number, owner=owner, invno=invno, pos=pos
        )
        # подписки на сигналы элемента
        locker.sig.requestEditOwner.connect(self.main_window.on_edit_owner)
        locker.sig.requestEditNumber.connect(self.main_window.on_edit_number)
        locker.sig.requestEditInvno.connect(self.main_window.on_edit_invno)
        locker.sig.requestDuplicate.connect(self.main_window.on_duplicate_locker)
        locker.sig.requestDelete.connect(self.main_window.on_delete_locker)

        self.addItem(locker)
        self.main_window.sync_table_from_scene()

    def add_locker_grid(self, pos):
        rows, ok = QInputDialog.getInt(None, "Сетка", "Строк:", value=2, min=1, max=200)
        if not ok:
            return
        cols, ok = QInputDialog.getInt(None, "Сетка", "Столбцов:", value=5, min=1, max=200)
        if not ok:
            return
        step, ok = QInputDialog.getInt(None, "Сетка", "Шаг (px):", value=40, min=20, max=400)
        if not ok:
            return

        start_num = self.main_window.next_free_number()
        cur_y = pos.y()
        for _ in range(rows):
            cur_x = pos.x()
            num = start_num
            for _ in range(cols):
                while self.main_window.number_exists(num):
                    num += 1
                self.add_locker(QPointF(cur_x, cur_y), number=num)
                num += 1
                cur_x += step
            start_num = num
            cur_y += step
