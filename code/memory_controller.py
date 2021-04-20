import os
from helpers import pad
from constants import WORD_SIZE, L1D_CACHE_LATENCY, L2D_CACHE_LATENCY, MEMORY_LATENCY, DEBUG
from constants import L1D_CACHE_SIZE, L2D_CACHE_SIZE, L1D_WAYS, L2D_WAYS

from cache import Cache
from cache_algos.prefetcher.next_line import Prefetcher
from cache_algos.replacement.lru import Replacement_policy


class MemoryController:
    def __init__(self, mem_file, enable_L1=True, enable_L2=True, enable_prefetcher=True):
        self._L1D = None
        self._L2D = None

        self._mem_file = mem_file
        self._memory = []
        self._mem_busy_bit = []
        self._size = 0

        self.load_memory()

        if enable_L1:
            self._L1D = Cache(L1D_CACHE_SIZE, "L1D", L1D_WAYS, False, Replacement_policy(
                L1D_CACHE_SIZE, L1D_WAYS))  # have to update

        if enable_L2:
            self._L2D = Cache(L2D_CACHE_SIZE, "L2D", L2D_WAYS,
                              True, Replacement_policy(L2D_CACHE_SIZE, L2D_WAYS))

        if os.path.exists(mem_file):
            self._mem_file = mem_file
        else:
            print("Memory file not found")
            return

        self._prefetcher = None
        if enable_prefetcher:
            self._prefetcher = Prefetcher(self._size)

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
        self._mem_busy_bit[addr] = busy_bit

    def mem_write(self, addr, data):
        if addr > self._size:
            return False

        if self._L1D.set_entry(addr, data):
            return data  # have to design still
        elif self._L2D.set_entry(addr, data):
            if(self._L1D.get_prefetch_on_miss()):
                self._L1D.add_entry(data, addr)
            return data  # have to still design
        else:
            if(self._L1D.get_prefetch_on_miss()):
                self._L1D.add_entry(data, addr)
            if(self._L2D.get_prefetch_on_miss()):
                self._L2D.add_entry(data, addr)
            self._memory[addr] = data
            self.save_memory()
            return True

    def update_busy_bit(self, addr, value=False):
        self._L1D.update_busy_bit(addr, value)
        self._L2D.update_busy_bit(addr, value)
        self.mem_busy_bit_update(addr, True)

    def get_latency(self, addr):
        if(self._L1D.has_entry(addr)):
            return L1D_CACHE_LATENCY
        elif(self._L2D.has_entry(addr)):
            return L1D_CACHE_LATENCY+L2D_CACHE_LATENCY
        else:
            return L1D_CACHE_LATENCY+L2D_CACHE_LATENCY+MEMORY_LATENCY

    def get_memory_entry(self, addr):
        if addr > self._size:
            return False

        # [data_at_location, n_cycles_needed_for_access]

        # prefetching part
        prefetch_address = self._prefetcher.prefetch_address(addr)
        if not self._mem_busy_bit[addr]:
            mem_value = self._memory[addr]

        self._L2D.add_entry(mem_value, addr)

        value = self._L1D.get_memory_entry(addr)
        if not value:
            value = self._L2D.get_memory_entry(addr)
            if not value:
                if self._mem_busy_bit[addr]:
                    return False
                else:
                    mem_value = self._memory[addr]
                    self._L1D.add_entry(mem_value, addr)
                    self._L2D.add_entry(mem_value, addr)
                    return [mem_value, L1D_CACHE_LATENCY+L2D_CACHE_LATENCY+MEMORY_LATENCY]
            else:
                self._L1D.add_entry(value, addr)
                return [value[1], L1D_CACHE_LATENCY+L2D_CACHE_LATENCY]
        else:
            return [value[1], L1D_CACHE_LATENCY]

    # Get the entire memory, for the GUI

    def get_memory(self):
        return [f"0b{pad(bin(line), WORD_SIZE)}" for line in self._memory]

    def get_l1_cache(self):
        return self._L1D.get_cache()

    def get_l2_cache(self):
        return self._L2D.get_cache()
