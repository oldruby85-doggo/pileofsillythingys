# lockers/core/state.py
"""
Простая бизнес-логика приложения:
- учёт вместимости (capacity)
- подсчёт занятых локеров
- проверка возможности добавить ещё одного владельца
- проверка дубликатов номеров
- поиск следующего свободного номера
"""

from __future__ import annotations
from typing import Callable, Iterable, Optional, Any


class _LockerProto:
    """Мини-«протокол», чтобы mypy не плакал и было понятно, что мы ждём от locker-объекта."""
    number: Optional[int]
    owner: str


class AppState:
    def __init__(self, capacity: Optional[int], lockers_provider: Callable[[], Iterable[_LockerProto]]):
        """
        :param capacity: максимум владельцев, None = безлимит
        :param lockers_provider: функция без аргументов, возвращающая итерируемую коллекцию локеров.
                                 Каждый локер обязан иметь поля .number (int|None) и .owner (str).
        """
        if capacity is not None:
            try:
                capacity = int(capacity)
                assert capacity >= 0
            except Exception:
                raise ValueError("capacity должен быть неотрицательным целым или None")
        self.capacity: Optional[int] = capacity
        self._lockers_provider = lockers_provider

    # ---------------- occupancy ----------------
    def occupied_count(self) -> int:
        """Количество локеров с непустым владельцем."""
        cnt = 0
        for it in self._iter_lockers_safely():
            if getattr(it, "owner", "").strip():
                cnt += 1
        return cnt

    def can_add_one_owner(self) -> bool:
        """Можно ли добавить ещё одного НЕпустого владельца с учётом вместимости."""
        if self.capacity is None:
            return True
        return self.occupied_count() < int(self.capacity)

    def can_assign_owner(self, old_owner: str, new_owner: str) -> bool:
        """
        Проверка «можно ли присвоить владельца»:
        - если new_owner пустой → всегда можно (снятие владельца).
        - если old пустой, new непустой → нужна свободная вместимость.
        - если old и new непустые (замена строки владельца) → ок, занятость не меняется.
        """
        new_owner = (new_owner or "").strip()
        old_owner = (old_owner or "").strip()
        if not new_owner:
            return True
        if not old_owner and new_owner:
            # было пусто → станет занято: потребуется одно место
            return self.can_add_one_owner()
        # было занято → останется занято: лимит не меняется
        return True

    # ---------------- numbering ----------------
    def number_exists(self, number: int, *, exclude_obj: Optional[Any] = None) -> bool:
        """Проверяет, занят ли номер (игнорирует None, можно исключить конкретный объект)."""
        try:
            number = int(number)
        except Exception:
            return False
        for it in self._iter_lockers_safely():
            if exclude_obj is not None and it is exclude_obj:
                continue
            num = getattr(it, "number", None)
            if num is None:
                continue
            try:
                if int(num) == number:
                    return True
            except Exception:
                continue
        return False

    def next_free_number(self, start_from: int = 1) -> int:
        """Возвращает следующий свободный НЕотрицательный номер, начиная с start_from."""
        if start_from < 0:
            start_from = 0
        used = set()
        for it in self._iter_lockers_safely():
            num = getattr(it, "number", None)
            if num is None:
                continue
            try:
                used.add(int(num))
            except Exception:
                continue
        n = start_from
        while n in used:
            n += 1
        return n

    # ---------------- internals ----------------
    def _iter_lockers_safely(self) -> Iterable[_LockerProto]:
        """Безопасный итератор: защищаемся от странностей провайдера."""
        try:
            for it in self._lockers_provider():
                # минимальная sanity-проверка
                if hasattr(it, "number") and hasattr(it, "owner"):
                    yield it
        except RuntimeError:
            # Qt иногда кидает во время мутаций коллекции; просто прекращаем итерацию
            return
