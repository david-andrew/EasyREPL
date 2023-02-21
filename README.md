# Easy REPL
A simple python class for creating Read Evaluate Print Line (REPL) interfaces.

## Requirements

This module requires Python 3.7 or higher. 

Additionally this library uses the `termios` module so it will only work on Unix based systems.

## Usage

This module exposes the `REPL` class which can be used to quickly create a REPL interface. REPL will read in a line of user input via a custom input function that allows you to edit the text by moving the cursor with the arrow keys, as well as view the history of previous inputs.

```python
from easyrepl import REPL

for line in REPL():
    # do something with line
    print(line)
```

which will create a simple echoing REPL interface that repeats any line you type into it (Ctrl-D to exit).

```bash
>>> hello
hello
>>> world
world
>>>
```

Additionally the standalone `readl` function is available. It provides the simple line editor interface for reading in a line of text from the terminal. I.e. you can use the arrow keys to move the cursor and edit the line.

```python
from easyrepl import readl

line = readl()
```