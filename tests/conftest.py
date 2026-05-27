import os
from dataclasses import dataclass, field


@dataclass
class FakeTerminal:
    """Scripted terminal for driving LineEditor without a real TTY."""

    chars: list[str] = field(default_factory=list)
    _index: int = 0
    written: list[str] = field(default_factory=list)

    def read_char(self) -> str:
        if self._index >= len(self.chars):
            raise EOFError
        ch = self.chars[self._index]
        self._index += 1
        return ch

    def peek_ready(self, timeout: float = 0.05) -> bool:
        return self._index < len(self.chars)

    def write(self, s: str) -> None:
        self.written.append(s)

    def size(self) -> os.terminal_size:
        return os.terminal_size((80, 24))
