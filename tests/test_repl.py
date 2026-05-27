import subprocess
import sys


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
