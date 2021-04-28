import os
from helpers import pad, dec2bin

from constants import WORD_SIZE, L1D_CACHE_LATENCY, L2D_CACHE_LATENCY, MEMORY_LATENCY, DEBUG
from constants import L1D_CACHE_SIZE, L2D_CACHE_SIZE, L1D_WAYS, L2D_WAYS
from constants import PREFETCHER_ON

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

        # checking for whether L1 cache is enabled or not.
        # If enabled then creating L1D cache with given cache size and number of ways, and replacement policy it uses

        if enable_L1:
            self._L1D = Cache(L1D_CACHE_SIZE, "L1D", L1D_WAYS, True, Replacement_policy(
                L1D_CACHE_SIZE, L1D_WAYS))  # have to update

        # checking for whether L1 cache is enabled or not.
        # If enabled then creating L1D cache with given cache size and number of ways, and replacement policy it uses

        if enable_L2:
            self._L2D = Cache(L2D_CACHE_SIZE, "L2D", L2D_WAYS,
                              True, Replacement_policy(L2D_CACHE_SIZE, L2D_WAYS))

        # Getting memory for memory accesses
        if os.path.exists(mem_file):
            self._mem_file = mem_file
        else:
            print("Memory file not found")
            return

        self._prefetcher = None

        # Checking for prefetcher is enabled or not.
        # If enabled, we are intializing the prefetcher - Here using
        if enable_prefetcher:
            self._prefetcher = Prefetcher(self._size)

        # list of dictionary({"address":prefetch_address,"value":mem_value,"count":MEMORY_LATENCY})
        self._prefetcher_queue = []

        # caching stats
        self._L1D_read_hits = 0
        self._L2D_read_hits = 0
        self._L1D_read_miss = 0
        self._L2D_read_miss = 0
        self._L1D_write_hits = 0
        self._L1D_write_miss = 0

        # prefeteching stats
        self._prefetched_addresses = []
        self._prefetch_hits = 0
        self._total_prefetches = 0

    # Loading data memory here

    def load_memory(self):
        with open(self._mem_file, 'r') as dataMemory:
            self._memory = dataMemory.readlines()

        self._memory = [line.replace(" ", "").strip() for line in self._memory]
        self._memory = [int(line, 2) for line in self._memory]

        self._size = len(self._memory)
        self._mem_busy_bit = [False for _ in range(self._size)]
        if DEBUG:
            print("Memory loaded of size: ", self._size)

    # Use to save the data in memory file
    def save_memory(self):
        write_buffer = [dec2bin(line, WORD_SIZE) +
                        "\n" for line in self._memory]
        if len(write_buffer) != self._size:
            return False

        with open(self._mem_file, 'w') as dataMemory:
            dataMemory.writelines(write_buffer)

        return True

    # if busy bit is set if that address line in memory is being used currently for lw sw operation.
    # if busy bit is 0 then we can access the address line in memory
    def mem_busy_bit_update(self, addr, busy_bit):
        self._mem_busy_bit[addr] = busy_bit

    # mem write function is used sw word instruction, basically write to memory instructions
    def mem_write(self, addr, data):
        if addr > self._size:
            return False

        if self._L1D.set_entry(addr, data):
            self._L1D_write_hits = self._L1D_write_hits + 1
            self._L2D.update_busy_bit(addr, True)
            self._mem_busy_bit[addr] = True
            return data
        else:
            self._L1D_write_miss = self._L1D_write_miss + 1
            write_back = self._L1D.add_entry(data, addr, True, True)
            if(write_back):
                if(self._L2D.has_entry(addr)):
                    self._L2D.set_entry(write_back[0], write_back[1])
                else:
                    write_back2 = self._L2D.add_entry(
                        write_back[1], write_back[0], True, True)
                    if(write_back2):
                        self._memory[write_back2[0]] = write_back2[1]
                        self.save_memory()
            return data

    # if busy bit is set if that address line in L1D and L2D caches is being used currently for lw sw operation.
    # if busy bit is 0 then we can access the address line in L1D and L2D caches
    def update_busy_bit(self, addr, value=False):
        self._L1D.update_busy_bit(addr, value)
        self._L2D.update_busy_bit(addr, value)
        self.mem_busy_bit_update(addr, True)

    # returns the how many clock cycles are required that memory access.
    # It varies if the entry is in L1D cache or L2D cahce or in memory
    def get_latency(self, addr):
        if(self._L1D.has_entry(addr)):
            return L1D_CACHE_LATENCY
        elif(self._L2D.has_entry(addr)):
            return L1D_CACHE_LATENCY+L2D_CACHE_LATENCY
        else:
            return L1D_CACHE_LATENCY+L2D_CACHE_LATENCY+MEMORY_LATENCY

    # this functions checks whether the latency of the memory line is satisfied to be prefetched or not.
    # If yes it prefetches the date and puts in L2D cache
    def prefetch_tick(self):
        pop_list = []
        for i in range(len(self._prefetcher_queue)):
            self._prefetcher_queue[i]['count'] = self._prefetcher_queue[i]['count'] - 1
            if(self._prefetcher_queue[i]['count'] == 0):
                self._L2D.add_entry(
                    self._prefetcher_queue[i]['value'], self._prefetcher_queue[i]['address'])
                self._prefetched_addresses.append(
                    self._prefetcher_queue[i]['address'])
                self._total_prefetches = self._total_prefetches + 1
                pop_list.append(i)
        for i in range(len(pop_list)):
            self._prefetcher_queue.pop(pop_list[i]-i)

    # mem write function is used lw word instruction, basically read from memory instructions
    def get_memory_entry(self, addr):
        if addr > self._size:
            return False

        # [data_at_location, n_cycles_needed_for_access]

        # prefetching part
        if(PREFETCHER_ON):
            prefetch_address = self._prefetcher.prefetch_address(addr)
            if not self._mem_busy_bit[prefetch_address]:
                mem_value = self._memory[prefetch_address]
                self._prefetcher_queue.append(
                    {"address": prefetch_address, "value": mem_value, "count": MEMORY_LATENCY})

        # accessing caches
        value = self._L1D.get_memory_entry(addr)
        if not value:
            self._L1D_read_miss = self._L1D_read_miss + 1
            value = self._L2D.get_memory_entry(addr)
            if not value:
                self._L2D_read_miss = self._L2D_read_miss + 1
                if self._mem_busy_bit[addr]:
                    return False
                else:
                    mem_value = self._memory[addr]
                    write_back = self._L2D.add_entry(mem_value, addr)
                    if(write_back):
                        self._memory[write_back[0]] = write_back[1]
                        self.save_memory()

                    write_back = self._L1D.add_entry(mem_value, addr)
                    if(write_back):
                        if(self._L2D.has_entry(addr)):
                            self._L2D.set_entry(write_back[0], write_back[1])
                        else:
                            write_back2 = self._L2D.add_entry(
                                write_back[1], write_back[0], True, True)
                            if(write_back2):
                                self._memory[write_back2[0]] = write_back2[1]
                                self.save_memory()

                    return [mem_value, L1D_CACHE_LATENCY+L2D_CACHE_LATENCY+MEMORY_LATENCY]
            else:
                self._L2D_read_hits = self._L2D_read_hits + 1

                # updating prefetcher stats
                if addr in self._prefetched_addresses:
                    self._prefetch_hits = self._prefetch_hits + 1
                # end of stats update

                write_back = self._L1D.add_entry(value, addr)
                if(write_back):
                    if(self._L2D.has_entry(addr)):
                        self._L2D.set_entry(write_back[0], write_back[1])
                    else:
                        write_back2 = self._L2D.add_entry(
                            write_back[1], write_back[0], True, True)
                        if(write_back2):
                            self._memory[write_back2[0]] = write_back2[1]
                            self.save_memory()
                return [value[1], L1D_CACHE_LATENCY+L2D_CACHE_LATENCY]
        else:
            self._L1D_read_hits = self._L1D_read_hits + 1
            return [value[1], L1D_CACHE_LATENCY]

    # for stats
    def get_L1D_read_hits(self):
        return self._L1D_read_hits

    def get_L2D_read_hits(self):
        return self._L2D_read_hits

    def get_L1D_read_miss(self):
        return self._L1D_read_miss

    def get_L2D_read_miss(self):
        return self._L2D_read_miss

    def get_L1D_write_hits(self):
        return self._L1D_write_hits

    def get_L1D_write_miss(self):
        return self._L1D_write_miss

    def get_prefetch_hits(self):
        return self._prefetch_hits

    def get_prefetch_accuracy(self):
        if self._total_prefetches == 0:
            return 0

        return self._prefetch_hits/self._total_prefetches

    # Get the entire memory, for the GUI

    def get_memory(self):
        return [f"0b{dec2bin(line, WORD_SIZE)}" for line in self._memory]

    def get_l1_cache(self):
        return self._L1D.get_cache()

    def get_l2_cache(self):
        return self._L2D.get_cache()
