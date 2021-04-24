from collections import defaultdict
from math import log2
from copy import deepcopy

class CacheEntry:
    def __init__(self):
        self._value = None
        self._tag = None
        self._valid_bit = False
        self._dirty_bit = False
        self._busy_bit = False

    def update_entry(self, new_value, tag, dirty_bit, valid_bit=True, busy_bit=False):
        self._value = new_value
        self._tag = tag
        self._dirty_bit = dirty_bit
        self._valid_bit = valid_bit
        self._busy_bit = busy_bit

    def evict(self):
        self._valid_bit = False

    def write(self, new_value, dirty_bit=True):
        self.updateEntry(new_value, dirty_bit, valid_bit=True)

    def update_busy_bit(self, busy_bit):
        self._busy_bit = busy_bit

    def update_dirty_bit(self, dirty_bit):
        self._dirty_bit = dirty_bit

    def update_tag(self, new_tag):
        self._tag = new_tag

    def get_busy_bit(self):
        return self._busy_bit

    def get_valid_bit(self):
        return self._valid_bit

    def get_dirty_bit(self):
        return self._dirty_bit

    def get_cache_value(self):
        return self._value

    def get_tag(self):
        return self._tag



    def __str__(self):
        return f"<[{'VALID' if self._valid_bit else 'INVALID'}]CacheEntry: tag: {self._tag}, value: {self._value} [{'NOT ' if not self._dirty_bit else ''}DIRTY]>"


class Cache:
    def __init__(self, size, name, ways=4, fetch_on_miss=False, replacement=None):
        self._size = size
        self._ways = ways
        self._n_rows = self._size // self._ways
        self._name = name
        self._replacement_policy = replacement
        self._fetch_on_miss = fetch_on_miss
        self._mem = [defaultdict(None, {}) for _ in range(self._n_rows)]

        for row in self._mem:
            for way in range(self._ways):
                row[f"way {way+1}"] = CacheEntry()

    # Function to get the name of the way, given the tag of the CacheEntry
    def __find_way(self, search_tag, row):
        for way, entry in row.items():
            if search_tag == entry.get_tag():
                return way

        return None

    # Function to get the index, tag, cache row entry and the way of an entry, if it exists
    def __find_location(self, addr):
        index = addr % self._n_rows
        tag = addr // self._n_rows
        row = self._mem[index]
        way = self.__find_way(tag, row)

        return index, tag, row, way

    # Function to update the value stored at a particular address
    def set_entry(self, addr, data):
        _, tag, row, way = self.__find_location(addr)

        if way:
            entry = row[way]

            col_no = int(way.split(" ")[-1]) - 1
            self._replacement_policy.update_lru(col_no, addr)

            entry.update_entry(data, tag, True,
                               valid_bit=True, busy_bit=True)
            return True
        else:
            return False

    # Function to get a CacheEntry, if it exists in the cache
    def get_memory_entry(self, addr):
        _, _, row, way = self.__find_location(addr)

        if way:
            entry = row[way]

            col_no = int(way.split(" ")[-1]) - 1
            self._replacement_policy.update_lru(col_no, addr)

            if entry.get_busy_bit():
                return False
            else:
                return [True, entry.get_cache_value()]
        else:
            return False

    # Function to check if a particular entry exists in the cache
    def has_entry(self, addr):
        _, _, row, way = self.__find_location(addr)

        if way:
            return True
        else:
            return False

    # Set the busy bit of a cache entry, if data @ addr is stored in cache
    def update_busy_bit(self, addr, value=False):
        _, _, row, way = self.__find_location(addr)

        if way:
            entry = row[way]
            entry.update_busy_bit(value)
            return True
        else:
            return False

    def update_dirty_bit(self, addr, value):
        _, _, row, way = self.__find_location(addr)

        if way:
            row[way].update_dirty_bit(value)
            return True
        else:
            return False

    # Function to add a new entry into the cache
    # Utilizes the replacement policy to find a new cache memory location
    def add_entry(self, data, addr,dirty_bit=False,busy_bit=False):
        evict_way_index = self._replacement_policy.evict_index(addr)
        evict_way = list(self._mem[0].keys())[evict_way_index]

        index = addr % self._n_rows

        evicting_entry = deepcopy(self._mem[index][evict_way])
        was_dirty_true = evicting_entry.get_dirty_bit()
        was_value = evicting_entry.get_cache_value()
        was_tag = evicting_entry.get_tag()

        tag = addr // self._n_rows

        for i in list(self._mem[0].keys()):
            if(self._mem[index][i].get_tag() == tag):
                return False

        updated_tag = addr // self._n_rows
        print("Updating tag ",tag," value ",data)
        self._mem[index][evict_way].update_entry(
            data, tag, dirty_bit, True, busy_bit)

        self._replacement_policy.update_lru(evict_way_index, addr)
        print(was_dirty_true,was_value)
        if(was_dirty_true):
            print("Evict tag ",was_tag," Value ",was_value)
            was_tag = int(was_tag*(2**log2(self._n_rows)))
            return [was_tag+index,was_value]
        else:
            return False

    # Check if prefetcher is to be used or not
    def get_prefetch_on_miss(self):
        return self._fetch_on_miss

    # Get the name of the cache
    def get_name(self):
        return self._name

    # For GUI, get the entire cache
    def get_cache(self):
        return self._mem
