(to see the initial working history, see [here](https://github.com/Shubhayu-Das/VL803-projects))

# Tomasulo OOO Processor
-------------------------

This is my attempt to make an interactive simulation of the Tomasulo out of order processor, as part of the VL803 course's first assignment.
This documentation is still in the works, I am actively trying to improve things in this program and documentation. Feel
free to raise Issues for feature requests and bugs.

-------------------
### Student
Name: Shubhayu Das

Roll number: IMT2018523

Version: 1.1.0

-----------------------------

### Progress
Completed the base model of the Tomasulo machine, as implemented in the IBM 360/91. The difference is that the Tomasulo machine was originally meant for floating point units only, but I am using it for integers too. The other rub is that I am actually using *integer* instructions from RISC-V ISA, for this sim.

-----------------------------

### Future improvements
1. Additional GUI features
2. Document the code base and improve this README

------------------------------

### Software libraries

The GUI needs the ```tkinter``` and ```pysimplegui```. These can be installed using the following commands:

On Linux/Ubuntu:
```bash
$ sudo apt install python3-tk
$ pip install pysimplegui
```

On Windows:
```
$ pip install pysimplegui
```

I have tested the code on Python 3.8.7 on both the OS (Windows 1903 build and Ubuntu 20.04.01 LTS), if there are any issues, please raise an Issue on Github. The GUI might appear different in different screens, depending on the aspect ratios. I have tried to make it useable, over looking pretty. For better control over the GUI, I would have to dive too deep(using tk or Qt5), which I can't bother to do now.

**References**:
1. [PySimpleGUI documentation website](https://pysimplegui.readthedocs.io/en/latest/)

--------------------

### Instructions for running

This simulator supports LW/SW, ADD/SUB from RISC-V RV32I, and MUL/DIV from RISC-V RV32M. 

Summary to execute program:
- To simply start the simulation, for the given question: ```python main.py```

- To load custom assembled program: ```python main.py build/<filename.elf>```

- To load in custom data memory along with assembled program: ```python main.py build/<filename.elf> <data_mem.data>```

### Detailed instructions:
- Place your ```asm``` program in the src folder.
- Open a terminal and navigate to the ```code/``` folder. Execute: ```python assembler.py src/<filename.asm>```.
- This will generate the ```elf``` file in ```build/<filename.elf>```.
- Now run: ```python main.py build/<filename.elf>``` to launch the simulation
- The simulation supports pausing, stepping back and forward - one step at a time.
- To stop the simulation, simply close the window
- The data memory is stored in ```data_memory.dat```. You can either modify the same file, or create a separate file.
  The data memory file can be chosen from the GUI itself(Load > Load from data memory). Or while executing the program:

  ```python main.py build/<filename.elf> <data_mem.data>```

- To change the duration spent on each cycle, open ```constants.py``` and adjust the ```CYCLE_DURATION``` in *milliseconds* to your desired value.

-----

### Known Bugs

1. The "Prev" button can't go below PC=2. Its a pain to figure out how to implement history in the GUI related code in ```main.py```, so I left it as is. After all, how much even happens in the first two cycles.

2. ```DEBUG=True``` doesn't print a whole lot of intelligible data. This is sorely because I didn't have the time and patience to complete it yet. Enjoy the GUI though.

3. While going to the next "event" step, if the next happens to be the last step of the entire execution, the program WILL hang. My history traversal mechanism are pretty buggy right now. If the program hangs, please go to the terminal(from where the python program was started) and press ```Ctrl+C```.
--------------

### License

I have MIT licensed this project **except for the RISC-V references**. RISC-V opcodes repo [riscv/riscv-opcodes](https://github.com/riscv/riscv-opcodes) is licensed by the University of California.
