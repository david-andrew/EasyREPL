import os
import platform
import select
import subprocess
import sys
import time

import pytest


def test_pipe_mode_integration():
    script = """
from easyrepl import REPL
for line in REPL(prompt='> '):
    print('OUT:' + line)
"""
    proc = subprocess.run(
        [sys.executable, '-c', script],
        input='first\nsecond\n',
        text=True,
        capture_output=True,
        timeout=10,
    )
    assert proc.returncode == 0
    assert 'OUT:first' in proc.stdout
    assert 'OUT:second' in proc.stdout


@pytest.mark.skipif(not hasattr(os, 'openpty'), reason='requires os.openpty')
def test_pty_repl_submits_line():
    master, slave = os.openpty()
    proc = subprocess.Popen(
        [sys.executable, '-c', 'from easyrepl import readl; print(readl(prompt=">>> "))'],
        stdin=slave,
        stdout=slave,
        stderr=slave,
        close_fds=True,
    )
    os.close(slave)
    time.sleep(0.25)
    os.write(master, b'pty-test\r')
    out = b''
    deadline = time.time() + 5
    while time.time() < deadline:
        if proc.poll() is not None:
            break
        ready, _, _ = select.select([master], [], [], 0.1)
        if ready:
            chunk = os.read(master, 4096)
            if not chunk:
                break
            out += chunk
            if b'pty-test' in out:
                break
    os.close(master)
    proc.wait(timeout=5)
    assert proc.returncode == 0, (proc.returncode, out)
    assert b'pty-test' in out
