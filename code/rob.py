'''
MIT Licensed by Shubhayu Das, copyright 2021

Developed for Processor Architecture course assignment 1 - Tomasulo Out-Of-Order Machine

This file contains the data structure used to represent the ROB and each of its entries
The ROB kills two birds with one stone: performs register renaming to prevent false 
dependencies. It is also used for in-order writeback, which helps preserve the machine
state in case of faults/errors, leading to improved error handling
'''

from collections import defaultdict

from constants import DEBUG


# Data structure to represent each entry of the ROB
# Stores the Instruction object, the desination Register and the value to be written
class ROBEntry:
    def __init__(self, inst, destination, value, name=""):
        self._name = name
        self._inst = inst
        self._dest = destination
        self._value = value

    # Function to set the value of the ROB entry
    def set_value(self, new_val):
        self._value = new_val

    # Function to get the value stored in the ROB
    def get_value(self):
        return self._value

    # Function to get the name of the ROB entry
    def get_name(self):
        return self._name

    # Function to get the destination Register
    def get_destination(self):
        return self._dest

    # Function to get the instruction associated with the ROB entry
    def get_inst(self):
        return self._inst

    def __str__(self):
        return f"{self._name}, inst={self._inst}, val={self._value}, dest={self._dest}"


# Data structure to represent the ROB table, a cicular buffer effectively
# The ROBEntry elements aer stored in a dictionary
class ROBTable:
    def __init__(self, size=8):
        self._tail = 1
        self._head = 1
        self._bank = defaultdict(None, {})

        for i in range(1, size+1):
            self._bank.update({f"ROB{i}": None})

    # Function to add an entry to the head of the ROB, if possible 
    def add_entry(self, inst, dest):
        if self._bank[f"ROB{self._head}"]:
            if DEBUG:
                print("ROB FULL")
            return False

        name = f"ROB{self._head}"

        new_entry = ROBEntry(
            inst=inst,
            destination=dest,
            value="NA",
            name=name
        )

        self._bank[name] = new_entry
        self._head += 1

        if self._head > len(self._bank):
            self._head = 1

        if DEBUG:
            print(f"ADDED to ROB @ {new_entry}")

        return name

    # Function to update the value stored in the ROB
    # This is ONLY used after a CDB broadcast
    def update_value(self, inst, value):
        for entry in list(self._bank.values()):
            if entry:
                if entry.get_inst().PC == inst.PC:
                    entry.set_value(value)
                    return entry

    # Function to remove and return the entry at the tail of the ROB
    def remove_entry(self):
        if not self._bank[f"ROB{self._tail}"]:
            if DEBUG:
                print("ROB EMPTY")
            return False
        
        removedValue = self._bank[f"ROB{self._tail}"]
        self._bank[f"ROB{self._tail}"] = None
        self._tail += 1

        if self._tail > len(self._bank):
            self._tail = 1

        if DEBUG:
            print(f"REMOVED from ROB @ {removedValue}")

        return removedValue

    # Function to get the value stored in a particular ROBEntry
    def get_value(self, entry):
        if entry:
            return self._bank[entry].get_value()
        else:
            return False

    # Function to return all the ROB entries, for displaying purposes only
    def get_entries(self):
        return self._bank
