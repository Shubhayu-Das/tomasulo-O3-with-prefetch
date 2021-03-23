'''
MIT Licensed by Shubhayu Das, copyright 2021

Developed for Processor Architecture course assignment 1 - Tomasulo Out-Of-Order Machine

This file contains the data structure used to represent the load sture table and every entry in it.

In this implementaito, the LoadStoreBuffer also contains the memory that is used to load in the variables.
This is essentially a counterpart of the RS, for LW/SW instructions
'''

import os
from constants import DEBUG
from instruction import Instruction


# Data structure to represent every entry in the load/store buffer 
class LoadStoreBufferEntry:
    def __init__(self, instr, ARFTable, memory):
        self._instruction = instr
        self._busy = True
        self._dest = instr.rd
        self._offset = int(instr.offset, 2)
        self._src_reg = ARFTable.get_register(instr.rs1)
        self._memory = memory

    # Function to tell whether the instruction is ready for executing
    # This function checks if the source register is ready
    def is_executeable(self):
        return not self._src_reg.is_busy()

    # Function to tell is the particular slot is busy or not. Pretty much vestigial
    # in my implementation
    def is_busy(self):
        return self._busy

    # Function to get the instruction associated with this entry
    def get_inst(self):
        return self._instruction

    # Function to get the result of the operation, when requested for
    # This function is capable of handling extra spaces, which can be added
    # to improve readability
    def get_result(self):
        index = self._src_reg.get_value() + self._offset
        if index < len(self._memory):
            self._busy = False
            return int(self._memory[index].replace(" ", "").strip(), 2)
        else:
            return False

    def __str__(self):
        return f"<LW/SW buffer entry: {self._instruction.dissamble()}, {self._busy}>"


# Data structure to represent the load/store buffer
class LoadStoreBuffer:
    def __init__(self, size, memoryFile):
        self._size = size
        self._buffer = [None for _ in range(size)]
        self._is_full = False
        self._index = 0

        # Load the memory into...memory
        if os.path.exists(memoryFile):
            with open(memoryFile, 'r') as dataMemory:
                self._memory = dataMemory.readlines()

    # Function to find the next free index to make an entry.
    # Could have simply ripped of a circular buffer, but meh
    def __update_free_index(self, update=False):
        counter = 0

        if update and not self._is_full:
            return

        while(counter < self._size):
            self._index = (self._index + 1) % self._size
            if self._buffer[self._index] is None:
                    break
            else:
                counter += 1

        if counter == self._size:
            self._is_full = True
            self._index = -1
        else:
            self._is_full = False

    # Function to add an entry to the LW/SW buffer
    def add_entry(self, instr, ARFTable):
        if self._is_full:
            if DEBUG:
                print("Entry Failed. Load store station is full")
            return False

        if isinstance(instr, Instruction):
            entry = LoadStoreBufferEntry(instr, ARFTable, self._memory)

        self._buffer[self._index] = entry
        if DEBUG:
            print(f"Added at LS buffer: {self._index + 1}")

        self.__update_free_index()
        return entry

    # Function to remove an entry from the LS buffer
    def remove_entry(self, entry):
        if isinstance(entry, Instruction):
            for e in self._buffer:
                if e:
                    if e._instruction.PC == entry.PC:
                        entry = e
                        break

        elif not isinstance(entry, LoadStoreBufferEntry):
            return False

        if entry in self._buffer:
            location = self._buffer.index(entry)
            self._buffer[location] = None
            self.__update_free_index(update=True)

            if DEBUG:
                print(f"Removed from RS{location + 1}")

            return True
        else:
            return False

    # Function to tell if the buffer is full and can't accept more dispatches
    def is_busy(self):
        return self._is_full

    # Function to get all the entries, for display purpose only
    def get_entries(self):
        return self._buffer

    def __str__(self):
        return f"<LW/SW Buffer>"