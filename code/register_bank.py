'''
MIT Licensed by Shubhayu Das, copyright 2021

Developed for Processor Architecture course assignment 1 - Tomasulo Out-Of-Order Machine

This file contains the data structure used to represent the ARF and every register in it.

Each 'register" actually stores a name, the value, a link and a busy bit. It does is
not literally a register, but a row in the ARF(Architectural Register File)
'''

from collections import defaultdict
from random import randint


# Data structure to represent a compound register
# Each "register" stores its name and value, along with a busy bit and the linked ROB entry
class Register:
    def __init__(self, name, value, busy=False, link=None):
        self._name = name
        self._value = value
        self._busy = busy
        self._link = link

    # Function to get the name of the register, used mainly for displaying
    def get_name(self):
        return self._name

    # function to get the value stored in the register
    def get_value(self):
        return self._value

    # Get the linked ROB entry. Returns None is the register is not linked to ROB
    def get_link(self):
        return self._link

    # Returns True if the register is linked to ROB and is waiting for a new value
    def is_busy(self):
        return self._busy

    # Function to update the value stored in the register
    def set_value(self, new_val):
        self._value = new_val

    # Function to set the link and the state of the register
    # Note that the link is of type 'str': the name of the ROB entry
    def set_link(self, link):
        self._link = link
        if link:
            self._busy = True
        else:
            self._busy = False

    def __str__(self):
        return f"[{'BUSY' if self._busy else 'FREE'}] Register: {self._name}: {self._busy}"


# Data structure to represent the ARF. Individual registers are stored in a dictionary
class RegisterBank:
    def __init__(self, name="", size=1, init="random"):
        self._name = name
        self._bank = defaultdict(None, {})

        # Perform random initialization of the ARF
        if init == "random":
            init = [randint(1, 101) for _ in range(size)]

        # Initialize the register with some initial value
        for i in range(0, size):
            self._bank.update({f"R{i}": Register(f"R{i}", init[i], False)})

    # Function to access a particular register, using its name
    def get_register(self, name):
        return self._bank[name]

    # Function to get all the entries in the ARF, mainly for displaying purposes
    def get_entries(self):
        return self._bank

    # Function to update the value of a particular ARF register
    # The input is a ROB entry, which contains the new value
    def update_register(self, robEntry):
        name = robEntry.get_destination().get_name()
        self._bank[name].set_value(robEntry.get_value())

        # Remove the link only if the links match
        # If they don't match, the register has been renamed again, the new link
        # needs to be preserved
        if self._bank[name].get_link() == robEntry.get_name():
            self._bank[name].set_link(None)

    def __str__(self):
        return f"<Register Bank {self._name} of size: {len(self._bank)}>"
