# Easy REPL
A simple python class for creating Read Evaluate Print Line (REPL) interfaces.

## Requirements

This module requires Python (version TBD) or higher. 

Additionally this library uses the `termios` module so it will only work on Unix based systems.

## Usage

This module exposes the `REPL` class which can be used to quickly create a REPL interface.

```python
from easyrepl import REPL

for line in REPL():
    # do something with line
```

Additionally the `readl` function is available. It provides a simple line editor interface for reading in a line of text from the terminal. I.e. you can use the arrow keys to move the cursor and edit the line.

```python
from easyrepl import readl

line = readl()
```