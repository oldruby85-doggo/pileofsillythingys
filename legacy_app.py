# ===============================================================
# Forbidden Castle of Lockers — legacy_app.py (Signal-safe)
# Сигналы вынесены во вложенный QObject, без множественного наследования
# ===============================================================

import sys, os, json, random

from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF, pyqtSignal, QObject
from PyQt5.QtGui import QBrush, QColor, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QFileDialog, QMessageBox,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QTableWidget, QTableWidgetItem, QWidget, QHBoxLayout,
    QMenu, QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QToolBar, QScrollArea
)

# наши модули
from lockers.core.storage.assets import get_asset
from lockers.core.storage.json_store import (
    load_layout as load_json_layout,
    save_layout as save_json_layout,
)
from lockers.core.storage.export_txt import export_txt as export_txt_file
from lockers.core.storage.export_xlsx import export_xlsx as export_xlsx_file
from lockers.utils.paths import autosave_path
from lockers.core.state import AppState
from lockers.ui.items import LockerItem


# --------------------------- VIEW ---------------------------
class LockerView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self._zoom = 0
        self.setToolTip("Колёсико: прокрутка. Ctrl+колёсико: масштаб. ЛКМ зажми и тяни — панорамирование.")

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            angle = event.angleDelta().y()
            factor = 1.25 if angle > 0 else 1 / 1.25
            self._zoom += 1 if angle > 0 else -1
            self.scale(factor, factor)
        else:
            super().wheelEvent(event)

# --------------------------- SCENE ---------------------------
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
        choice = QMessageBox.question(None, "Фон", random.choice(question_variants),
                                      QMessageBox.Yes | QMessageBox.No)
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
        path, _ = QFileDialog.getOpenFileName(None, "Выбрать фон", "", "Images (*.png *.jpg *.bmp)")
        if not path:
            return
        pm = QPixmap(path)
        if pm.isNull():
            QMessageBox.warning(None, "Ошибка", "Не удалось загрузить изображение.")
            return
        self.set_background_pixmap(pm)

    def contextMenuEvent(self, event):
        item = self.itemAt(event.scenePos(), self.views()[0].transform()) if self.views() else None
        if isinstance(item, LockerItem):
            return super().contextMenuEvent(event)
        menu = QMenu()
        a_add = QAction("Добавить локер", menu)
        a_grid = QAction("Добавить сетку локеров…", menu)
        menu.addAction(a_add); menu.addAction(a_grid)
        chosen = menu.exec_(event.screenPos())
        if chosen == a_add:
            self.add_locker(event.scenePos())
        elif chosen == a_grid:
            self.add_locker_grid(event.scenePos())

    def add_locker(self, pos, number=None, owner="", invno=""):
        if number is None:
            number = self.main_window.next_free_number()
        locker = LockerItem(self.main_window, number=number, owner=owner, invno=invno, pos=pos)

        # подписки на сигналы
        locker.sig.requestEditOwner.connect(self.main_window.on_edit_owner)
        locker.sig.requestEditNumber.connect(self.main_window.on_edit_number)
        locker.sig.requestEditInvno.connect(self.main_window.on_edit_invno)
        locker.sig.requestDuplicate.connect(self.main_window.on_duplicate_locker)
        locker.sig.requestDelete.connect(self.main_window.on_delete_locker)

        self.addItem(locker)
        self.main_window.sync_table_from_scene()

    def add_locker_grid(self, pos):
        from PyQt5.QtWidgets import QInputDialog
        rows, ok = QInputDialog.getInt(None, "Сетка", "Строк:", value=2, min=1, max=200)
        if not ok: return
        cols, ok = QInputDialog.getInt(None, "Сетка", "Столбцов:", value=5, min=1, max=200)
        if not ok: return
        step, ok = QInputDialog.getInt(None, "Сетка", "Шаг (px):", value=40, min=20, max=400)
        if not ok: return

        start_num = self.main_window.next_free_number()
        cur_y = pos.y()
        for _ in range(rows):
            cur_x = pos.x(); num = start_num
            for _ in range(cols):
                while self.main_window.number_exists(num):
                    num += 1
                self.add_locker(QPointF(cur_x, cur_y), number=num)
                num += 1; cur_x += step
            start_num = num; cur_y += step


# --------------------------- DIALOGS ---------------------------
class AuthorsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторы")
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Locker GUI App\n\nYahont Ruby & Сеточка"))
        img_path = get_asset("authors.png")
        if os.path.exists(img_path):
            pm = QPixmap(img_path)
            if not pm.isNull():
                lbl = QLabel()
                lbl.setPixmap(pm.scaledToWidth(260, Qt.SmoothTransformation))
                lay.addWidget(lbl)
        btns = QDialogButtonBox(QDialogButtonBox.Ok)
        btns.accepted.connect(self.accept)
        lay.addWidget(btns)


class AboutWhatDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О чем это")
        self.resize(560, 520)

        wrapper = QVBoxLayout(self)

        img_path = get_asset("shen.png")
        if os.path.exists(img_path):
            pm = QPixmap(img_path)
            if not pm.isNull():
                img_lbl = QLabel(); img_lbl.setAlignment(Qt.AlignHCenter)
                img_lbl.setPixmap(pm.scaledToWidth(260, Qt.SmoothTransformation))
                wrapper.addWidget(img_lbl)

        scroll = QScrollArea(self); scroll.setWidgetResizable(True)
        content = QWidget(); v = QVBoxLayout(content)
        html = """
        <div style='font-size: 13px; line-height: 1.45'>
        <p><b>Forbidden Castle of Lockers</b> — настольное приложение для визуального учета и планировки локеров/ячейкохранилищ поверх схемы помещения.</p>
        <p><b>Зачем это:</b> быстро разложить локеры по плану, пронумеровать, назначить владельцев и инвентарные номера, контролировать заполнение и выгружать списки.</p>
        <ul>
          <li>Фон-схема с авто-поиском <code>background.png</code> и диалогом выбора.</li>
          <li>Добавление по одному и сеткой, перетаскивание, масштабирование, привязка к сетке.</li>
          <li>Нумерация, владельцы и Инв.№, редактирование из таблицы и через ПКМ.</li>
          <li>Лимит по вместимости, экспорт TXT/XLSX, JSON сохранение/загрузка, автосейв.</li>
        </ul>
        </div>
        """
        lbl = QLabel(); lbl.setTextFormat(Qt.RichText); lbl.setWordWrap(True); lbl.setText(html)
        v.addWidget(lbl); v.addStretch(1)
        scroll.setWidget(content); wrapper.addWidget(scroll)
        btns = QDialogButtonBox(QDialogButtonBox.Ok); btns.accepted.connect(self.accept); wrapper.addWidget(btns)


# --------------------------- MAIN WINDOW ---------------------------
class LockerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Locker GUI App — Signal-safe")
        self.setGeometry(100, 100, 1400, 800)

        self.snap_to_grid = False
        self._updating_table = False
        self._syncing_selection = False
        self._current_json_path = None
        self.capacity = 100
        self.state = AppState(capacity=self.capacity, lockers_provider=self._iter_lockers)

        self.scene = LockerScene(self)
        self.view  = LockerView(self.scene, self)

        self.table = QTableWidget(); self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Локер", "Владелец", "Инв. №"])
        self.table.setSortingEnabled(True)
        self.table.itemChanged.connect(self._on_table_item_changed)
        self.table.itemSelectionChanged.connect(self._on_table_selection_changed)
        self.scene.selectionChanged.connect(self._on_scene_selection_changed)

        layout = QHBoxLayout()
        layout.addWidget(self.view, 7)
        layout.addWidget(self.table, 3)
        container = QWidget(); container.setLayout(layout)
        self.setCentralWidget(container)

        self._build_menubar_and_toolbar()
        self.statusBar().showMessage("Готово")
        self._setup_autosave()
        self.sync_table_from_scene()

    # ---- menus / toolbar ----
    def _build_menubar_and_toolbar(self):
        mb = self.menuBar(); m_file = mb.addMenu("Файл")

        a_save = QAction("Сохранить схему…", self); a_save.setShortcut("Ctrl+S")
        a_save.triggered.connect(self.save_layout); m_file.addAction(a_save)

        a_load = QAction("Загрузить схему…", self); a_load.setShortcut("Ctrl+O")
        a_load.triggered.connect(self.load_layout); m_file.addAction(a_load)

        a_bg = QAction("Загрузить фон…", self); a_bg.setShortcut("Ctrl+B")
        a_bg.triggered.connect(self.scene.load_background_via_dialog); m_file.addAction(a_bg)

        a_export_txt = QAction("Экспорт TXT…", self); a_export_txt.setShortcut("Ctrl+E")
        a_export_txt.triggered.connect(self.export_txt); m_file.addAction(a_export_txt)

        a_export_xlsx = QAction("Экспорт Excel…", self)
        a_export_xlsx.triggered.connect(self.export_excel); m_file.addAction(a_export_xlsx)

        m_file.addSeparator()
        a_exit = QAction("Выход", self); a_exit.triggered.connect(self.close); m_file.addAction(a_exit)

        m_add = mb.addMenu("Добавить")
        a_new = QAction("Создать локер", self); a_new.setShortcut("Ctrl+N")
        a_new.triggered.connect(lambda: self.scene.add_locker(self.view.mapToScene(self.view.viewport().rect().center())))
        m_add.addAction(a_new)

        a_grid = QAction("Создать сетку локеров…", self)
        a_grid.triggered.connect(lambda: self.scene.add_locker_grid(self.view.mapToScene(self.view.viewport().rect().center())))
        m_add.addAction(a_grid)

        m_view = mb.addMenu("Вид")
        a_snap = QAction("Привязка к сетке", self, checkable=True); a_snap.setChecked(self.snap_to_grid)
        a_snap.triggered.connect(self._toggle_snap); m_view.addAction(a_snap)

        m_tools = mb.addMenu("Инструменты")
        a_capacity = QAction("Задать вместимость помещения…", self)
        a_capacity.triggered.connect(self.set_capacity_dialog); m_tools.addAction(a_capacity)

        m_about = mb.addMenu("О программе")
        a_auth = QAction("Авторы", self); a_auth.triggered.connect(self.show_authors); m_about.addAction(a_auth)
        a_about_what = QAction("О чем это…", self); a_about_what.triggered.connect(self.show_about_what); m_about.addAction(a_about_what)

        tb: QToolBar = self.addToolBar("Главная"); tb.setMovable(False); tb.setFloatable(False)
        tb.addAction("➕ Локер", lambda: self.scene.add_locker(self.view.mapToScene(self.view.viewport().rect().center())))
        tb.addAction("💾 Сохранить", self.save_layout)
        tb.addAction("📂 Открыть", self.load_layout)

        def _export_menu():
            menu = QMenu(); menu.addAction(a_export_txt); menu.addAction(a_export_xlsx)
            menu.exec_(tb.mapToGlobal(tb.rect().bottomLeft()))
        tb.addAction("📤 Экспорт", _export_menu)

        tb.addAction("👥 Вместимость", self.set_capacity_dialog)
        tb.addAction("🖼 Фон", self.scene.load_background_via_dialog)

    # ---- utils ----
    def _toggle_snap(self, checked): self.snap_to_grid = bool(checked)

    def _setup_autosave(self):
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(60_000)
        self._autosave_timer.timeout.connect(self._do_autosave)
        self._autosave_timer.start()

    def _do_autosave(self):
        try:
            path = autosave_path()
            payload = {"capacity": self.capacity, "lockers": self._collect_layout_data()}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _iter_lockers(self):
        try:
            for it in self.scene.items():
                if isinstance(it, LockerItem):
                    yield it
        except RuntimeError:
            return

    # ---- state proxy ----
    def count_occupied(self): return self.state.occupied_count()
    def number_exists(self, num, exclude=None): return self.state.number_exists(int(num), exclude_obj=exclude)
    def next_free_number(self): return self.state.next_free_number()

    def can_add_one_owner(self, show_message=False):
        ok = self.state.can_add_one_owner()
        if not ok and show_message:
            QMessageBox.warning(self, "Лимит вместимости", f"Достигнута вместимость {self.capacity}.")
        return ok

    def can_assign_owner(self, old_owner: str, new_owner: str):
        ok = self.state.can_assign_owner(old_owner, new_owner)
        if not ok:
            QMessageBox.warning(self, "Лимит вместимости", f"Достигнута вместимость {self.capacity}.")
        return ok

    # ---- table sync ----
    def sync_table_from_scene(self):
        lockers = [it for it in self._iter_lockers()]
        lockers.sort(key=lambda it: (it.number is None, it.number if it.number is not None else 0))

        was_sort = self.table.isSortingEnabled()
        self._updating_table = True
        self.table.setSortingEnabled(False)
        self.table.clearContents()
        self.table.setRowCount(len(lockers))

        for row, it in enumerate(lockers):
            num_text = "" if it.number is None else str(it.number)
            num_item = QTableWidgetItem(num_text)
            num_item.setData(Qt.UserRole, 10**9 if it.number is None else int(it.number))
            num_item.setData(Qt.UserRole + 1, it)

            owner_item = QTableWidgetItem(it.owner)
            owner_item.setData(Qt.UserRole + 1, it)

            inv_item = QTableWidgetItem(it.invno)
            inv_item.setData(Qt.UserRole + 1, it)

            self.table.setItem(row, 0, num_item)
            self.table.setItem(row, 1, owner_item)
            self.table.setItem(row, 2, inv_item)

        self.table.setSortingEnabled(was_sort)
        self._updating_table = False
        self._update_status_counts()

    def _on_table_item_changed(self, item):
        if self._updating_table: return
        locker = item.data(Qt.UserRole + 1)
        if not isinstance(locker, LockerItem): return

        col = item.column()
        text = item.text().strip()

        if col == 0:
            if text == "":
                new_val = None
            else:
                try:
                    new_val = int(text); assert new_val >= 0
                except Exception:
                    QMessageBox.warning(self, "Некорректный номер", "Введите целое число или оставьте пустым.")
                    self._reflect_locker_to_row(item.row(), locker); return
            if new_val is not None and self.number_exists(new_val, exclude=locker):
                QMessageBox.warning(self, "Дубликат", f"Номер {new_val} уже занят.")
                self._reflect_locker_to_row(item.row(), locker); return
            locker.number = new_val

        elif col == 1:
            if not self.can_assign_owner(locker.owner, text):
                self._reflect_locker_to_row(item.row(), locker); return
            locker.owner = text
            locker._update_color()

        elif col == 2:
            locker.invno = text

        self.sync_table_from_scene()

    def _reflect_locker_to_row(self, row, locker):
        self._updating_table = True
        self.table.item(row, 0).setText("" if locker.number is None else str(locker.number))
        self.table.item(row, 1).setText(locker.owner)
        self.table.item(row, 2).setText(locker.invno)
        self._updating_table = False

    # ---- selection sync ----
    def _on_table_selection_changed(self):
        if self._syncing_selection: return
        self._syncing_selection = True

        selected_rows = {idx.row() for idx in self.table.selectedIndexes()}
        selected_lockers = set()
        for r in selected_rows:
            item = self.table.item(r, 0)
            if not item: continue
            locker = item.data(Qt.UserRole + 1)
            if isinstance(locker, LockerItem):
                selected_lockers.add(locker)

        for it in self._iter_lockers():
            it.setSelected(it in selected_lockers)

        if selected_lockers:
            self.view.centerOn(next(iter(selected_lockers)))

        self._syncing_selection = False

    def _on_scene_selection_changed(self):
        if self._syncing_selection: return
        self._syncing_selection = True

        selected = {it for it in self._iter_lockers() if it.isSelected()}
        self.table.clearSelection()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if not item: continue
            locker = item.data(Qt.UserRole + 1)
            if locker in selected:
                self.table.selectRow(row)

        self._syncing_selection = False

    # ---- save/load/export ----
    def _collect_layout_data(self):
        data = []
        for it in self._iter_lockers():
            data.append({
                "number": it.number,
                "owner": it.owner,
                "invno": it.invno,
                "x": float(it.pos().x()),
                "y": float(it.pos().y()),
            })
        return data

    def save_layout(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить схему",
                                              self._current_json_path or "", "JSON Files (*.json)")
        if not path: return
        if os.path.exists(path):
            try:
                with open(path, "rb") as src, open(path + ".bak", "wb") as dst:
                    dst.write(src.read())
            except Exception:
                pass
        try:
            save_json_layout(path, self.capacity, self._collect_layout_data())
            self._current_json_path = path
            self.statusBar().showMessage(f"Сохранено: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")

    def load_layout(self):
        path, _ = QFileDialog.getOpenFileName(self, "Загрузить схему",
                                              self._current_json_path or "", "JSON Files (*.json)")
        if not path: return
        try:
            cap, lockers_data = load_json_layout(path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{e}")
            return

        if cap is not None:
            try:
                self.capacity = int(cap)
                self.state.capacity = self.capacity
            except Exception:
                pass

        self.scene.clear_lockers_only()
        for d in lockers_data:
            self.scene.add_locker(
                QPointF(float(d["x"]), float(d["y"])),
                number=d["number"], owner=d["owner"], invno=d["invno"]
            )
        self._current_json_path = path
        self.sync_table_from_scene()
        self.statusBar().showMessage(f"Загружено: {path}")

    def export_txt(self):
        path, _ = QFileDialog.getSaveFileName(self, "Экспорт списка", "", "Text Files (*.txt)")
        if not path: return
        try:
            export_txt_file(path, self._collect_layout_data())
            self.statusBar().showMessage(f"Экспортировано в TXT: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать TXT:\n{e}")

    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Экспорт в Excel", "", "Excel Files (*.xlsx)")
        if not path: return
        try:
            export_xlsx_file(path, self._collect_layout_data())
            self.statusBar().showMessage(f"Экспортировано в Excel: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать Excel:\n{e}")

    # ---- misc ----
    def _update_status_counts(self):
        total = 0; occupied = 0
        for it in self._iter_lockers():
            total += 1
            occupied += 1 if it.owner else 0
        free = total - occupied
        cap = self.capacity if self.capacity is not None else "∞"
        self.statusBar().showMessage(f"Локеров: {total}, занято: {occupied}/{cap}, свободно: {free}")

    def set_capacity_dialog(self):
        from PyQt5.QtWidgets import QInputDialog
        val, ok = QInputDialog.getInt(self, "Вместимость помещения",
                                      "Максимум владельцев:",
                                      value=int(self.capacity if self.capacity is not None else 0),
                                      min=1, max=100000)
        if not ok: return
        self.capacity = int(val)
        self.state.capacity = self.capacity
        occ = self.count_occupied()
        if occ > self.capacity:
            QMessageBox.information(self, "Внимание",
                                    f"Сейчас занято {occ}, что больше новой вместимости {self.capacity}.")
        self._update_status_counts()

    def show_authors(self): AuthorsDialog(self).exec_()
    def show_about_what(self): AboutWhatDialog(self).exec_()

    # ---- handlers from LockerItem ----
    def on_edit_owner(self, it):
        from PyQt5.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Изменить владельца", "Новый владелец:", text=it.owner)
        if not ok: return
        new_owner = text.strip()
        if not self.can_assign_owner(it.owner, new_owner): return
        it.owner = new_owner
        it._update_color()
        self.sync_table_from_scene()

    def on_edit_number(self, it):
        from PyQt5.QtWidgets import QInputDialog
        current = it.number if it.number is not None else 0
        num, ok = QInputDialog.getInt(self, "Изменить номер", "Новый номер (0 чтобы очистить):",
                                      value=current, min=0)
        if not ok: return
        new_val = None if num == 0 else num
        if new_val is not None and self.number_exists(new_val, exclude=it):
            QMessageBox.warning(self, "Дубликат", f"Номер {new_val} уже занят.")
            return
        it.number = new_val
        self.sync_table_from_scene()

    def on_edit_invno(self, it):
        from PyQt5.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Инвентарный номер", "Инв. №:", text=it.invno)
        if not ok: return
        it.invno = text.strip()
        self.sync_table_from_scene()

    def on_duplicate_locker(self, it):
        pos = it.pos() + QPointF(it.rect().width() + 6, 0)
        owner_copy = it.owner
        if owner_copy and not self.can_add_one_owner(show_message=True):
            owner_copy = ""
        # создаём ОДНУ копию
        copy = LockerItem(self, number=None, owner=owner_copy, invno=it.invno, pos=pos)

        copy.sig.requestEditOwner.connect(self.on_edit_owner)
        copy.sig.requestEditNumber.connect(self.on_edit_number)
        copy.sig.requestEditInvno.connect(self.on_edit_invno)
        copy.sig.requestDuplicate.connect(self.on_duplicate_locker)
        copy.sig.requestDelete.connect(self.on_delete_locker)

        self.scene.addItem(copy)
        self.sync_table_from_scene()

    def on_delete_locker(self, it):
        reply = QMessageBox.question(self, "Удаление", "Удалить этот локер?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            sc = it.scene()
            if sc: sc.removeItem(it)
            self.sync_table_from_scene()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LockerApp(); win.show()
    sys.exit(app.exec_())
