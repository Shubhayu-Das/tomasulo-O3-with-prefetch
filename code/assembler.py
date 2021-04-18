'''
MIT Licensed by Shubhayu Das, copyright 2021

Developed for Processor Architecture course assignment 1 - Tomasulo Out-Of-Order Machine

This is the script for a basic RISC-V assembler. It only support LW, ADD, SUB, MUL and DIV instructions so far.
All are integer instructions only. Execution generates integers only [updated].
'''
import re
import sys

from helpers import pad

# Function to split the instruction string into opcode and registers(and offset if needed)
# This function is capable of handling comments too

def clean_program(program):
    program = [inst.split(";")[0].strip() for inst in program]
    program = list(filter(None, program))
    
    return program

def split_operands(program):
    program = [re.split(r",|\s", inst) for inst in program]
    program = [[re.sub(r'X(\d)', r'\1', word.upper()) for word in inst if word]
               for inst in program]
    program = [inst for inst in program if inst]

    return program

# The main assembler function, which contains the mapping between the instructions and their
# opcodes, function-7 and function-3 fields


def assembler(filename):
    outFile = ".".join([filename.split("/")[-1].split(".")[0], "bin"])
    program = []
    assembly = []
    branch_mappings = {}

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
            "opcode": "0000011"
        },
        "SW": {
            "funct3": "010",
            "opcode": "0100011"
        },
        "BEQ": {
            "funct3": "000",
            "opcode": "1100011"
        },
        "BNE": {
            "funct3": "001",
            "opcode": "1100011"
        },
    }

    # Read the source code
    with open(filename) as sourceCode:
        program = (sourceCode.readlines())

    program = clean_program(program)

    for index, line in enumerate(program):
        if ":" in line:
            tag, inst = line.split(":")
            program[index] = inst
            branch_mappings.update({tag: index})

    # Split each instruction into requisite pieces
    program = split_operands(program)

    # Decode the split chunks into binary
    for i, inst in enumerate(program):
        if inst[0].startswith('B'):

            inst[-1] = branch_mappings[inst[-1]] - i - 1

            offset = pad(bin(int(inst[-1])), 12)
            rs2 = pad(bin(int(inst[1])), 5)
            rs1 = pad(bin(int(inst[2])), 5)
            funct3 = mapping[inst[0]]["funct3"]
            opcode = mapping[inst[0]]["opcode"]

            assembly.append(offset[0]+offset[2:8]+rs2+ \
                            rs1+funct3+offset[8:]+offset[1]+opcode)


        elif "LW" in inst:
            offset, rs1 = inst[2].split('(')

            offset = pad(bin(int(offset)), 12)
            rs1 = pad(bin(int(rs1.replace(')', ''))), 5)
            rd = pad(bin(int(inst[1])), 5)

            assembly.append(
                offset + rs1 + mapping["LW"]["funct3"] + rd + mapping["LW"]["opcode"])
        elif "SW" in inst:
            offset, base = inst[2].split('(')

            offset = pad(bin(int(offset)), 12)
            base = pad(bin(int(base.replace(')', ''))), 5)
            rs2 = pad(bin(int(inst[1])), 5)

            assembly.append(
                offset[0:7] + rs2 + base + mapping["SW"]["funct3"] + offset[7:] + mapping["SW"]["opcode"])
        else:
            rd = pad(bin(int(inst[1])), 5)
            rs1 = pad(bin(int(inst[2])), 5)
            rs2 = pad(bin(int(inst[3])), 5)

            assembly.append(mapping[inst[0]]["funct7"] + rs2 + rs1 +
                            mapping[inst[0]]["funct3"] + rd + mapping[inst[0]]["opcode"])

    # Write the assembled binary into an output bin file
    with open(f"../build/{outFile}", 'w') as destFile:
        for idx, inst in enumerate(assembly):
            destFile.write(inst)
            if idx < len(assembly) - 1:
                destFile.write("\n")

    return f"../build/{outFile}"


if __name__ == "__main__":
    # Check if a program was fed it, otherwise use a default
    if len(sys.argv) < 2:
        print(f"Output generated to: {assembler('../src/riscv_program.asm')}")
    else:
        print(f"Output generated to: {assembler(sys.argv[1])}")
