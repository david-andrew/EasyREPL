#!/usr/bin/env python3
"""Drive easyrepl through a real TTY (PTY on POSIX, winpty on Windows).

Exits 0 when a line can be typed and read back via readl(); non-zero on failure.
"""

from __future__ import annotations

import os
import platform
import select
import subprocess
import sys
import time

_CHILD = (
    "from easyrepl import readl; print('RESULT:' + repr(readl(prompt='>>> ')))"
)
_EXPECTED = b"RESULT:'smoke-line'"


def _posix_smoke() -> int:
    master, slave = os.openpty()
    child = subprocess.Popen(
        [sys.executable, '-c', _CHILD],
        stdin=slave,
        stdout=slave,
        stderr=slave,
        close_fds=True,
    )
    os.close(slave)
    time.sleep(0.25)
    os.write(master, b'smoke-line\r')
    captured = _read_until_done(child, master)
    os.close(master)
    child.wait(timeout=5)
    return _check(child.returncode, captured)


def _windows_smoke() -> int:
    try:
        from winpty import PtyProcess
    except ImportError:
        print('pywinpty required on Windows: pip install pywinpty', file=sys.stderr)
        return 1

    proc = PtyProcess.spawn([sys.executable, '-c', _CHILD])
    time.sleep(0.5)
    proc.write('smoke-line\r')
    captured = b''
    deadline = time.time() + 15
    while time.time() < deadline:
        if _EXPECTED in captured:
            break
        try:
            chunk = proc.read(4096)
        except EOFError:
            break
        if chunk:
            if isinstance(chunk, bytes):
                captured += chunk
            else:
                captured += chunk.encode('utf-8', errors='replace')
        if not proc.isalive():
            break
        time.sleep(0.05)
    proc.wait()
    return _check(proc.exitstatus, captured)


def _read_until_done(child: subprocess.Popen, master: int) -> bytes:
    captured = b''
    deadline = time.time() + 10
    while time.time() < deadline:
        if _EXPECTED in captured:
            break
        if child.poll() is not None and _EXPECTED in captured:
            break
        ready, _, _ = select.select([master], [], [], 0.1)
        if ready:
            chunk = os.read(master, 4096)
            if not chunk:
                break
            captured += chunk
    return captured


def _check(returncode: int | None, captured: bytes) -> int:
    if _EXPECTED not in captured:
        print('missing expected RESULT in TTY output', file=sys.stderr)
        print(captured.decode('utf-8', errors='replace'), file=sys.stderr)
        return 1
    if returncode not in (None, 0):
        print(f'child exit {returncode}', file=sys.stderr)
        print(captured.decode('utf-8', errors='replace'), file=sys.stderr)
        return 1
    print(f'{platform.system()} TTY smoke OK')
    return 0


def main() -> int:
    if platform.system() == 'Windows':
        return _windows_smoke()
    if not hasattr(os, 'openpty'):
        print('openpty not available on this platform', file=sys.stderr)
        return 1
    return _posix_smoke()


if __name__ == '__main__':
    raise SystemExit(main())
