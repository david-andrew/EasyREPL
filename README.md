# Easy REPL
A simple python class for creating Read Evaluate Print Line (REPL) interfaces.

## Requirements

This module requires Python 3.8 or higher.

EasyREPL is a pure-Python line editor with no dependency on GNU readline. It works
on Linux, macOS, and Windows (Windows uses [colorama](https://pypi.org/project/colorama/)
to enable ANSI escape-sequence processing on the console).

## Installation

```bash
pip install easyrepl
```

## Usage

This module exposes the `REPL` class which can be used to quickly create a REPL interface. `REPL` reads a line of user input via a built-in line editor that allows you to move the cursor with the arrow keys, navigate previous inputs, and edit multi-line input.

```python
from easyrepl import REPL

for line in REPL():
    # do something with line
    print(line)
```

which will create a simple echoing REPL interface that repeats any line you type into it.

```bash
>>> hello
hello
>>> world
world
>>>
```

The input supports the following key bindings:
- **Ctrl-D**: exit REPL (on an empty buffer); otherwise forward-delete
- **Ctrl-L**: clear screen
- **Ctrl-R**: reverse-i-search through history
- **Left/Right Arrow**: move cursor left/right
- **Up/Down Arrow**: move up/down within a multi-line input; at the top/bottom edge, navigates previous/next history entry
- **Home / Ctrl-A**: move cursor to beginning of line
- **End / Ctrl-E**: move cursor to end of line
- **Alt-B / Ctrl-Left**: move cursor backward one word
- **Alt-F / Ctrl-Right**: move cursor forward one word
- **Ctrl-K**: delete from cursor to end of line
- **Ctrl-U**: delete from cursor to beginning of line
- **Ctrl-W**: delete from cursor to beginning of word
- **Alt-D**: delete from cursor to end of word
- **Ctrl-C**: abort current input (or quit, if `ctrl_c_quit=True`)


## Multi-line input

Multi-line input can be entered by starting a line with triple quotes (`"""` or `'''`),
and ending the final line with a matching triple quote. Triple quotes in the middle
of a line have no effect.


```
>>> """
... This is a multi-line input
... that will continue until
... the user enters three quotes
... at the end of a line
... """
This is a multi-line input
that will continue until
the user enters three quotes
at the end of a line
>>>
```

A single newline is stripped from the beginning and end of the result if present.

Within a multi-line block, the Up and Down arrow keys move the cursor between
lines of the buffer. When the cursor is on the first row, Up navigates to the
previous history entry; when it's on the last row, Down navigates to the next
history entry. Pressing Enter inserts a newline unless the cursor is at the end
of the buffer and the block is closed (the line then gets submitted).

## API

```python
REPL(*, prompt='>>> ', continuation_prompt='... ', history=None,
     dedup_history=True, ctrl_c_quit=False)
```

- `prompt`: prompt rendered before the first line of each input.
- `continuation_prompt`: prompt rendered on every line of a multi-line input after the first.
- `history`: path to a file used to load and persist history; `None` keeps history in-memory only.
- `dedup_history`: when True, appending an entry removes any earlier identical entries.
- `ctrl_c_quit`: when True, Ctrl-C re-raises `KeyboardInterrupt` to terminate the REPL.

```python
readl(*, prompt='', continuation_prompt='... ', history=None,
      dedup_history=True, ctrl_c_quit=True) -> str
```

Read a single line using the REPL editor and return it. Takes the same
keyword arguments as `REPL` (except `ctrl_c_quit` defaults to `True` here).
History is shared process-wide keyed by `history`, so repeated `readl` calls —
and a `REPL` using the same `history` — participate in the same history.
