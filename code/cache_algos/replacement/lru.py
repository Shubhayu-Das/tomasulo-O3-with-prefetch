from typing import List


# if more the lru number, least it is accessed
class Replacement_policy:
    def __init__(self, size: int, ways: int) -> None:
        self._name: str = "LRU"
        self._size: int = size
        self._ways: int = ways
        self._no_rows: int = size//ways
        self._lru_number: List[List[int]] = [[i for i in range(self._ways)] for _ in range(
            self._size//self._ways)]

    def evict_index(self, addr: int) -> int:
        index: int = addr % self._no_rows
        return self._lru_number[index].index(max(self._lru_number[index]))

    def update_lru(self, column_no: int, addr: int) -> None:
        index: int = addr % self._no_rows
        previous_lru_value: int = self._lru_number[index][column_no]

        for i in range(self._ways):
            if self._lru_number[index][i] < previous_lru_value:
                self._lru_number[index][i] = self._lru_number[index][i] + 1

        self._lru_number[index][column_no] = 0

    def __str__(self) -> str:
        return self._name
