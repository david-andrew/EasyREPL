import pytest

from easyrepl.keys import Key, _read_key_posix, _read_key_windows, read_key
from tests.conftest import FakeTerminal


def test_posix_arrow_and_enter():
    term = FakeTerminal(chars=['\x1b', '[', 'A', 'x', '\r'])
    assert _read_key_posix(term).name == 'up'
    key = _read_key_posix(term)
    assert key.name == 'char' and key.char == 'x'
    assert _read_key_posix(term).name == 'enter'


def test_posix_ctrl_letter():
    term = FakeTerminal(chars=['\x01'])
    assert _read_key_posix(term) == Key('ctrl-a', None, True, False)


def test_windows_arrow_prefix():
    term = FakeTerminal(chars=['\x00', 'H', 'a', '\r'])
    assert _read_key_windows(term).name == 'up'
    key = _read_key_windows(term)
    assert key.name == 'char' and key.char == 'a'
    assert _read_key_windows(term).name == 'enter'


def test_windows_ctrl_c_synthetic(monkeypatch):
    monkeypatch.setattr('easyrepl.keys.IS_WINDOWS', True)
    term = FakeTerminal()

    def raise_interrupt():
        raise KeyboardInterrupt

    monkeypatch.setattr(term, 'read_char', raise_interrupt)
    assert read_key(term) == Key('ctrl-c', None, True, False)


@pytest.mark.parametrize('is_windows', [False, True])
def test_read_key_dispatches(monkeypatch, is_windows: bool):
    monkeypatch.setattr('easyrepl.keys.IS_WINDOWS', is_windows)
    term = FakeTerminal(chars=['\x05'])
    key = read_key(term)
    assert key.name == 'ctrl-e'
