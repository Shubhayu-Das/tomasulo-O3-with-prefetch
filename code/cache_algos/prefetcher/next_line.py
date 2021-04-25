class Prefetcher:
    def __init__(self, size: int) -> None:
        self._name: str = "Next Line"
        self._size: int = size

    def prefetch_address(self, addr: int) -> int:
        return (addr+1) % self._size

    def __str__(self) -> str:
        return self._name
