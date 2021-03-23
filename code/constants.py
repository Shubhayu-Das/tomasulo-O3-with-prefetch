'''
MIT Licensed by Shubhayu Das, copyright 2021

Developed for Processor Architecture course assignment 1 - Tomasulo Out-Of-Order Machine

This file contains some important constants that are used to modify the behaviour of the entire program.
'''

# Some variables that affect the output of the program
# Set DEBUG to True to enable text output to the terminal
DEBUG          = False
VERSION        = "1.1.0"

# CYCLE_DURATION sets the time period of each clock cycle.
# Increase this value(in milliseconds) to make each cycle last longer in the simulation
CYCLE_DURATION = 1000    # in ms

# The number of cycles taken by each supported instruction to execute
NumCycles = {
    "ADD": 1,
    "SUB": 1,
    "MUL": 10,
    "DIV": 40,
    "LW": 5
}

# This class is NOT to be modified. Represents the execution states of each instruction
class RunState:
    NOT_STARTED = "NOT STARTED"
    RS          = "RS"
    EX_START    = "EX_STARTED"
    EX_END      = "EX_END"
    CDB         = "CDB"
    COMMIT      = "COMMIT"        

# Stores the number of ARF registers to generate and display(RISC-V has 32)
LIMIT          = 10

# The name of the different reservation station groups
ADD_SUB = "ADD/SUB"
MUL_DIV = "MUL/DIV"    