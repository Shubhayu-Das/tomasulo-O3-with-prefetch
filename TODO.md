## Things to implement for this assignment

### Things to update and fix

1. Implement store word,
2. two's complement in ```assembler.py```, ```instruction.py```, any other place where integer decoding is happening(```gui.py```?)
3. ```assembler.py```, ```instruction.py``` --> add support for SW
4. ```ls_buffer.py``` --> add support for SW

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

3. Add memory controller interface, which contains 2 levels of cache and data memory. Includes interfaces for using prefetching and replacement policies.
    ```python
    class MemoryController:

        # l1 -> cache object
        # l2 -> cache object

        # data_memory = load from file
        # replacement -> LRU
        # prefetchers -> None

        def get_from_addr(addr):
            # check_L1
            
            # check_prefetch
            # check_L2
            
            # ld_from_memory

            return data_source, value
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