class Prefetcher:
    def __init__(self, size):
        self._size = size

    def prefetch_address(self, addr):
        return (addr+1) % self._size
