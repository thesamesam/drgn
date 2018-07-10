from drgn.dwarf import Die
from typing import List


class DwarfIndex:
    address_size: int
    files: List[str]
    def __init__(self, *paths: str) -> None: ...
    def add(self, *paths: str) -> None: ...
    def find(self, name: str, tag: int = ...) -> List[Die]: ...
