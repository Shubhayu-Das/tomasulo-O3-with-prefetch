'''
MIT Licensed by Shubhayu Das, copyright 2021

Developed for Processor Architecture course assignment 1 - Tomasulo Out-Of-Order Machine

This file contains the data structure used to represent the instruction table and every entry in it.

Each entry is a data structure that stores the cycle in which the instruction passed through different
stages of the pipeline. It is used to keep track of the state of execution of the instruction, along 
with the final outcome(result) of the instruction. This result is ideally supposed to come from a FPU,
but I am cheating here. The result is calculated by the reservation station.

This is by far the most important class, in terms of maintaining execution order
'''

from constants import DEBUG, NumCycles, RunState
from instruction import Instruction


# Data structure to represent each row of the instruction table
# Stores execution state information of the entire program
class InstructionTableEntry:
    def __init__(self, instruction):
        self._instruction = instruction
        self._state = RunState.NOT_STARTED
        self._rs_issue_cycle = ""
        self._exec_start = ""
        self._exec_complete = ""
        self._cdb_write = ""
        self._commit = ""
        self._counter = 0
        self._max_ticks = NumCycles[instruction.disassemble()["command"]]
        self._value = None

    # Function to record the issue of an instruction into the RS
    def rs_issue(self, cycle):
        self._state = RunState.RS
        self._rs_issue_cycle = cycle

    # Function to record the start of execution of the instruction
    def ex_start(self, cycle):
        self._state = RunState.EX_START
        self._exec_start = cycle
        self.ex_tick(cycle)

    # Function to count up on the number of cycles the instruction has executed for
    def ex_tick(self, cycle):
        if self._counter == self._max_ticks:
            self._exec_complete = cycle
            self._state = RunState.EX_END
        else:
            self._counter += 1

    # Function to record the cycle in which the CDB broadcast is done for the instruction
    def cdb_write(self, cycle):
        self._state = RunState.CDB
        self._cdb_write = cycle

    # Function to record the cycle in which the instruction is committed back to the ARF
    def commit(self, cycle):
        self._state = RunState.COMMIT
        self._commit = cycle

    # Function to update the result of the instruction, once it completes instruction
    def update_result(self, new_value):
        self._value = new_value
    
    # Function to get the current state of the instruction
    # Legal values include the members of the RunState class in constants.py
    def get_state(self):
        return self._state

    # Function to get the instruction stored in the instruction table entry
    def get_inst(self):
        return self._instruction

    # Function to return the result of the execution of the instruction
    def get_result(self):
        return self._value

    def __str__(self):
        return f"{self._instruction.str_disassemble()}\t\t{self._rs_issue_cycle} {self._exec_start}\
         {self._exec_complete} {self._cdb_write} {self._commit}"


# Data structure to represent the instruction table.
# The table consists of an array of InstructionTableEntry elements
class InstructionTable:
    def __init__(self, size):
        self._size = size
        self._index = 0
        self._entries = [None for _ in range(size)]

    # Function to add an entry to the instruction table
    # The index maintains the index of the next insertion as the size of the table is a constant
    def add_entry(self, instruction):
        self._entries[self._index] = InstructionTableEntry(instruction)
        self._index += 1

    # Function to get a particular entry, depending on the PC of the stored instruction
    # The entry is recognized using the instruction that it stores
    def get_entry(self, index):
        if isinstance(index, Instruction):
            for entry in self._entries:
                if entry.get_inst().PC == index.PC:
                    return entry

    # Function to get all the entries stored in the table
    # This function is used for checking and updating the states of all the instructions
    # It is further used by the GUI interface to display all the contents
    def get_entries(self):
        return list(filter(None, self._entries))

    def __str__(self):
        display = "Instruction\t\t\t\t\t\t\tRS Start Exec Start Exec End CDB Write commit\n"
        for entry in self._entries:
            display += f"{entry.__str__()}\n"

        return display