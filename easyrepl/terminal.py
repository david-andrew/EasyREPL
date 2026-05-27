import sys
import os
import platform
import shutil
from typing import Optional

_IS_WINDOWS = platform.system() == 'Windows'

if _IS_WINDOWS:
    import msvcrt
    import time
    import colorama
    colorama.just_fix_windows_console()
else:
    import termios
    import tty
    import select


class Terminal:
    """Cross-platform raw-mode terminal context manager.

    On POSIX, switches stdin into cbreak/raw mode for the duration of the
    context and restores the previous termios state on exit.
    On Windows, raw input is handled by msvcrt directly; colorama is
    initialized at module import to enable VT-mode output processing.
    """

    def __enter__(self) -> 'Terminal':
        if _IS_WINDOWS:
            self.old_settings = None
        else:
            self.fd = sys.stdin.fileno()
            self.old_settings = termios.tcgetattr(self.fd)
            tty.setraw(self.fd)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not _IS_WINDOWS and self.old_settings is not None:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
        self.old_settings = None

    def read_char(self) -> str:
        """Read one logical character (decoding UTF-8 multibyte sequences on POSIX).

        Raises EOFError if the underlying stream is closed.
        """
        if _IS_WINDOWS:
            ch = msvcrt.getwch()
            if ch == '':
                raise EOFError
            return ch

        b = os.read(self.fd, 1)
        if not b:
            raise EOFError
        b0 = b[0]
        if b0 < 0x80:
            return b.decode('latin-1')
        if b0 >= 0xf0:
            n = 4
        elif b0 >= 0xe0:
            n = 3
        elif b0 >= 0xc0:
            n = 2
        else:
            return b.decode('utf-8', errors='replace')
        for _ in range(n - 1):
            more = os.read(self.fd, 1)
            if not more:
                break
            b += more
        return b.decode('utf-8', errors='replace')

    def peek_ready(self, timeout: float = 0.05) -> bool:
        """Return True if a character is available within `timeout` seconds."""
        if _IS_WINDOWS:
            end = time.monotonic() + timeout
            while time.monotonic() < end:
                if msvcrt.kbhit():
                    return True
                time.sleep(0.001)
            return False
        r, _, _ = select.select([self.fd], [], [], timeout)
        return bool(r)

    def write(self, s: str) -> None:
        sys.stdout.write(s)
        sys.stdout.flush()

    def size(self) -> os.terminal_size:
        return shutil.get_terminal_size()


IS_WINDOWS = _IS_WINDOWS
