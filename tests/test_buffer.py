from easyrepl.buffer import Buffer


def test_insert_and_backspace():
    buf = Buffer()
    for c in 'hi':
        buf.insert_char(c)
    assert buf.text == 'hi'
    buf.backspace()
    assert buf.text == 'h'


def test_multiline_newline():
    buf = Buffer.from_text('ab')
    buf.move_end_of_buffer()
    buf.insert_newline()
    buf.insert_char('c')
    assert buf.text == 'ab\nc'
    assert buf.row == 1 and buf.col == 1


def test_word_motion():
    buf = Buffer.from_text('foo bar_baz')
    buf.move_end_of_buffer()
    buf.move_word_left()
    assert buf.col == 4
    buf.move_word_left()
    assert buf.col == 0


def test_kill_line():
    buf = Buffer.from_text('hello world')
    buf.move_bol()
    buf.move_right()
    buf.move_right()
    buf.kill_to_eol()
    assert buf.text == 'he'
