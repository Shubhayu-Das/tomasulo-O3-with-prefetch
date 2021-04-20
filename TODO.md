## Things to implement for this assignment

### Things to update and fix

1. Implement 2's complement in ```helper.py```. Change everywhere else

---------------------------------

### New things to add

2. Implement basic structure of the prefetcher(after all of above are complete). The base line prefetcher will be next line prefetcher only.
    ```python
    class prefetcher:
        # get address of data that needs to be prefetched.
        def fetch_addr(self):
            pass
    ```

3. Implement a basic cache replacement policy(after all till point 3 are complete). The baseline policy will be LRU.
    ```python
    class replacement:
        # returns the address that will be replaced
        def replace_addr(self):
            pass
    ```