class Replacement_policy:
    # if more the lru number, least it is accessed

    def __init__(self, size, ways):
        self._size = size
        self._ways = ways
        self._no_rows = size/ways
        self._lru_number = [[i for i in range(self._ways)] for _ in range(
            int(self._size/self._ways))]

    def evict_index(self, addr):
        index = int(addr % self._no_rows)
        return self._lru_number[index].index(max(self._lru_number[index]))

    def update_lru(self, column_no, addr):
        index = int(addr % self._no_rows)
        previous_lru_value = self._lru_number[index][column_no]
        for i in range(self._ways):
            if(self._lru_number[index][i] < previous_lru_value):
                self._lru_number[index][i] = self._lru_number[index][i] + 1
        self._lru_number[index][column_no] = 0
