(to see the initial working history, see [here](https://github.com/Shubhayu-Das/VL803-projects)). *This repo is not public yet.*

# Tomasulo OOO Processor
-------------------------

This is our attempt to improve on the base Tomasulo machine, designed by Shubhayu Das, as part of the VL803 course's first assignment. In this extension to the original code, we will implement various data prefetching policies. Our course was instructed by professor [Nanditha Rao](https://in.linkedin.com/in/nanditha-rao-b5608928) at IIITB.

This documentation is still in the works, We will actively improve things in this program and documentation. 

Feel free to raise Issues for feature requests and bugs.

The original code is publicly available [here](https://gitlab.com/shubhayu-das/tomasulo-o3-processor-simulator). We will make the original repo public on Github after our course is complete.


Version: 1.2.0

-------------------
### Students
1. [Sai Manish Sasanapuri](https://github.com/Sai-Manish/)
2. [Shubhayu Das](https://github.com/Shubhayu-Das/)
3. [Veerendra S. Devaraddi](https://github.com/vsdevaraddi)

-----------------------------

### Progress
Updated GUI to accomodate cache and data memory display.

-----------------------------

### Future improvements
1. Develop cache, which can accept prefetching and replacement policies
2. Develop base next-line prefetchet
3. Develop base LRU replacement policy
4. Integrate everything with existing codebase and GUI
5. Add additional prefetchers and replacement policies
6. Additional GUI features
7. Document the code base and improve this README

------------------------------

### Software libraries

**GUI**

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

**Linting**

This project enforces uniform code style using the pep8 standards. For this, the ```pycodestyle``` and ```autopep8``` libraries are used. The ```E501``` styling(too long lines) is ignored, because there are just too many of them and they are hard to fix properly. The libraries can be installed as extensions in VS code. However, I prefer using them from the terminal. To install them, run(in any OS):

```bash
$ pip install pycodestyle autopep8
```

After this, detect all the errors using:
```pycodestyle code/ --statistics```. You might want to pipe the output through pipe, to see the statistics at the end only. Optionally, you can use ```grep``` to find which files have the error.

To fix(most of) the errors, use ```autopep8``` as follows:

```autopep8 code/ --recursive --in-place -j 8 --pep8-passes 1000```


To fix a single error, use:

```autopep8 code/ --recursive --in-place -j 8 --pep8-passes 1000 --select=<error code>```.

Note that for both the above steps, you need to be in the directory which contains this README file.


**References**:
1. [PySimpleGUI documentation website](https://pysimplegui.readthedocs.io/en/latest/)
2. [autopep8 documentation](https://pypi.org/project/autopep8/#usage)
3. [pep8 documentation](https://www.python.org/dev/peps/pep-0008/)

--------------------

### Instructions for running

This simulator supports LW/SW, ADD/SUB from RISC-V RV32I, and MUL/DIV from RISC-V RV32M. 

Summary to execute program:
- To simply start the simulation, for the given question: ```python main.py```

- To load custom assembled program: ```python main.py build/<filename.bin>```

- To load in custom data memory along with assembled program: ```python main.py build/<filename.bin> <data_mem.data>```

### GUI doesn't open up

The GUI library might throw an error saying that the DISPLAY environment variable is not available. To fix this, set ```DISPLAY=":0"```. In Ubuntu(Linux in general), one way to do this is:
```bash
$ echo 'export DISPLAY=":0"' >> ~/.profile
$ source ~/.profile
# Just to confirm that the env is really set
$ echo $DISPLAY
```

Try running the program after this, it should not cause any problems. You can remove that line from ```.profile``` later on, if needed. That line of code selects the monitor on which the GUI will be displayed. So, if you have a multi-monitor display, you can remove it after running this program. You will have to run ```source ~/.profile``` after removing the line from the file.

### Detailed instructions:
- Place your ```asm``` program in the src folder.
- Open a terminal and navigate to the ```code/``` folder. Execute: ```python assembler.py src/<filename.asm>```.
- This will generate the ```bin``` file in ```build/<filename.bin>```.
- Now run: ```python main.py build/<filename.bin>``` to launch the simulation
- The simulation supports pausing, stepping back and forward - one step at a time.
- To stop the simulation, simply close the window
- The data memory is stored in ```data_memory.dat```. You can either modify the same file, or create a separate file.
  The data memory file can be chosen from the GUI itself(Load > Load from data memory). Or while executing the program:

  ```python main.py build/<filename.bin> <data_mem.data>```

- To change the duration spent on each cycle, open ```constants.py``` and adjust the ```CYCLE_DURATION``` in *milliseconds* to your desired value.

-----

### Known Bugs

1. The "Prev" button can't go below PC=2. Its a pain to figure out how to implement history in the GUI related code in ```main.py```, so I left it as is. After all, how much even happens in the first two cycles.

2. ```DEBUG=True``` doesn't print a whole lot of intelligible data. This is sorely because I didn't have the time and patience to complete it yet. Enjoy the GUI though.

3. While going to the next "event" step, if the next happens to be the last step of the entire execution, the program WILL hang. My history traversal mechanism are pretty buggy right now. If the program hangs, please go to the terminal(from where the python program was started) and press ```Ctrl+C```.
--------------

### License

We have MIT licensed this project **except for the RISC-V references**. RISC-V opcodes repo [riscv/riscv-opcodes](https://github.com/riscv/riscv-opcodes) is licensed by the University of California.
