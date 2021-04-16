import os
from assembler import pad
from constants import WORD_SIZE


class MemoryController:
    def __init__(self, mem_file, L1=None, L2=None):
        self._l1 = L1
        self._l2 = L2

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

        self._memory[addr] = data
        self.save_memory()
        return True

    def get_entry(self, addr):
        if addr > self._size:
            return False

        return self._memory[addr]

    # Get the entire memory, for the GUI
    def get_memory(self):
        return [f"0b{pad(bin(line), WORD_SIZE)}" for line in self._memory]