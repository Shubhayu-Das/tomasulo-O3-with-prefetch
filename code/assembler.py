'''
MIT Licensed by Shubhayu Das, Veerendra S Devaraddi, Sai Manish Sasanapuri, copyright 2021

Developed for Processor Architecture course assignments 1 and 3 - Tomasulo Out-Of-Order Machine

This is the script for a basic RISC-V assembler. It only support LW, ADD, SUB, MUL and DIV instructions so far.
All are integer instructions only. Execution generates integers only [updated].
'''
import re
import sys
from typing import List

from helpers import pad, dec2bin

# Function to split the instruction string into opcode and registers(and offset if needed)
# This function is capable of handling comments too


def clean_program(program: List[str]) -> List[str]:
    program = [insts.split(";")[0].strip() for insts in program]
    program = map(lambda x: "ADDI x0, x0, 0" if x == "NOP" else x, program)
    program = list(filter(None, program))

    return program


def split_operands(program: List[str]) -> List[List[str]]:
    split_components: List[List[str]] = [
        re.split(r",|\s", insts) for insts in program]

    rename_regs: List[List[str]] = []
    for insts in split_components:
        rename_regs.append([re.sub(r'X(\d)', r'\1', word.upper())
                           for word in insts if word])

    split_program: List[List[str]] = [insts for insts in rename_regs if insts]

    return split_program

# The main assembler function, which contains the mapping between the instructions and their
# opcodes, function-7 and function-3 fields


def assembler(filename: str) -> str:
    insts: List[str] = []
    outFile: str = ".".join([filename.split("/")[-1].split(".")[0], "bin"])
    program: List[str] = []
    assembly: List[str] = []
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
        "ADDI": {
            "funct3": "000",
            "opcode": "0010011"
        }
    }

    # Read the source code
    with open(filename) as sourceCode:
        program = (sourceCode.readlines())

    program = clean_program(program)

    for index, line in enumerate(program):
        if ":" in line:
            tag, instruction = line.split(":")
            program[index] = instruction
            branch_mappings.update({tag: index})

    # Split each instruction into requisite pieces
    split_program: List[List[str]] = split_operands(program)

    # Decode the split chunks into binary
    for i, insts in enumerate(split_program):
        inst = mapping.get(insts[0])
        if inst is None:
            print(
                f"Instruction: {insts[0]} not supported/is not a valid RISC-V instruction. Skipping")
            continue

        funct3 = inst.get("funct3")
        opcode = inst.get("opcode")

        if insts[0].startswith('B'):

            insts[-1] = branch_mappings[insts[-1]] - i - 1

            offset = dec2bin(int(insts[-1]), 12)
            rs2 = dec2bin(int(insts[1]), 5)
            rs1 = dec2bin(int(insts[2]), 5)

            assembly.append(offset[0]+offset[2:8]+rs2 +
                            rs1+funct3+offset[8:]+offset[1]+opcode)

        elif insts[0].endswith('I'):
            imm = dec2bin(int(insts[-1]), 12)
            rd = dec2bin(int(insts[1]), 5)
            rs1 = dec2bin(int(insts[2]), 5)

            assembly.append(imm + rs1 + funct3 + rd + opcode)

        elif "LW" in insts:
            offset, rs1 = insts[2].split('(')

            offset = dec2bin(int(offset), 12)
            rs1 = dec2bin(int(rs1.replace(')', '')), 5)
            rd = dec2bin(int(insts[1]), 5)

            assembly.append(
                offset + rs1 + funct3 + rd + opcode)
        elif "SW" in insts:
            offset, base = insts[2].split('(')

            offset = dec2bin(int(offset), 12)
            base = dec2bin(int(base.replace(')', '')), 5)
            rs2 = dec2bin(int(insts[1]), 5)

            assembly.append(
                offset[0:7] + rs2 + base + funct3 + offset[7:] + opcode)
        else:
            rd = dec2bin(int(insts[1]), 5)
            rs1 = dec2bin(int(insts[2]), 5)
            rs2 = dec2bin(int(insts[3]), 5)

            assembly.append(mapping[insts[0]]["funct7"] + rs2 + rs1 +
                            funct3 + rd + opcode)

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
