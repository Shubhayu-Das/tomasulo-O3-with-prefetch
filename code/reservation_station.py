'''
MIT Licensed by Shubhayu Das, copyright 2021

Developed for Processor Architecture course assignment 1 - Tomasulo Out-Of-Order Machine

This file contains the data structure used to represent the reservation stations(RS) and their entries

The RSes are used to keep track of the instructions and their source operands until
they start executing. Once they start executing, they are removed from the corresponding RS.
'''
from constants import DEBUG
from instruction import Instruction


class ReservationStationEntry:
    def __init__(self, instr, ARFTable, busy=True):
        self._instruction = instr
        self._busy = busy
        self._dest = instr.rd
        self._rob_updated = False
        self._value = None

        # Check if the value is available, else get the tag
        self._src_val1, self._src_tag1 = self.__getSrcValTag(ARFTable.get_register(instr.rs1))
        self._src_val2, self._src_tag2 = self.__getSrcValTag(ARFTable.get_register(instr.rs2))       

    # Function to check if the ARF entry is valid, and get the value/tag accordingly
    def __getSrcValTag(self, source):
        if source.is_busy():
            return "-", source.get_link()
        else:
            return source.get_value(), "-"

    # Function to check if the current instruction is ready to start executing
    # This is done by checking both the operands are available and not waiting for
    # their value from the ROB tag
    def is_executeable(self):
        if self._rob_updated:
            self._rob_updated = False
            return False
        else:
            condition = (self._src_val1 != "-") and (self._src_val2 != "-")
            if condition:
                self._value = self.__exec()
            
            return condition

    # Private function to get the calculated value of the instructions
    def __exec(self):
        command = self._instruction.disassemble()["command"]
        lookup = {
            "ADD": lambda x, y: round(x+y, 2),
            "SUB": lambda x, y: round(x-y, 2),
            "MUL": lambda x, y: round(x*y, 2),
            "DIV": lambda x, y: round(x/y, 2),
        }

        try:
            return lookup[command](self._src_val1, self._src_val2)
        except ZeroDivisionError:
            print("Divisor is 0!: ", self._src_val1, self._src_val2)
            return 0

    # Function to return the resultant value of the instruction
    def get_result(self):
        return self._value

    # Function to return the Instruction associated with this entry
    def get_inst(self):
        return self._instruction

    # Function to get the destination of this entry
    def get_destination(self):
        return self._dest

    def __str__(self):
        return f"""ReservationStationEntry:
                    Instruction: {self._instruction.disassemble()}
                    Busy State: {self._busy}
                    Destination: {self._dest}
                    Source Tag 1: {self._src_tag1}
                    Source Tag 2: {self._src_tag2}
                    Source Value 1: {self._src_val1}
                    Source Value 2: {self._src_val2}
                """


# Data structure to represent the RSes 
class ReservationStation:
    def __init__(self, inst_type, size):
        self._type = inst_type
        self._is_full = False
        self._size = size
        self._buffer = [None for _ in range(size)]
        self._index = 0

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

    # Function to add an entry into the RS
    # The ARF is needed to get the actual source Registers
    def add_entry(self, instruction, ARFTable):
        if self._is_full:
            if DEBUG:
                print("Reservation station is full")
            return False

        if isinstance(instruction, Instruction):
            entry = ReservationStationEntry(instruction, ARFTable)
        
        else:
            return False

        self._buffer[self._index] = entry
        if DEBUG:
            print(f"Added at RS{self._index + 1}")

        self.__update_free_index()
        return True

    # Function to update the values of the RS entries on a CDB broadcast
    def updateEntries(self, arf, robEntry):
        for entry in self._buffer:
            if entry and robEntry:
                if entry._src_tag1 == robEntry.get_name():
                    entry._src_val1 = robEntry.get_value()
                    entry._src_tag1 = "-"
                    entry._rob_updated = True

                if entry._src_tag2 == robEntry.get_name():
                    entry._src_val2 = robEntry.get_value()
                    entry._src_tag2 = "-"
                    entry._rob_updated = True

    # Function to remove an entry from the RS when it starts executing
    def remove_entry(self, entry):
        if isinstance(entry, Instruction):
            for e in self._buffer:
                if e:
                    if e._instruction.PC == entry.PC:
                        entry = e
                        break

        elif not isinstance(entry, ReservationStationEntry):
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

    # Function to tell whether the RS is full and can't accept more dispatches
    def is_busy(self):
        return self._is_full

    # Function to get a particular entry, given the associated Instruction(using PC)
    def get_entry(self, instr):
        if isinstance(instr, Instruction):
            for entry in self._entries:
                if entry.get_inst().PC == instr.PC:
                    return entry
        else:
            return None

    # Function to get all the valid entries, mainly for displaying purposes
    def get_entries(self):
        return list(filter(None, self._buffer))

    def __str__(self):
        return f"""Reservation Station for {self._type}.
                    {self._buffer}
                """
