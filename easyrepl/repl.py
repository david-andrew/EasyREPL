import sys
from os import PathLike
from typing import Iterator, Optional, Union

from .editor import LineEditor
from .history import get_history
from .terminal import Terminal


def readl(
    *,
    prompt: str = '',
    continuation_prompt: str = '... ',
    history: Optional[Union[str, PathLike]] = None,
    dedup_history: bool = True,
    ctrl_c_quit: bool = True,
) -> str:
    """Read a single line via the REPL editor, returning its contents.

    History is shared process-wide keyed by `history` (or by None for a shared
    in-memory session history), so repeated `readl` calls participate in the
    same history.

    Args:
        prompt: prompt rendered before the first line of input.
        continuation_prompt: prompt rendered on subsequent lines of a multi-line input.
        history: file path to load/save history. If None, uses the process-shared in-memory history.
        dedup_history: when True, appending an entry removes any prior identical entries.
        ctrl_c_quit: when True, Ctrl-C re-raises KeyboardInterrupt instead of restarting the read.

    Raises:
        EOFError: when the input stream is closed (e.g. Ctrl-D on an empty line).
        KeyboardInterrupt: when `ctrl_c_quit` is True and Ctrl-C is pressed.
    """
    hist = get_history(history, dedup=dedup_history)
    if not sys.stdin.isatty():
        line = _fallback_read(prompt, continuation_prompt, ctrl_c_quit)
    else:
        while True:
            try:
                with Terminal() as term:
                    line = LineEditor(term, hist, prompt, continuation_prompt).edit()
                break
            except KeyboardInterrupt:
                if ctrl_c_quit:
                    raise
                print('KeyboardInterrupt')
    if line:
        hist.append(line)
    return line


def _fallback_read(prompt: str, continuation_prompt: str, ctrl_c_quit: bool) -> str:
    """Plain `input()` single-read for non-TTY stdin (pipes, redirects).

    Handles triple-quoted multi-line submissions the same way the editor does.
    """
    while True:
        try:
            line = input(prompt)
        except KeyboardInterrupt:
            if ctrl_c_quit:
                raise
            print('KeyboardInterrupt')
            continue
        break

    if line.startswith('"""') or line.startswith("'''"):
        delim = line[:3]
        rest = line[3:]
        parts = [rest]
        while not parts[-1].endswith(delim):
            parts.append(input(continuation_prompt))
        joined = '\n'.join(parts)
        line = joined[:-3]
        if line.startswith('\n'):
            line = line[1:]
        if line.endswith('\n'):
            line = line[:-1]
    return line


class REPL:
    """Generator-based Read Evaluate Print Loop with a built-in line editor.

    Args:
        prompt: prompt rendered before the first line of each input. Defaults to '>>> '.
        continuation_prompt: prompt rendered on every line of a multi-line input
            after the first. Defaults to '... '.
        history: file path to load/save history. If None, history is in-memory only.
        dedup_history: when True, appending an entry removes any prior identical entries.
        ctrl_c_quit: when True, Ctrl-C re-raises KeyboardInterrupt to terminate the REPL.

    Yields:
        Each non-empty submission as a string.

    Usage:
        ```python
        for line in REPL():
            print(line)
        ```
    """

    def __init__(
        self,
        *,
        prompt: str = '>>> ',
        continuation_prompt: str = '... ',
        history: Optional[Union[str, PathLike]] = None,
        dedup_history: bool = True,
        ctrl_c_quit: bool = False,
    ):
        self.prompt = prompt
        self.continuation_prompt = continuation_prompt
        self.history = history
        self.dedup_history = dedup_history
        self.ctrl_c_quit = ctrl_c_quit

    def __iter__(self) -> Iterator[str]:
        while True:
            try:
                line = readl(
                    prompt=self.prompt,
                    continuation_prompt=self.continuation_prompt,
                    history=self.history,
                    dedup_history=self.dedup_history,
                    ctrl_c_quit=self.ctrl_c_quit,
                )
            except EOFError:
                return
            if line:
                yield line
