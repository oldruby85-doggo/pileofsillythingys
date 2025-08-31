from dataclasses import dataclass
from typing import Optional

@dataclass
class LockerSnapshot:
    number: Optional[int]
    owner: str
    invno: str
    x: float
    y: float