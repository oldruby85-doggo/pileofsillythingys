from __future__ import annotations
import json
from typing import Iterable, Tuple

LockerDict = dict  # {number, owner, invno, x, y}

def load_layout(path: str) -> Tuple[int | None, list[LockerDict]]:
    """Load JSON layout. Supports legacy list and new dict format. Returns (capacity, lockers)."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return None, list(_normalize_list(data))
    cap = None
    try:
        cap = int(data.get("capacity")) if "capacity" in data else None
    except Exception:
        cap = None
    lockers = list(_normalize_list(data.get("lockers", [])))
    return cap, lockers

def save_layout(path: str, capacity: int | None, lockers: Iterable[LockerDict]) -> None:
    payload = {"capacity": capacity, "lockers": list(lockers)}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

def _normalize_list(items: Iterable[dict]):
    for d in items:
        yield {
            "number": d.get("number"),
            "owner": (d.get("owner") or "").strip(),
            "invno": str(d.get("invno") or "").strip(),
            "x": float(d.get("x") or 0.0),
            "y": float(d.get("y") or 0.0),
        }
