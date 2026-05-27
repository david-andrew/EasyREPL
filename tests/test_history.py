from pathlib import Path

from easyrepl.history import History


def test_prev_next_roundtrip(tmp_path: Path):
    h = History()
    h.append('one')
    h.append('two')
    assert h.prev('draft') == 'two'
    assert h.prev('two') == 'one'
    assert h.next('one') == 'two'
    assert h.next('two') == 'draft'


def test_dedup(tmp_path: Path):
    path = tmp_path / 'hist.jsonl'
    h = History(path=path, dedup=True)
    h.append('a')
    h.append('b')
    h.append('a')
    assert h.entries == ['b', 'a']


def test_load_legacy_lines(tmp_path: Path):
    path = tmp_path / 'hist.txt'
    path.write_text('legacy-one\nlegacy-two\n', encoding='utf-8')
    h = History(path=path)
    assert h.entries == ['legacy-one', 'legacy-two']
