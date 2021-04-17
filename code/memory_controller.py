import os
from helpers import pad
from constants import WORD_SIZE, L1D_CACHE_SIZE, L2D_CACHE_SIZE

from cache import Cache


class MemoryController:
    def __init__(self, mem_file, enable_L1=False, enable_L2=False):
        self_L1D = None
        self_L2D = None
        
        if enable_L1:
            self._L1D = Cache(L1D_CACHE_SIZE, "L1D")
        
        if enable_L2:
            self._L2D = Cache(L2D_CACHE_SIZE, "L2D")

        if os.path.exists(mem_file):
            self._mem_file = mem_file
        else:
            print("Memory file not found")
            return

        self._memory = []
        self._size = 0

        self.load_memory()

    def load_memory(self):
        with open(self._mem_file, 'r') as dataMemory:
            self._memory = dataMemory.readlines()

        self._memory = [line.replace(" ", "").strip() for line in self._memory]
        self._memory = [int(line, 2) for line in self._memory]

        self._size = len(self._memory)
        print("Memory loaded of size: ", self._size)

    def save_memory(self):
        write_buffer = [pad(bin(line), WORD_SIZE)+"\n" for line in self._memory]
        if len(write_buffer) != self._size:
            return False

        with open(self._mem_file, 'w') as dataMemory:
            dataMemory.writelines(write_buffer)

        return True

    def mem_write(self, result):
        addr, data = result

        if addr > self._size:
            return False

        # TODO: add caches in here

        self._memory[addr] = data
        self.save_memory()
        return True

    def get_memory_entry(self, addr):
        if addr > self._size:
            return False

        # TODO: add caches in here

        return self._memory[addr]

    # Get the entire memory, for the GUI
    def get_memory(self):
        return [f"0b{pad(bin(line), WORD_SIZE)}" for line in self._memory]

    def get_l1_cache(self):
        return self._L1D.get_cache()

    def get_l2_cache(self):
        return self._L2D.get_cache()