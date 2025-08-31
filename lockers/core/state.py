from __future__ import annotations
from typing import Callable, Iterable, Optional
from .models import LockerSnapshot

class AppState:
    """Простое состояние без Qt-сигналов. Читает локеры через провайдер."""

    def __init__(self, capacity: int = 100,
                 lockers_provider: Optional[Callable[[], Iterable[object]]] = None):
        self.capacity = capacity
        # провайдер отдаёт объекты с атрибутами number/owner/invno/pos()
        self._provider = lockers_provider or (lambda: ())

    # ------ чтение текущего набора локеров ------
    def _snapshots(self) -> list[LockerSnapshot]:
        snaps: list[LockerSnapshot] = []
        for it in self._provider():
            try:
                snaps.append(
                    LockerSnapshot(
                        number=getattr(it, "number", None),
                        owner=getattr(it, "owner", "") or "",
                        invno=str(getattr(it, "invno", "") or ""),
                        x=float(it.pos().x()),
                        y=float(it.pos().y()),
                    )
                )
            except Exception:
                continue
        return snaps

    # ------ бизнес-логика ------
    def occupied_count(self) -> int:
        return sum(1 for s in self._snapshots() if s.owner)

    def number_exists(self, num: int, exclude_obj: object | None = None) -> bool:
        for it in self._provider():
            if exclude_obj is not None and it is exclude_obj:
                continue
            if getattr(it, "number", None) == num:
                return True
        return False

    def next_free_number(self) -> int:
        used = {getattr(it, "number") for it in self._provider() if getattr(it, "number") is not None}
        n = 1
        while n in used:
            n += 1
        return n

    def can_add_one_owner(self) -> bool:
        if self.capacity is None:
            return True
        return self.occupied_count() < self.capacity

    def can_assign_owner(self, old_owner: str, new_owner: str) -> bool:
        return bool(old_owner) or not bool(new_owner.strip()) or self.can_add_one_owner()
