from collections import defaultdict


class CacheEntry:
    def __init__(self):
        self._value = None
        self._valid_bit = False
        self._dirty_bit = False
        sefl._busy_bit = False

    def update_entry(self, new_value, dirty_bit, valid_bit=True,busy_bit=False):
        self._value = new_value
        self._dirty_bit = dirty_bit
        self._valid_bit = valid_bit
        sefl._busy_bit = busy_bit
    def evict(self):
        self._valid_bit = False

    def write(self, new_value, dirty_bit=True):
        self.updateEntry(new_value, dirty_bit, valid_bit=True)

    def update_busy_bit(self,busy_bit):
        self._busy_bit = busy_bit

    def get_busy_bit(self):
        return self._busy_bit

    def get_valid_bit(self):
        return self._valid_bit

    def get_dirty_bit(self):
        return self._dirty_bit

    def get_cache_value(self):
        return self._value

    def __str__(self):
        return f"<[{'VALID' if self._valid_bit else 'INVALID'}]CacheEntry: tag: , value: {self._value} [{'NOT ' if not self._dirty_bit else ''}DIRTY]>"


class Cache:
    def __init__(self, size, name, ways = 4, fetch_on_miss=False, prefetcher=None, replacement=None):
        # TODO: decide on number of ways
        self._fetch_on_miss = fetch_on_miss
        self._size = size
        self._ways = ways
        self._name = name
        self._prefetcher = prefetcher
        self._replacement_policy = replacement
        self._mem = [defaultdict(lambda :False,dict((str(val)+"way",None) for val in range(1,ways+1))) for _ in range(int(self._size/self._ways))]

    def set_entry(self, addr, value):
        no_rows = self._size/self._ways
        index = int(addr % no_rows)
        tag = int(addr/no_rows)
        stat = self._mem[index][tag]
        if stat:
            entry = self._mem[index][tag]
            entry.update_entry(value,1)
            return True
        else:
            return False
  

    def get_memory_entry(self, addr):
        no_rows = self._size/self._ways
        index = int(addr % no_rows)
        tag = int(addr/no_rows)
        entry = self._mem[index][tag]
        if entry:
            return [True,value.get_cache_value()]
        else:
            return False

    def is_entry_there(self, addr):
        no_rows = self._size/self._ways
        index = int(addr % no_rows)
        tag = int(addr/no_rows)
        entry = self._mem[index][tag]
        if entry:
            return True
        else:
            return False

    # Uses replacement policy to make entry into cache
    def remove_entry(self, addr):
        no_rows = self._size/self._ways
        index = int(addr % no_rows)
        tag = int(addr/no_rows)
        self._mem
    
    def set_busy_bit(self, addr):
        no_rows = self._size/self._ways
        index = int(addr % no_rows)
        tag = int(addr/no_rows)
        stat = self._mem[index][tag]
        if stat:
            entry = self._mem[index][tag]
            entry.update_busy_bit(True)
            return True
        else:
            return False

    def clear_busy_bit(self, addr):
        no_rows = self._size/self._ways
        index = int(addr % no_rows)
        tag = int(addr/no_rows)
        stat = self._mem[index][tag]
        if stat:
            entry = self._mem[index][tag]
            entry.update_busy_bit(False)
            return True
        else:
            return False


    def add_entry(self, data, addr):
        pass

    def get_name(self):
        return self._name

    # For GUI
    def get_cache(self):
        return self._mem
