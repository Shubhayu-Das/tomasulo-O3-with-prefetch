## Things to implement for this assignment

### Things to update and fix

*Support for SW added by Shubhayu on 16-04-21 0200*
*Added dedicated Memory controller, as the only point of access to memory: Shubhayu on 16-04-21 1030*

1. Convert all integer to binary conversions to 2's complement format
2. Add support for caches in memory controller, load_memory must return data source too

---------------------------------

### New things to add

1. Add class for cache entries
    ```python
    class CacheEntry
        def __init__(self):
            self._value = 
            self._tag = 
            self._dirty_bit = 
    ```

2. Add class for general cache structure. Should *atleast* implement the following interfaces:
    ```python
        class Cache:
            def __init__(self):
                self._mem = [None for _ in range(size)]
                self._size = 
                name

            def set_entry(self, entry, addr):
                self._mem[addr] = entry

            def get_entry(self, addr):
                pass

            def remove_entry(self, addr):
                pass

            # For GUI
            def get_mem(self):
                return sef._mem
    ```

4. Implement basic structure of the prefetcher(after all of above are complete). The base line prefetcher will be next line prefetcher only.
    ```python
    class prefetcher:
        # get address of data that needs to be prefetched.
        def fetch_addr(self):
            pass
    ```

5. Implement a basic cache replacement policy(after all till point 3 are complete). The baseline policy will be LRU.
    ```python
    class replacement:
        # returns the address that will be replaced
        def replace_addr(self):
            pass
    ```