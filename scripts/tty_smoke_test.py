#!/usr/bin/env python3
"""Drive easyrepl through a real TTY (PTY when available).

Exits 0 when a line can be typed and read back via readl(); non-zero on failure.
"""

from __future__ import annotations

import os
import select
import subprocess
import sys
import time


def _pty_smoke() -> int:
    master, slave = os.openpty()
    child = subprocess.Popen(
        [
            sys.executable,
            '-c',
            "from easyrepl import readl; print('RESULT:' + repr(readl(prompt='>>> ')))",
        ],
        stdin=slave,
        stdout=slave,
        stderr=slave,
        close_fds=True,
    )
    os.close(slave)
    time.sleep(0.25)
    os.write(master, b'smoke-line\r')
    captured = b''
    deadline = time.time() + 10
    while time.time() < deadline:
        if b"RESULT:'smoke-line'" in captured:
            break
        if child.poll() is not None and b'RESULT:' in captured:
            break
        ready, _, _ = select.select([master], [], [], 0.1)
        if ready:
            chunk = os.read(master, 4096)
            if not chunk:
                break
            captured += chunk
    os.close(master)
    child.wait(timeout=5)
    if child.returncode != 0:
        print(f'child exit {child.returncode}', file=sys.stderr)
        print(captured.decode('utf-8', errors='replace'), file=sys.stderr)
        return 1
    if b"RESULT:'smoke-line'" not in captured:
        print('missing expected RESULT in TTY output', file=sys.stderr)
        print(captured.decode('utf-8', errors='replace'), file=sys.stderr)
        return 1
    print('TTY smoke OK')
    return 0


def main() -> int:
    if not hasattr(os, 'openpty'):
        print('openpty not available on this platform', file=sys.stderr)
        return 1
    return _pty_smoke()


if __name__ == '__main__':
    raise SystemExit(main())
