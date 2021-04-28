'''
MIT Licensed by Shubhayu Das, Veerendra S Devaraddi, Sai Manish Sasanapuri, copyright 2021

Developed for Processor Architecture course assignments 1 and 3 - Tomasulo Out-Of-Order Machine

This file contains the program for the GUI interface. It is completely detached from other files,
except main.py, which calls appropriate functions in the main event loop
'''

import PySimpleGUI as sg

from constants import LIMIT, NumCycles, VERSION, GUI_FONTSIZE
from constants import L1D_CACHE_LATENCY, L2D_CACHE_LATENCY, MEMORY_LATENCY
from constants import L1D_CACHE_SIZE, L2D_CACHE_SIZE, L1D_WAYS, L2D_WAYS


# Class to encapsulate the entire behaviour of the GUI interface
# The entire state of the GUI is stored in '_machine_state'
class Graphics():
    def __init__(self, machineState=None):
        self._font_size = GUI_FONTSIZE
        if machineState:
            self._machine_state = machineState
        else:
            self._machine_state = {
                "Instruction Table": {
                    "contents": [[""]*6]*5
                },
                "Reservation Station": {
                    "contents": [["ADD/SUB", "", "", "", "", "", "", ""]]*3 + [["MUL/DIV", "", "", "", "", "", "", ""]]*2
                },
                "ROB": {
                    "contents": [[""]*4]*2
                },
                "Load Store Buffer": {
                    "contents": [[""]*5]*2
                },
                "ARF": {
                    "contents": [f" R{i} " for i in range(0, LIMIT)]
                },
                "metadata": {
                    "cycle": 0,
                    "data-mem": {
                        "contents": [[hex(addr), bin(0), hex(0), 0] for addr in range(64)]
                    }
                },
                "caches": {
                    "L1": {
                        "contents": [[str(i % L1D_WAYS + 1)] + ["" for col in range(6)] for i in range(L1D_CACHE_SIZE)]
                    },
                    "L2": {
                        "contents": [[str(i % L2D_WAYS + 1)] + ["" for col in range(6)] for i in range(L2D_CACHE_SIZE)]
                    },
                    "stats": {
                        "contents": [["", ""] for _ in range(8)]
                    }
                }
            }

    # Function to generate a table, given the data and other hyperparameters
    def __generate_table(self, title, data, headings, n_rows=5, key="table"):
        row_contents = data["contents"]
        hide_vertical_scroll = True

        if len(row_contents) > n_rows:
            hide_vertical_scroll = False

        table = sg.Table(
            values=row_contents,
            headings=headings,
            hide_vertical_scroll=hide_vertical_scroll,
            def_col_width=self._font_size//2,
            row_height=2*(self._font_size+1),
            justification="center",
            num_rows=n_rows,
            alternating_row_color="lightgrey",
            text_color="black",
            key=key
        )

        return [sg.Frame(
            title=title,
            layout=[[table]],
            title_location=sg.TITLE_LOCATION_TOP,
        )]

    # Function to generate the overall layout, with some dummy initial content
    def generate_layout(self):
        width, height = sg.Window.get_screen_size()
        aspect_ratio = width/height

        if aspect_ratio < 16/9:
            self._font_size = 14

        # Code for tab 1 starts
        # This tab contains all the components of the actual Tomasulo hardware

        mainHeading = [sg.Text(
            "Tomasulo out-of-order simulation",
            justification="center",
            pad=((20, 20), (2, 2)),
            font=f"Times {int(self._font_size*1.5)}",
            text_color="black"
        )]

        cpuClockCycle = [sg.Frame(
            title="CPU Clock Cycle",
            layout=[[sg.Text(
                    text=self._machine_state["metadata"]["cycle"],
                    key="cycle_number",
                    size=(8, 1),
                    text_color="black",
                    font=f"Times {self._font_size+2}",
                    )]],
            title_location=sg.TITLE_LOCATION_TOP,
            element_justification="center",
        )]

        # Extract the content of each of the tables, from the machine's state
        instructions = self._machine_state["Instruction Table"]
        buffer = self._machine_state["Load Store Buffer"]
        reserv = self._machine_state["Reservation Station"]
        ROB = self._machine_state["ROB"]
        ARF = self._machine_state["ARF"]
        nCycles = {
            "contents": [[inst, cycles] for inst, cycles in NumCycles.items()],
        }
        L1_cache = self._machine_state["caches"]["L1"]
        L2_cache = self._machine_state["caches"]["L2"]
        cache_stats = self._machine_state["caches"]["stats"]

        # Declare all the headings for each of the tables
        bufferHeading = [" Instruction ", "Busy",
                         "Dest Tag", "Address offset", "src reg"]
        instructionsHeading = ["Instruction", "Issue",
                               "EX start", "EX end", "write to CDB", "Commit"]
        reservationHeading = ["Type", "Instruction", "Busy", "Dest tag",
                              "src tag1", "src tag2", "val 1", "val 2"]
        robHeading = [" Name ", "  Instruction  ", " Dest. ", "  Value  "]
        arfHeading = ["Reg", "   Value   ", "Mapping", "Busy"]
        cycleHeading = ["Instr.", "No. of cycles"]
        dataMemoryHeading = [
            "Address",
            "          Data(bin)          ",
            "Data(hex)", "Data(decimal)"
        ]
        l1CacheHeading = ["Way", "Mem addr", "  Tag ",
                          " Value ", "Dirty", " Valid ", " Busy "]
        l2CacheHeading = ["Way", "Mem addr", "  Tag ",
                          " Value ", "Dirty", " Valid ", " Busy "]
        cacheStatsHeading = ["   Property   ", "Count"]

        # Generate the menu
        menu = [
            sg.Menu(
                menu_definition=[
                    ['&Load', ['&Load new program', '&Load new data memory']],
                    ['&Help', ['&Instructions', '&About']]
                ],
                key="menu"
            )
        ]

        # Generate each of the tables
        instructionTable = self.__generate_table(
            "Instruction Queue",
            instructions,
            instructionsHeading,
            n_rows=7,
            key="inst_table"
        )

        instructionTableCacheTab = self.__generate_table(
            "Instruction Queue",
            instructions,
            instructionsHeading,
            n_rows=7,
            key="inst_table_cache_tab"
        )

        loadStoreBufferTable = self.__generate_table(
            "Load Store Buffer",
            buffer,
            bufferHeading,
            n_rows=3,
            key="ls_buffer_table"
        )
        reservationStationTable = self.__generate_table(
            "Reservation Station",
            reserv,
            reservationHeading,
            key="reserve_station"
        )
        ROBTable = self.__generate_table("ROB",
                                         ROB,
                                         robHeading,
                                         n_rows=8,
                                         key="rob"
                                         )
        ARFTable = self.__generate_table("ARF",
                                         ARF,
                                         arfHeading,
                                         n_rows=LIMIT,
                                         key="arf"
                                         )
        CycleInfoTable = self.__generate_table(
            "No. of Cycles",
            nCycles,
            cycleHeading,
            n_rows=len(NumCycles),
            key="num_cycles"
        )
        L1_cache_table = self.__generate_table("L1 cache",
                                               L1_cache,
                                               l1CacheHeading,
                                               n_rows=min(LIMIT,
                                                          L1D_CACHE_SIZE + 1),
                                               key="l1_cache_table"
                                               )
        L2_cache_table = self.__generate_table("L2 cache",
                                               L2_cache,
                                               l2CacheHeading,
                                               n_rows=min(LIMIT,
                                                          L2D_CACHE_SIZE + 1),
                                               key="l2_cache_table"
                                               )
        cache_stats_table = self.__generate_table("Cache stats",
                                                  cache_stats,
                                                  cacheStatsHeading,
                                                  n_rows=8,
                                                  key="cache_stats_table"
                                                  )

        # Define all the control buttons
        pauseButton = [sg.Button(
            button_text="  Start  ",
            key="pause_button"
        )]

        nextButton = [sg.Button(
            button_text="Next",
            key="next_button"
        )]

        prevButton = [sg.Button(
            button_text="Prev",
            key="previous_button"
        )]

        nextEventButton = [sg.Button(
            button_text="Next Event",
            key="next_event_button"
        )]

        # Combine all the buttons in to a single logical control panel
        controlPanel = [sg.Frame(
            title="Control Panel",
            layout=[pauseButton, nextButton + prevButton, nextEventButton],
            title_location=sg.TITLE_LOCATION_TOP,
            element_justification="center",
            pad=(2*self._font_size, 2*self._font_size)
        )]

        # Arrange the components into 3 different blocks, depending on screen resolution
        allowScroll = False
        col1 = [sg.Column(
            [cpuClockCycle, CycleInfoTable, controlPanel],
            element_justification="center",
            key="layout_col1"
        )]

        if aspect_ratio >= 16/9:
            col2 = [sg.Column(
                [instructionTable, loadStoreBufferTable, reservationStationTable],
                element_justification="center",
                expand_x=True,
                key="layout_col2"
            )]

            col3 = [sg.Column(
                [ARFTable, ROBTable],
                element_justification="center",
                expand_x=True,
                key="layout_col3"
            )]
        else:
            allowScroll = True
            col2 = [sg.Column(
                [instructionTable, loadStoreBufferTable,
                    reservationStationTable, ARFTable + ROBTable],
                element_justification="center",
                expand_x=True,
                key="layout_col2"
            )]
            col3 = []

        tab_1_layout = [sg.Tab(
            title="Tomasulo components",
            layout=[[sg.Column(
                layout=[
                    col2 + col3
                ],
                element_justification="center",
                scrollable=allowScroll,
                vertical_scroll_only=allowScroll,
                size=sg.Window.get_screen_size(),
                key="main_scroll_col_1"
            )]],
            key="tab_1_layout"
        )]
        # Tab 1 code ends

        # Tab 2 code starts
        # This tab contains all the cache related code

        tab_2_layout = [sg.Tab(
            title="Cache",
            layout=[[sg.Column(
                layout=[
                    instructionTableCacheTab,
                    [sg.Column(layout=[L1_cache_table, L2_cache_table])
                     ] + cache_stats_table
                ],
                element_justification="center",
                scrollable=allowScroll,
                vertical_scroll_only=allowScroll,
                size=sg.Window.get_screen_size(),
                key="main_scroll_col_2"
            )]],
            key="tab_2_layout"
        )]
        # Tab 2 code ends

        # Tab 3 code starts
        # This tab shows the data memory, for completeness
        dataMemoryTable = self.__generate_table(
            "Data Memory",
            self._machine_state["metadata"]["data-mem"],
            dataMemoryHeading,
            n_rows=20,
            key="data_mem_table",
        )

        tab_3_layout = [sg.Tab(
            title="Data memory",
            layout=[[sg.Column(
                layout=[
                    dataMemoryTable
                ],
                element_justification="center",
                scrollable=allowScroll,
                vertical_scroll_only=allowScroll,
                size=sg.Window.get_screen_size(),
                key="main_scroll_col_3"
            )]],
            key="tab_3_layout"
        )]
        # Tab 3 code ends

        # Generate the final layout, by combining the individual columns
        displayLayout = [
            menu,
            mainHeading,
            [sg.HorizontalSeparator(color="black", key="sep_2")],
            col1 + [sg.TabGroup(
                layout=[
                    tab_1_layout + tab_2_layout + tab_3_layout
                ],
                key="tabs"
            )]
        ]

        return displayLayout

    # Function to generate the GUI window
    def generate_window(self):
        sg.theme('Material2')

        return sg.Window(
            'Tomasulo OOO processor sim',
            self.generate_layout(),
            font=f"Times {self._font_size}",
            size=sg.Window.get_screen_size(),
            element_padding=(self._font_size//2, self._font_size//2),
            margins=(self._font_size, self._font_size),
            text_justification="center",
            resizable=True,
            element_justification="center",
        ).finalize()

    # Function to convert the InstructionTable data into the _machine_state
    def __convertInstructionTable(self, instructionTable):
        insts = []
        for entry in instructionTable._entries:
            data = []

            data.append(entry._instruction.str_disassemble())
            data.append(str(entry._rs_issue_cycle))
            data.append(str(entry._exec_start))
            data.append(str(entry._exec_complete))
            data.append(str(entry._cdb_write))
            data.append(str(entry._commit))

            insts.append(data)

        self._machine_state["Instruction Table"]["contents"] = insts

    # Function to convert the ARF data into the _machine_state
    def __convert_ARF(self, ARFTable):
        insts = []

        for register in list(ARFTable.get_entries().values())[:LIMIT]:
            data = []

            data.append(register.get_name())
            data.append(register.get_value())
            data.append(register.get_link() if register.get_link() else "-")
            data.append(str(register.is_busy())[0])

            insts.append(data)

        self._machine_state["ARF"]["contents"] = insts

    # Function to convert the ROBTable data into the _machine_state
    def __convert_ROB(self, rob):
        insts = []
        for name, entry in rob.get_entries().items():
            data = []
            if entry is None:
                data = [name] + [""] * 3
            else:
                data.append(name)
                data.append(entry.get_inst().str_disassemble())
                if entry.get_destination():
                    data.append(entry.get_destination().get_name())
                else:
                    data.append("NA")
                data.append(entry.get_value())

            insts.append(data)

        self._machine_state["ROB"]["contents"] = insts

    # Function to convert the RS data into the _machine_state
    def __convertReservationStation(self, RS_buffers):
        insts = []
        for name, resStat in RS_buffers.items():
            for entry in resStat._buffer:
                data = []
                if entry:
                    data.append(name)
                    data.append(entry._instruction.str_disassemble())

                    data.append(str(entry._busy)[0])
                    data.append(entry._dest)

                    data.append(entry._src_tag1)
                    data.append(entry._src_tag2)

                    data.append(str(entry._src_val1))
                    data.append(str(entry._src_val2))
                else:
                    data = [name] + [""] * 7
                    data[2] = "F"

                insts.append(data)

        self._machine_state["Reservation Station"]["contents"] = insts

    # Function to convert the LSQ data into the _machine_state
    def __convert_LS_buffer(self, LW_SW):
        insts = []
        for entry in LW_SW.get_entries():
            data = []
            if entry:
                data.append(entry.get_inst().str_disassemble())

                data.append(str(entry.is_busy())[0])
                if isinstance(entry._dest, str):
                    data.append(entry._dest)
                else:
                    data.append(entry._dest.get_name())

                if entry._base_val == "-":
                    data.append(f"{entry._offset}+{entry._base.get_name()}")
                else:
                    data.append(f"{entry._offset}+{entry._base_val}")
                data.append(entry._base.get_name())

            else:
                data = [""] * 5

            insts.append(data)

        self._machine_state["Load Store Buffer"]["contents"] = insts

    # Function to update the state of the memory, using the memory controller
    def __convertMemCtl(self, controller):
        mem = []
        caches = [[], []]
        row_sizes = [L1D_CACHE_SIZE//L1D_WAYS, L2D_CACHE_SIZE//L2D_WAYS]

        # Update the memory
        for addr, mem_row in enumerate(controller.get_memory()):
            data = []
            data.append(hex(addr))
            data.append(mem_row)
            data.append(hex(int(mem_row, 2)))
            data.append(int(mem_row, 2))

            mem.append(data)

        # Update the caches
        for i, cache in enumerate([controller.get_l1_cache(), controller.get_l2_cache()]):
            for index, row in enumerate(cache):
                for way, entry in row.items():
                    data = []
                    way = way.split(" ")[-1]
                    addr = "-"
                    data.append(way)
                    if entry.get_tag() < 0:
                        data.append(addr)
                        data.append("-")
                        data.append("-")
                    else:
                        addr = entry.get_tag() * row_sizes[i] + index
                        data.append(addr)
                        data.append(entry.get_tag())
                        temp = entry.get_cache_value()
                        if isinstance(temp, list):
                            data.append(temp[-1])
                        else:
                            data.append(temp)
                    data.append(str(entry.get_dirty_bit())[0])
                    data.append(str(entry.get_valid_bit())[0])
                    data.append(str(entry.get_busy_bit())[0])

                    caches[i].append(data)

        # Update the cache stats
        stats = [
            ["L1 read hits", controller.get_L1D_read_hits()],
            ["L1 read misses", controller.get_L1D_read_miss()],
            ["L1 write hits", controller.get_L1D_write_hits()],
            ["L1 write misses", controller.get_L1D_write_miss()],
            ["L2 read hits", controller.get_L2D_read_hits()],
            ["L2 read misses", controller.get_L2D_read_miss()],
            ["Prefetch hits", controller.get_prefetch_hits()],
            ["Prefetcher accuracy", controller.get_prefetch_accuracy()]
        ]

        self._machine_state["metadata"]["data-mem"]["contents"] = mem
        self._machine_state["caches"]["L1"]["contents"] = caches[0]
        self._machine_state["caches"]["L2"]["contents"] = caches[1]
        self._machine_state["caches"]["stats"]["contents"] = stats

    # Function to call the individual update blocks. This function is called from the main event loop

    def update_contents(self, window, cycle, instructionTable=None, ROB=None, RS_buffers=None, ARF=None, LS_Buffer=None, MemCtl=None):
        self._machine_state["metadata"]["cycle"] = cycle
        window["cycle_number"].update(
            value=self._machine_state["metadata"]["cycle"])

        if instructionTable:
            self.__convertInstructionTable(instructionTable)
            window['inst_table'].update(
                self._machine_state["Instruction Table"]["contents"])
            window['inst_table_cache_tab'].update(
                self._machine_state["Instruction Table"]["contents"])

        if ROB:
            self.__convert_ROB(ROB)
            window['rob'].update(self._machine_state["ROB"]["contents"])

        if RS_buffers:
            self.__convertReservationStation(RS_buffers)
            window['reserve_station'].update(
                self._machine_state["Reservation Station"]["contents"])

        if ARF:
            self.__convert_ARF(ARF)
            window['arf'].update(self._machine_state["ARF"]["contents"])

        if LS_Buffer:
            self.__convert_LS_buffer(LS_Buffer)
            window['ls_buffer_table'].update(
                self._machine_state["Load Store Buffer"]["contents"])

        if MemCtl:
            self.__convertMemCtl(MemCtl)
            window['data_mem_table'].update(
                self._machine_state["metadata"]["data-mem"]["contents"])

            window['l1_cache_table'].update(
                self._machine_state["caches"]["L1"]["contents"])

            window['l2_cache_table'].update(
                self._machine_state["caches"]["L2"]["contents"])

            window['cache_stats_table'].update(
                self._machine_state["caches"]["stats"]["contents"])

    # Function to reset the machine state in GUI
    # Used after loading in a new program
    def reset_state(self):
        self._machine_state = {
            "Instruction Table": {
                "contents": [[""]*6]*5
            },
            "Reservation Station": {
                "contents": [["ADD/SUB", "", "", "", "", "", "", ""]]*3 + [["MUL/DIV", "", "", "", "", "", "", ""]]*2
            },
            "ROB": {
                "contents": [[""]*4]*2
            },
            "Load Store Buffer": {
                "contents": [[""]*5]*2
            },
            "ARF": {
                "contents": [f" R{i} " for i in range(0, LIMIT)]
            },
            "metadata": {
                "cycle": 0,
                "data-mem": {
                    "contents": [[hex(addr), bin(0), hex(0), 0] for addr in range(64)]
                }
            },
            "caches": {
                "L1": {
                    "contents": [[str(i % L1D_WAYS + 1)] + ["" for col in range(6)] for i in range(L1D_CACHE_SIZE)]
                },
                "L2": {
                    "contents": [[str(i % L2D_WAYS + 1)] + ["" for col in range(6)] for i in range(L2D_CACHE_SIZE)]
                },
                "stats": {
                    "contents": [["", ""] for _ in range(8)]
                }
            }
        }

    # Function to call up the About popup:
    def generateAboutPopup(self):
        contents = f'''
        Developer: Shubhayu Das, Veerendra S Devaraddi, Sai Manish Sasanapuri
        Program: Tomasulo Machine simulator
        Version: {VERSION}
        Date: 3rd April, 2021
        Project repo: https://github.com/Shubhayu-Das/tomasulo-O3-with-prefetch
        '''
        sg.popup_ok(
            contents,
            title="About",
            non_blocking=True,
            grab_anywhere=True,
            font=f"Times {self._font_size}"
        )

    # Function to call up the Instructions of Use popup
    def generateInstructionPopup(self):
        content = f'''
        1. This program is a cycle-by-cycle simulation of the Tomasulo Out Of Order Machine, used in the IBM 360/91

        2. Each of the main components is assigned its own display table. If the tables are too long, they will have scrollbars

        3. The GUI scales and adjusts according to your screen resolution, Best results are obtained at 1920x1080 and 1440x900.

        4. The GUI is interactive, the behaviour can be controlled using the buttons in the Control Panel on the left

        5. To single step through the clock cycles of the simulation, use the previous and next buttons. It is recommended that you\
        pause the simulation before this.

        6. To start the simulation, click on the "Start" button. The button will change to a pause button after this.

        7. To pause the simulation, click on the "Pause" button; after this the button will change to a continue button. Clicking it\
        will continue executing the simulation.

        8. Some executions can take a while, with nothing noticeable happening. To skip to the next cycle, where one of the components\
        have a change, click on the "Next Event" button. This button can be used irrespective of whether the simulation is running\
        or is paused.

        9. There are some known bugs in the GUI. Refer to the README for more details
        '''

        sg.popup_scrolled(
            content,
            title="Instructions of use",
            non_blocking=True,
            grab_anywhere=True,
            background_color='white',
            text_color="black",
            font=f"Times {self._font_size}",
            size=(100, 10)
        )

    # Function to load in a new file
    def generateFileLoader(self, text):
        return sg.popup_get_file(text)


# Local testing code
if __name__ == "__main__":

    GUI = Graphics()

    window = GUI.generate_window()

    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED:
            break
    window.close()
