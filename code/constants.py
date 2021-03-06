import sys

'''
MIT Licensed by Shubhayu Das, Veerendra S Devaraddi, Sai Manish Sasanapuri, copyright 2021

Developed for Processor Architecture course assignments 1 and 3 - Tomasulo Out-Of-Order Machine

This file contains some important constants that are used to modify the behaviour of the entire program.
'''

# Some variables that affect the output of the program
# Set DEBUG to True to enable text output to the terminal
DEBUG = False
VERSION = "2.0.0"

# Font size for the text in the GUI
# Decrease if content doesn't seem to fitting in properly

if sys.platform == 'win32':
    GUI_FONTSIZE = 12
else:
    GUI_FONTSIZE = 16

# CYCLE_DURATION sets the time period of each clock cycle.
# Increase this value(in milliseconds) to make each cycle last longer in the simulation
CYCLE_DURATION = 200    # in ms

# Bit width of the data used by the processor
WORD_SIZE = 32

# Size of the various caches
L1D_CACHE_SIZE = 2
L2D_CACHE_SIZE = 4

# Number of ways in the cache
L1D_WAYS = 2
L2D_WAYS = 2

# Latencies for accessing various levels of the cache
L1D_CACHE_LATENCY = 1
L2D_CACHE_LATENCY = 5
MEMORY_LATENCY = 10

# Prefetcher
PREFETCHER_ON = True

# The number of cycles taken by each supported instruction to execute
NumCycles = {
    "ADD": 1,
    "ADDI": 1,
    "SUB": 1,
    "MUL": 10,
    "DIV": 40,
    "LW": 3,
    "SW": 5,
    "BNE": 1,
    "BEQ": 1,
}

# This class is NOT to be modified. Represents the execution states of each instruction


class RunState:
    NOT_STARTED = "NOT STARTED"
    RS = "RS"
    EX_START = "EX_STARTED"
    EX_END = "EX_END"
    CDB = "CDB"
    COMMIT = "COMMIT"
    MEM_WRITE = "MEM_WRITE"


# Stores the number of ARF registers to generate and display(RISC-V has 32)
LIMIT = 10

# The name of the different reservation station groups
ADD_SUB = "ADD/SUB"
MUL_DIV = "MUL/DIV"
