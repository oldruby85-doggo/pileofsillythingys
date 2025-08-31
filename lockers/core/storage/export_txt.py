from typing import Iterable

def export_txt(path: str, lockers: Iterable[dict]) -> None:
    lockers_sorted = sorted(lockers, key=lambda it: (it.get("number") is None, it.get("number") or 0))
    with open(path, "w", encoding="utf-8") as f:
        for it in lockers_sorted:
            num = "" if it.get("number") is None else str(it.get("number"))
            f.write(f"{num}\t{it.get('owner','')}\t{it.get('invno','')}\n")
