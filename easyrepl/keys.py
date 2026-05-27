from typing import NamedTuple, Optional
from .terminal import Terminal, IS_WINDOWS


class Key(NamedTuple):
    name: str
    char: Optional[str]
    ctrl: bool
    alt: bool


_WIN_SPECIAL = {
    'H': 'up',
    'P': 'down',
    'K': 'left',
    'M': 'right',
    'G': 'home',
    'O': 'end',
    'S': 'delete',
    'I': 'page_up',
    'Q': 'page_down',
    's': 'ctrl-left',
    't': 'ctrl-right',
    '\x8d': 'ctrl-up',
    '\x91': 'ctrl-down',
    '\x93': 'ctrl-delete',
    '\x77': 'ctrl-home',
    '\x75': 'ctrl-end',
    '0': 'alt-b',
    '!': 'alt-n',
    '"': 'alt-m',
    ' ': 'alt-d',
}


def _read_key_posix(term: Terminal) -> Key:
    c = term.read_char()
    b = ord(c) if len(c) == 1 else None

    if b == 0x1b:
        if not term.peek_ready(0.05):
            return Key('escape', None, False, False)
        c2 = term.read_char()
        if c2 == '[' or c2 == 'O':
            seq = c2
            while True:
                ch = term.read_char()
                seq += ch
                if ch.isalpha() or ch == '~':
                    break
                if len(seq) > 16:
                    break
            return _parse_csi(seq)
        return Key('alt-' + c2.lower(), c2, False, True)

    if b == 0x0d or b == 0x0a:
        return Key('enter', None, False, False)
    if b == 0x09:
        return Key('tab', None, False, False)
    if b == 0x7f or b == 0x08:
        return Key('backspace', None, False, False)
    if b is not None and 0x01 <= b <= 0x1a:
        letter = chr(b + 0x60)
        return Key('ctrl-' + letter, None, True, False)
    if b == 0x00:
        return Key('ctrl-space', None, True, False)

    return Key('char', c, False, False)


def _parse_csi(seq: str) -> Key:
    mapping = {
        '[A': 'up',
        '[B': 'down',
        '[C': 'right',
        '[D': 'left',
        '[H': 'home',
        '[F': 'end',
        'OH': 'home',
        'OF': 'end',
        '[3~': 'delete',
        '[5~': 'page_up',
        '[6~': 'page_down',
        '[1~': 'home',
        '[4~': 'end',
        '[7~': 'home',
        '[8~': 'end',
        '[1;5A': 'ctrl-up',
        '[1;5B': 'ctrl-down',
        '[1;5C': 'ctrl-right',
        '[1;5D': 'ctrl-left',
        '[1;3A': 'alt-up',
        '[1;3B': 'alt-down',
        '[1;3C': 'alt-right',
        '[1;3D': 'alt-left',
        '[5C': 'ctrl-right',
        '[5D': 'ctrl-left',
        '[3;5~': 'ctrl-delete',
    }
    if seq in mapping:
        name = mapping[seq]
        ctrl = name.startswith('ctrl-')
        alt = name.startswith('alt-')
        return Key(name, None, ctrl, alt)
    return Key('unknown', None, False, False)


def _read_key_windows(term: Terminal) -> Key:
    c = term.read_char()
    if c == '\x00' or c == '\xe0':
        c2 = term.read_char()
        name = _WIN_SPECIAL.get(c2)
        if name is None:
            return Key('unknown', None, False, False)
        ctrl = name.startswith('ctrl-')
        alt = name.startswith('alt-')
        return Key(name, None, ctrl, alt)

    if c == '\r' or c == '\n':
        return Key('enter', None, False, False)
    if c == '\t':
        return Key('tab', None, False, False)
    if c == '\x08' or c == '\x7f':
        return Key('backspace', None, False, False)
    if c == '\x1b':
        if term.peek_ready(0.05):
            c2 = term.read_char()
            if c2 == '[' or c2 == 'O':
                seq = c2
                while True:
                    ch = term.read_char()
                    seq += ch
                    if ch.isalpha() or ch == '~':
                        break
                    if len(seq) > 16:
                        break
                return _parse_csi(seq)
            return Key('alt-' + c2.lower(), c2, False, True)
        return Key('escape', None, False, False)
    if c == '\x03':
        return Key('ctrl-c', None, True, False)

    b = ord(c) if len(c) == 1 else None
    if b is not None and 0x01 <= b <= 0x1a:
        letter = chr(b + 0x60)
        return Key('ctrl-' + letter, None, True, False)

    return Key('char', c, False, False)


def read_key(term: Terminal) -> Key:
    """Read one key event from the terminal.

    On Windows, msvcrt converts Ctrl-C into a KeyboardInterrupt at the runtime
    level instead of returning '\\x03'; we catch that and synthesize a ctrl-c key.
    """
    try:
        if IS_WINDOWS:
            return _read_key_windows(term)
        return _read_key_posix(term)
    except KeyboardInterrupt:
        return Key('ctrl-c', None, True, False)
