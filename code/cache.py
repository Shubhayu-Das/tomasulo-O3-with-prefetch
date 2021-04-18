from collections import defaultdict


class CacheEntry:
    def __init__(self):
        self._tag = None
        self._value = None
        self._valid_bit = False
        self._dirty_bit = False

    def update_entry(self, new_tag, new_value, dirty_bit, valid_bit=True):
        self._tag = new_tag
        self._value = new_value
        self._dirty_bit = dirty_bit
        self._valid_bit = valid_bit

    def evict(self):
        self._valid_bit = False

    def write(self, new_value, dirty_bit=True):
        self.updateEntry(self._tag, new_value, dirty_bit, valid_bit=True)

    def get_valid_bit(self):
        return self._valid_bit

    def get_dirty_bit(self):
        return self._dirty_bit

    def get_cache_value(self):
        return self._value

    def get_cache_tag(self):
        return self._tag

    def __str__(self):
        return f"<[{'VALID' if self._valid_bit else 'INVALID'}]CacheEntry: tag: {self._tag}, value: {self._value} [{'NOT ' if not self._dirty_bit else ''}DIRTY]>"


class Cache:
    def __init__(self, size, name, prefetcher=None, replacement=None):
        # TODO: decide on number of ways
        self._mem = []
        self._size = size
        self._name = name
        self._prefetcher = prefetcher
        self._replacement_policy = replacement

    def set_entry(self, entry, addr):
        pass

    def get_memory_entry(self, addr):
        pass

    def remove_entry(self, addr):
        pass

    # Uses replacement policy to make entry into cache
    def add_entry(self, data, addr):
        pass

    def get_name(self):
        return self._name

    # For GUI
    def get_cache(self):
        return sef._mem
