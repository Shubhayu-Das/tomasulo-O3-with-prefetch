'''
MIT Licensed by Shubhayu Das, copyright 2021

Developed for Processor Architecture course assignment 1 - Tomasulo Out-Of-Order Machine

This is the script for a basic RISC-V assembler. It only support LW, ADD, SUB, MUL and DIV instructions so far.
All are integer instructions only, although, the program by itself supports floating point numbers(cheating)
'''
import re
import sys


# Function to split the instruction string into opcode and registers(and offset if needed)
# This function is capable of handling comments too
def split_operands(program):
    program = [inst.split(";")[0] for inst in program]
    program = list(filter(None, program))
    program = [re.split(r",|\s", inst.strip()) for inst in program]
    program = [[word.upper().replace('X', '') for word in inst if word]
               for inst in program]
    program = [inst for inst in program if inst]

    return program


# Zero pad the binary numbers appropriately
def pad(number, n):
    number = number[2:]
    while len(number) < n:
        number = "0" + number

    return number


# The main assembler function, which contains the mapping between the instructions and their
# opcodes, function-7 and function-3 fields
def assembler(filename):
    outFile = ".".join([filename.split("/")[-1].split(".")[0], "bin"])
    program = []
    assembly = []

    mapping = {
        "ADD": {
            "funct7": "0000000",
            "funct3": "000",
            "opcode": "0110011"
        },
        "SUB": {
            "funct7": "0100000",
            "funct3": "000",
            "opcode": "0110011"
        },
        "MUL": {
            "funct7": "0000001",
            "funct3": "000",
            "opcode": "0110011"
        },
        "DIV": {
            "funct7": "0000001",
            "funct3": "100",
            "opcode": "0110011"
        },
        "LW": {
            "funct3": "010",
            "opcode": "1010011"
        },
    }

    # Read the source code
    with open(filename) as sourceCode:
        program = (sourceCode.readlines())

    # Split each instruction into requisite pieces
    program = split_operands(program)

    # Decode the split chunks into binary
    for i, inst in enumerate(program):
        if "LW" in inst:
            offset, rs1 = inst[2].split('(')

            offset = pad(bin(int(offset)), 12)
            rs1 = pad(bin(int(rs1.replace(')', ''))), 5)
            rd = pad(bin(int(inst[1])), 5)

            assembly.append(
                offset + rs1 + mapping["LW"]["funct3"] + rd + mapping["LW"]["opcode"])
        else:
            rd = pad(bin(int(inst[1])), 5)
            rs1 = pad(bin(int(inst[2])), 5)
            rs2 = pad(bin(int(inst[3])), 5)

            assembly.append(mapping[inst[0]]["funct7"] + rs2 + rs1 +
                            mapping[inst[0]]["funct3"] + rd + mapping[inst[0]]["opcode"])

    # Write the assembled binary into an output bin file
    with open(f"build/{outFile}", 'w') as destFile:
        for idx, inst in enumerate(assembly):
            destFile.write(inst)
            if idx < len(assembly) - 1:
                destFile.write("\n")

    return f"build/{outFile}"


# Check if a program was fed it, otherwise use a default
if len(sys.argv) < 2:
    print(f"Output generated to: {assembler('src/riscv_program.asm')}")
else:
    print(f"Output generated to: {assembler(sys.argv[1])}")
