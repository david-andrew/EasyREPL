import sys
from os import PathLike
from typing import Iterator, Optional, Union

from .editor import LineEditor
from .history import History
from .terminal import Terminal


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
        self.history = History(path=history, dedup=dedup_history)
        self.ctrl_c_quit = ctrl_c_quit

    def __iter__(self) -> Iterator[str]:
        if not sys.stdin.isatty():
            yield from self._fallback_iter()
            return

        while True:
            try:
                with Terminal() as term:
                    editor = LineEditor(
                        term,
                        self.history,
                        self.prompt,
                        self.continuation_prompt,
                    )
                    line = editor.edit()
            except KeyboardInterrupt:
                if self.ctrl_c_quit:
                    raise
                print('KeyboardInterrupt')
                continue
            except EOFError:
                return

            if line:
                self.history.append(line)
                yield line

    def _fallback_iter(self) -> Iterator[str]:
        """Plain `input()` loop for non-TTY stdin (pipes, redirects)."""
        while True:
            try:
                line = input(self.prompt)
            except EOFError:
                return
            except KeyboardInterrupt:
                if self.ctrl_c_quit:
                    raise
                print('KeyboardInterrupt')
                continue
            if line.startswith('"""') or line.startswith("'''"):
                delim = line[:3]
                rest = line[3:]
                parts = [rest]
                while True:
                    if parts[-1].endswith(delim):
                        break
                    try:
                        parts.append(input(self.continuation_prompt))
                    except EOFError:
                        return
                joined = '\n'.join(parts)
                line = joined[:-3]
                if line.startswith('\n'):
                    line = line[1:]
                if line.endswith('\n'):
                    line = line[:-1]
            if line:
                self.history.append(line)
                yield line


def readl(*, prompt: str = '', ctrl_c_quit: bool = True, **kwargs) -> str:
    """Read a single line via the REPL editor, returning its contents."""
    return next(iter(REPL(prompt=prompt, ctrl_c_quit=ctrl_c_quit, **kwargs)))


if __name__ == '__main__':
    for line in REPL(history='history.txt'):
        print(line)
