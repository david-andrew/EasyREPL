from easyrepl.editor import LineEditor
from easyrepl.history import History
from tests.conftest import FakeTerminal


def test_simple_line_submit():
    term = FakeTerminal(chars=list('hello') + ['\r'])
    editor = LineEditor(term, History(), '>>> ', '... ')
    assert editor.edit() == 'hello'


def test_triple_quote_multiline():
    """Closing delimiter on last line submits the block."""
    chars = list('"""') + ['\r']
    chars += list('line one') + ['\r']
    chars += list('line two') + ['\r']
    chars += list('"""') + ['\r']
    term = FakeTerminal(chars=chars)
    editor = LineEditor(term, History(), '>>> ', '... ')
    assert editor.edit() == 'line one\nline two'


def test_history_navigation():
    hist = History()
    hist.append('previous')
    term = FakeTerminal(chars=['\x1b', '[', 'A', '\r'])
    editor = LineEditor(term, hist, '>>> ', '... ')
    assert editor.edit() == 'previous'
