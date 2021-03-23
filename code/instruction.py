# RISC-V opcodes repo license
'''
Copyright (c) 2010-2017, The Regents of the University of California
(Regents).  All Rights Reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. Neither the name of the Regents nor the
   names of its contributors may be used to endorse or promote products
   derived from this software without specific prior written permission.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING
OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS
BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE. THE SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED
HEREUNDER IS PROVIDED "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE
MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
'''

# MY program's license and info
'''
MIT Licensed by Shubhayu Das, copyright 2021

Developed for Processor Architecture course assignment 1 - Tomasulo Out-Of-Order Machine

This file contains a class data structure that represents every instruction

The following instructions are supported by this program
             31:25   24:20  19:15   14:12  11:7   6:0
instruction - funct7 - rs2 - rs1 - funct3 - rd - opcode
    ADD      0000000 - src2 - src1 - 000 - dest - 0110011
    SUB      0100000 - src2 - src1 - 000 - dest - 0110011
    LW        offset[31:20] - src1 - 010 - dest - 1010011

    MUL      0000001 - src2 - src1 - 000 - dest - 0110011
    DIV      0000001 - src2 - src1 - 100 - dest - 0110011

ADD/SUB/MUL/DIV rd, rs1, rs2

References: 
1.  ADD/SUB/LW/SW come from 
    RV32I: https://github.com/riscv/riscv-opcodes/blob/master/opcodes-rv32i

2.  MUL/DIV come from 
    RV32M: https://github.com/riscv/riscv-opcodes/blob/master/opcodes-rv32m

Note: RISC-V and its repos have their own license and are NOT are a part of the MIT license that my program files
are licensed under.
'''

from register_bank import Register


# Instruction data structure that stores all the necessary information that an instruction carries
class Instruction:
    def __init__(self, PC=-1, funct7="0000000", rs2="00000", rs1="00000",
                 rd="00000", funct3="000", opcode="0000000", hasOffset=False):
        
        if PC > 0:
            self.PC = PC

        self.rs2 = None
        self.offset = None
        self.funct7 = None

        # To differentiate between instructions with offset(LW) and other instructions(ADD, SUB etc)
        if hasOffset:
            self.offset = funct7 + rs2
        else:
            self.funct7 = funct7
            self.rs2 = rs2

        self.hasOffset = hasOffset
        self.rs1 = rs1
        self.rd = rd
        self.funct3 = funct3
        self.opcode = opcode

    # Function to convert binary to English for decision making and displaying
    # Returns a struct which contains all the individual segments of the instruction, depending on their type
    def disassemble(self):
        command = ""

        if self.hasOffset:
            offset = int(self.offset, 2)
            if self.opcode == "1010011" and self.funct3 == "010":
                command = "LW"
            else:
                return -1

            return {
                "command": command,
                "rd": self.rd,
                "rs1": self.rs1,
                "offset": offset
            }
            
        else:
            if self.opcode == "0110011":
                if self.funct3 == "000":
                    if self.funct7 == "0000000":
                        command = "ADD"
                    elif self.funct7 == "0100000":
                        command = "SUB"
                    elif self.funct7 == "0000001":
                        command = "MUL"
                    else:
                        return -1
                elif self.funct3 == "100":
                    if self.funct7 == "0000001":
                        command = "DIV"
                    else:
                        return -1

            return {
                "command": command,
                "rd": self.rd,
                "rs1": self.rs1,
                "rs2": self.rs2
            }

    # Function to convert the binary to a English string for displaying purposes only
    def str_disassemble(self):
        instruction = self.disassemble()
        rd = instruction["rd"]
    
        rs1 = instruction["rs1"]

        if "offset" in instruction.keys():
            return f"{instruction['command']} {rd}, {instruction['offset']}({rs1})"
        else:
            return f"{instruction['command']} {rd}, {rs1}, {instruction['rs2']}"

    # Globally accessible class method to create an Instruction from a binary input
    # This function is capable of removing spaces, which can be added to improve readability
    @classmethod
    def segment(self, instruction, PC=-1):
        instruction = instruction.replace(" ", "")
        if len(instruction) != 32:
            return -1

        funct7 = instruction[0:7]
        rs2 = f"R{int(instruction[7:12], 2)}"
        rs1 = f"R{int(instruction[12:17], 2)}"
        funct3 = instruction[17:20]
        rd = f"R{int(instruction[20:25], 2)}"
        opcode = instruction[25:32]
        hasOffset = False

        # If we encounter a load word
        if funct3 == "010" and opcode == "1010011":
            hasOffset = True
            rs2 = instruction[7:12]

        return Instruction(
            PC=PC,
            funct7=funct7,
            rs2=rs2,
            rs1=rs1,
            rd=rd,
            funct3=funct3,
            opcode=opcode,
            hasOffset=hasOffset
        )

    def __str__(self):
        if self.hasOffset:
            return f"<[PC={self.PC}] offset:{self.offset} rs1:{self.rs1} funct3:{self.funct3} rd:{self.rd} opcode:{self.opcode}>"
        else:
            return f"<[PC={self.PC}] funct7:{self.funct7} rs2:{self.rs2} rs1:{self.rs1} funct3:{self.funct3} rd:{self.rd} opcode:{self.opcode}>"
