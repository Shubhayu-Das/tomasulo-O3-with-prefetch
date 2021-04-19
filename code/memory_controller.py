import os
from helpers import pad
from constants import WORD_SIZE, L1D_CACHE_LATENCY, L2D_CACHE_LATENCY, MEMORY_LATENCY, DEBUG
from constants import L1D_CACHE_SIZE, L2D_CACHE_SIZE, L1D_WAYS, L2D_WAYS

from cache import Cache


class MemoryController:
    def __init__(self, mem_file, enable_L1=False, enable_L2=False):
        self._L1D = None
        self._L2D = None

        if enable_L1:
            self._L1D = Cache(L1D_CACHE_SIZE, "L1D", L1D_WAYS)

        if enable_L2:
            self._L2D = Cache(L2D_CACHE_SIZE, "L2D", L2D_WAYS)

        if os.path.exists(mem_file):
            self._mem_file = mem_file
        else:
            print("Memory file not found")
            return

        self._memory = []
        self._mem_busy_bit = []
        self._size = 0

        self.load_memory()

    def load_memory(self):
        with open(self._mem_file, 'r') as dataMemory:
            self._memory = dataMemory.readlines()

        self._memory = [line.replace(" ", "").strip() for line in self._memory]
        self._memory = [int(line, 2) for line in self._memory]

        self._size = len(self._memory)
        self._mem_busy_bit = [False for _ in range(self._size)]
        if DEBUG:
            print("Memory loaded of size: ", self._size)

    def save_memory(self):
        write_buffer = [pad(bin(line), WORD_SIZE) +
                        "\n" for line in self._memory]
        if len(write_buffer) != self._size:
            return False

        with open(self._mem_file, 'w') as dataMemory:
            dataMemory.writelines(write_buffer)

        return True

    def mem_busy_bit_update(self, addr, busy_bit):
        print(addr, len(self._mem_busy_bit))
        self._mem_busy_bit[addr] = busy_bit

    def mem_write(self, addr, data):
        if addr > self._size:
            return False

        # TODO: add caches in here
        if self._L1D.set_entry(addr, data):
            return data #have to design still
        elif self._L2D.set_entry(addr, data):
            return data #have to still design
        else:
            self._memory[addr] = data
            self.save_memory()
            return True

    def set_busy_bit(self, addr):
        self._L1D.set_busy_bit(addr)
        self._L2D.set_busy_bit(addr)
        self.mem_busy_bit_update(addr, True)

    def clear_busy_bit(self, addr):
        self._L1D.clear_busy_bit(addr)
        self._L2D.clear_busy_bit(addr)
        self.mem_busy_bit_update(addr,False)
    
    def get_latency(self,addr):
        if(self._L1D.is_entry_there(addr)):
            return L1D_CACHE_LATENCY
        elif(self._L2D.is_entry_there(addr)):
            return L1D_CACHE_LATENCY+L2D_CACHE_LATENCY
        else:
            return L1D_CACHE_LATENCY+L2D_CACHE_LATENCY+MEMORY_LATENCY
    
    def get_memory_entry(self, addr):
        if addr > self._size:
            return False

        # TODO: add caches in here
        # TODO: This function MUST return an array of the form:
        # [data_at_location, n_cycles_needed_for_access]
        value = self._L1D.get_memory_entry(addr)
        if not value:
            value = self._L2D.get_memory_entry(addr)
            if not value:
                return [self._memory[addr],L1D_CACHE_LATENCY+L2D_CACHE_LATENCY+MEMORY_LATENCY] 
            else:
                return [value[1],L1D_CACHE_LATENCY+L2D_CACHE_LATENCY]
        else:
            return [value[1],L1D_CACHE_LATENCY]
        # As a proof of working, I have randomly set 10 for now
        # The second value will change depending on cache config
        return [self._memory[addr], 10]

    # Get the entire memory, for the GUI
    def get_memory(self):
        return [f"0b{pad(bin(line), WORD_SIZE)}" for line in self._memory]

    def get_l1_cache(self):
        return self._L1D.get_cache()

    def get_l2_cache(self):
        return self._L2D.get_cache()
