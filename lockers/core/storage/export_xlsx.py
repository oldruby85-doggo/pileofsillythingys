from typing import Iterable
import openpyxl

def export_xlsx(path: str, lockers: Iterable[dict]) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Lockers"
    ws.append(["Локер", "Владелец", "Инв. №", "X", "Y"])
    lockers_sorted = sorted(lockers, key=lambda it: (it.get("number") is None, it.get("number") or 0))
    for it in lockers_sorted:
        ws.append([
            it.get("number") or "",
            it.get("owner", ""),
            it.get("invno", ""),
            float(it.get("x") or 0.0),
            float(it.get("y") or 0.0),
        ])
    wb.save(path)
