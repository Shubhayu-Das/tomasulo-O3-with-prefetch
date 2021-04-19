'''
MIT Licensed by Shubhayu Das, copyright 2021

Developed for Processor Architecture course assignment 1 - Tomasulo Out-Of-Order Machine

This file contains the main logic, that combines individual blocks into a cohesive whole
'''

import os
import sys
import copy
import PySimpleGUI as sg

# Import all the functional components
from register_bank import RegisterBank as ARF
from memory_controller import MemoryController

from instruction import Instruction
from reservation_station import ReservationStation, ReservationStationEntry
from instruction_table import InstructionTable, InstructionTableEntry
from ls_buffer import LoadStoreBuffer
from rob import ROBTable

# Import the other custom components
import constants
from gui import Graphics


class Tomasulo:
    def __init__(self, program_src, data_mem):
        # Global variables that are needed throughout here
        self._instructions = []
        self._historyBuffer = []
        self._clock_cycle = 0
        self._next_event = False
        self._n_complete = 0
        self._data_mem_src = data_mem

        # Creating objects related to the memory
        self._memory_controller = MemoryController(data_mem, True, True)

        # Creating objects of the functional components
        self._ARF = ARF(size=10, init=[12, 16, 4, 5, 3, 4, 1, 2, 2, 3])

        self._ADD_RS = ReservationStation(constants.ADD_SUB, size=3)
        self._MUL_RS = ReservationStation(constants.MUL_DIV, size=2)

        self._LSQ = LoadStoreBuffer(size=3, memoryFile=data_mem)
        self._ROB = ROBTable(size=8)

        # Load in the program and create the instruction table accordingly
        # The instruction table is NOT a functional component of the Tomasulo machine
        with open(program_src) as binary:
            program = binary.readlines()
            program = [inst.strip() for inst in program]

            for local_PC, inst in enumerate(program):
                self._instructions.append(
                    Instruction.segment(inst, PC=local_PC+1))

        self._instructionTable = InstructionTable(
            size=min(10, len(self._instructions)))

        for instruction in self._instructions:
            self._instructionTable.add_entry(instruction)

    # ------------------------------------------------------------------------------- #
    # Functions to implement each stage of the pipeline
    # ------------------------------------------------------------------------------- #

    # Function to try and dispatch next instruction if corresponding RS is free
    # Updates all relevant source mappings too
    def tryDispatch(self, robEntry):
        for it_entry in self._instructionTable.get_entries():
            if it_entry.get_state() == constants.RunState.NOT_STARTED:
                instruction = it_entry.get_inst()
                instruction_type = instruction.disassemble()["command"]

                RS = None

                if instruction_type in ["ADD", "SUB"]:
                    RS = self._ADD_RS
                elif instruction_type in ["MUL", "DIV"]:
                    RS = self._MUL_RS
                elif instruction_type in ["LW", "SW"]:
                    RS = self._LSQ

                if RS:
                    if not RS.is_busy():
                        if RS.add_entry(instruction, self._ARF):
                            # Store word instructions have no destination register
                            # We still need to make a ROB entry for in-order commit
                            if instruction_type in ["SW"]:
                                self._ROB.add_entry(instruction, None)
                            else:
                                destination = self._ARF.get_register(
                                    instruction.rd)

                                destination.set_link(self._ROB.add_entry(
                                    instruction, destination))

                        if RS in [self._ADD_RS, self._MUL_RS, self._LSQ]:
                            RS.update_rs_entries(robEntry)

                        it_entry.rs_issue(self._clock_cycle)
                        self._next_event = True

                        break

    # Function to simulate the execution of the process. This includes dispatching
    # self._instructions and handling their execution steps
    def tryExecute(self):
        for RS in [self._LSQ, self._ADD_RS, self._MUL_RS]:
            for rs_entry in RS.get_entries():
                if rs_entry:
                    it_entry = self._instructionTable.get_entry(
                        rs_entry._instruction)

                    if it_entry.get_state() == constants.RunState.RS and rs_entry.is_executeable():
                        data = rs_entry.get_result(self._memory_controller)
                        if data:
                            it_entry.ex_start(self._clock_cycle)

                            # Separate handling of memory accesses, where the number of clock
                            # cycles needed might vary
                            if isinstance(data, list) and len(data) > 0:
                                data, n_cycles_needed = data
                                it_entry.set_max_tick(n_cycles_needed)

                            it_entry.update_result(data)
                            RS.remove_entry(rs_entry.get_inst())

                            self._next_event = True
                            break

        for it_entry in self._instructionTable.get_entries():
            if it_entry.get_state() == constants.RunState.EX_START:
                it_entry.ex_tick(self._clock_cycle)

    # Function to perform the CDB broadcast, when an instruction has completed executing
    def tryCDBBroadcast(self):
        for it_entry in self._instructionTable.get_entries():
            if it_entry.get_state() == constants.RunState.EX_END:

                if it_entry.get_inst().disassemble()["command"] == "SW":
                    # if self._memory_controller.mem_write(it_entry.get_result()):
                    it_entry.cdb_write("-")
                else:
                    it_entry.cdb_write(self._clock_cycle)

                    value = it_entry.get_result()
                    robEntry = self._ROB.update_value(
                        it_entry.get_inst(), value)

                    if robEntry:
                        for RS in [self._ADD_RS, self._MUL_RS, self._LSQ]:
                            RS.update_rs_entries(robEntry)

                    self._next_event = True
                    return robEntry

    # Function to commit the result of an instruction, if it has completed CDB broadcast
    # and is at the tail of the self._ROB
    def tryCommit(self):
        for it_entry in self._instructionTable.get_entries():
            if it_entry.get_state() == constants.RunState.MEM_WRITE:
                if it_entry.mem_tick():
                    it_entry.mem_commit(self._clock_cycle)

                    addr, data = it_entry.get_result()
                    self._memory_controller.mem_write(addr, data)
                    self._memory_controller.clear_busy_bit(addr)

            elif it_entry.get_state() == constants.RunState.COMMIT:
                continue

            elif it_entry.get_state() == constants.RunState.CDB:
                robEntry = self._ROB.remove_entry()
                if robEntry:
                    it_entry.commit(self._clock_cycle)

                    if it_entry.get_inst().disassemble()["command"] not in ["SW"]:
                        self._ARF.update_register(robEntry)
                    else:
                        it_entry.mem_access()

                        addr, data = it_entry.get_result()
                        it_entry.update_result([addr, data])

                        latency = self._memory_controller.get_latency(addr)
                        self._memory_controller.set_busy_bit(addr)

                        it_entry.set_max_tick(latency-1)

                self._next_event = True
                self._n_complete += 1
            break

    # Function to call all the above function, while updating the program counter
    def logic_loop(self):
        if self._n_complete == len(self._instructions):
            return

        self._clock_cycle += 1

        if constants.DEBUG:
            print(self._clock_cycle)

        # Execute each of the steps in reverse-pipeline order
        # The reverse order is to make sure that the previous instruction completes its stages
        self.tryCommit()
        robEntry = self.tryCDBBroadcast()
        self.tryExecute()

        # This is needed because I am dispatching after broadcasting.
        # This is a race condition effectively
        self.tryDispatch(robEntry)

        # Update the changes into the history buffer
        self._historyBuffer.append([
            copy.deepcopy(self._instructionTable),
            copy.deepcopy(self._ROB),
            {
                constants.ADD_SUB: copy.deepcopy(self._ADD_RS),
                constants.MUL_DIV: copy.deepcopy(self._MUL_RS)
            },
            copy.deepcopy(self._ARF),
            copy.deepcopy(self._LSQ),
            copy.deepcopy(self._memory_controller),
            copy.deepcopy(self._next_event)
        ])

    # Reset the flag variable that indicates a change in machine state
    def reset_next_event(self):
        self._next_event = False

    # Return the flag that indicates that the machine state has changed
    def next_event_occured(self):
        return self._next_event

    # Get the cycle-by-cycle execution history of the machine
    def get_history(self):
        return self._historyBuffer

    # Get the CPU clock cycle
    def get_cpu_clock(self):
        return self._clock_cycle

    # Get the instruction table object
    def get_instruction_table(self):
        return self._instructionTable

    # Get the ROB object
    def get_rob(self):
        return self._ROB

    # Get all the RS objects
    def get_all_rs(self):
        return {
            constants.ADD_SUB: self._ADD_RS,
            constants.MUL_DIV: self._MUL_RS
        }

    # Get the ARF object
    def get_arf(self):
        return self._ARF

    # Get the load/store buffer object
    def get_lsq(self):
        return self._LSQ

    # Get the memory controller object
    def get_mem_ctl(self):
        return self._memory_controller


if __name__ == "__main__":
    # Load in the program, if no program file is provided
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        program_src = "../build/riscv_program.bin"
    else:
        program_src = sys.argv[1]

    # Choose a data sourse
    if len(sys.argv) < 3 or not os.path.exists(sys.argv[2]):
        data_mem_src = "memory/data_memory.dat"
    else:
        data_mem_src = sys.argv[2]

    # Create the Tomasulo machine object
    machine = Tomasulo(program_src, data_mem_src)

# ------------------------------------------------------------------------------- #
# GUI related things, with event loop, which updates the processor in every clock self._clock_cycle
# ------------------------------------------------------------------------------- #

    RUN = False
    backwards = 0
    frameDuration = constants.CYCLE_DURATION

    GUI = Graphics()
    window = GUI.generateWindow()

    # Main event loop
    while True:
        event, values = window.read(timeout=frameDuration)
        done = False

        if event == sg.WIN_CLOSED or machine.get_cpu_clock() > 1000:
            break

        elif event == "About":
            RUN = False
            window["pause_button"].update(text="Continue")

            GUI.generateAboutPopup()

        elif event == "Instructions":
            RUN = False
            window["pause_button"].update(text="Continue")

            GUI.generateInstructionPopup()

        elif event == "pause_button":
            if RUN:
                window["pause_button"].update(text="Continue")
            else:
                window["pause_button"].update(text="  Pause  ")

            RUN = not RUN

        elif event in ["previous_button", "next_button"] and not RUN:

            if backwards < machine.get_cpu_clock() and event == "previous_button":
                backwards += 1
            if backwards < machine.get_cpu_clock() and event == "next_button":
                backwards -= 1

            index = machine.get_cpu_clock() - backwards
            history = machine.get_history()

            if index < len(history) and index != 0:
                GUI.updateContents(
                    window,
                    index + 1,
                    history[index][0],
                    history[index][1],
                    resStats=history[index][2],
                    ARF=history[index][3],
                    LS_Buffer=history[index][4],
                    MemCtl=history[index][5]
                )

                done = True

        elif event == "next_event_button":
            if RUN:
                while not machine.next_event_occured():
                    machine.logic_loop()
                machine.reset_next_event()

        elif event in ["Load new program", "Load new data memory"] and not RUN:
            if event == "Load new program":
                filename = GUI.generateFileLoader(
                    "Enter program file(.bin format only)")
            else:
                filename = GUI.generateFileLoader(
                    "Enter program file(.dat format only)")

            if filename:
                if event == "Load new program" and filename.split('.')[-1] != "bin":
                    sg.popup_error("Invalid file format!")
                elif event == "Load new data memory" and filename.split('.')[-1] != "dat":
                    sg.popup_error("Invalid file format!")

                else:
                    if event == "Load new program":
                        program_src = filename
                    else:
                        data_mem_src = filename

                    machine = Tomasulo(program_src, data_mem_src)
                    backwards = 0

                    GUI.resetState()
                    GUI.updateContents(
                        window,
                        machine.get_cpu_clock(),
                        machine.get_instruction_table(),
                        machine.get_rob(),
                        machine.get_all_rs(),
                        machine.get_arf(),
                        machine.get_lsq(),
                        machine.get_mem_ctl()
                    )

                    window.read(timeout=1)
                    window["pause_button"].update(text="Start")

        if RUN or (not RUN and not done and event in ["next_button", "next_event_button"]):
            # Reset the history/step controls
            if backwards > 1:
                index = machine.get_cpu_clock() - backwards
                history = machine.get_history()

                if event == "next_event_button":
                    while not history[index][5]:
                        backwards -= 1
                        index = machine.get_cpu_clock() - backwards

                GUI.updateContents(
                    window,
                    index + 1,
                    history[index][0],
                    history[index][1],
                    resStats=history[index][2],
                    ARF=history[index][3],
                    LS_Buffer=history[index][4],
                    MemCtl=history[index][5]
                )

                backwards -= 1

            else:
                if event == "next_event_button":
                    while not machine.next_event_occured():
                        machine.logic_loop()
                    machine.reset_next_event()
                else:
                    # Run the processor for one clock cycle
                    machine.logic_loop()

                # Render the contents to the GUI
                GUI.updateContents(
                    window,
                    machine.get_cpu_clock(),
                    machine.get_instruction_table(),
                    machine.get_rob(),
                    machine.get_all_rs(),
                    machine.get_arf(),
                    machine.get_lsq(),
                    machine.get_mem_ctl()
                )

    window.close()
