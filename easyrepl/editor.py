from typing import Optional

from .buffer import Buffer
from .history import History
from .keys import Key, read_key
from .render import Renderer
from .terminal import Terminal


class _Submit(Exception):
    pass


class _Abort(Exception):
    pass


class _Eof(Exception):
    pass


class LineEditor:
    """Interactive multi-line line editor over a Terminal.

    Reads one user input at a time. Returns the finished text from `edit()`,
    or raises KeyboardInterrupt on Ctrl-C / EOFError on Ctrl-D in empty buffer.
    """

    def __init__(
        self,
        terminal: Terminal,
        history: History,
        prompt: str,
        continuation_prompt: str,
    ):
        self.terminal = terminal
        self.history = history
        self.renderer = Renderer(terminal, prompt, continuation_prompt)

    def edit(self) -> str:
        buf = Buffer()
        self.history.reset()
        self.renderer.reset()

        while True:
            self.renderer.render(buf)
            key = read_key(self.terminal)

            try:
                self._dispatch(key, buf)
            except _Submit:
                text = self._finalize_text(buf)
                if text is None:
                    buf.insert_newline()
                    continue
                self.renderer.finalize()
                return text
            except _Abort:
                self.renderer.finalize()
                raise KeyboardInterrupt
            except _Eof:
                self.renderer.finalize()
                raise EOFError

    def _finalize_text(self, buf: Buffer) -> Optional[str]:
        """Return the submission string if the buffer is complete, else None.

        Handles the triple-quote multi-line stripping rules from the legacy
        implementation: the surrounding triple quotes are removed, then up to
        one leading newline and one trailing newline are stripped.
        """
        text = buf.text
        if text.startswith('"""') or text.startswith("'''"):
            delim = text[:3]
            if len(text) < 6 or not text.endswith(delim):
                return None
            body = text[3:-3]
            if body.startswith('\n'):
                body = body[1:]
            if body.endswith('\n'):
                body = body[:-1]
            return body
        return text

    def _is_complete(self, buf: Buffer) -> bool:
        text = buf.text
        if text.startswith('"""') or text.startswith("'''"):
            delim = text[:3]
            return len(text) >= 6 and text.endswith(delim)
        return True

    def _replace_buf(self, buf: Buffer, text: str) -> None:
        buf.replace_with(Buffer.from_text(text))

    def _dispatch(self, key: Key, buf: Buffer) -> None:
        name = key.name

        if name == 'char':
            buf.insert_char(key.char)
            return
        if name == 'enter':
            if self._is_complete(buf) and buf.is_at_end_of_buffer():
                raise _Submit
            buf.insert_newline()
            return
        if name == 'backspace':
            buf.backspace()
            return
        if name == 'delete':
            buf.delete()
            return
        if name in ('left', 'ctrl-b'):
            buf.move_left()
            return
        if name in ('right', 'ctrl-f'):
            buf.move_right()
            return
        if name == 'up':
            if not buf.move_up():
                entry = self.history.prev(buf.text)
                if entry is not None:
                    self._replace_buf(buf, entry)
            return
        if name == 'down':
            if not buf.move_down():
                entry = self.history.next(buf.text)
                if entry is not None:
                    self._replace_buf(buf, entry)
            return
        if name in ('home', 'ctrl-a'):
            buf.move_bol()
            return
        if name in ('end', 'ctrl-e'):
            buf.move_eol()
            return
        if name in ('ctrl-left', 'alt-b'):
            buf.move_word_left()
            return
        if name in ('ctrl-right', 'alt-f'):
            buf.move_word_right()
            return
        if name == 'ctrl-w':
            buf.delete_word_left()
            return
        if name in ('alt-d', 'ctrl-delete'):
            buf.delete_word_right()
            return
        if name == 'ctrl-k':
            buf.kill_to_eol()
            return
        if name == 'ctrl-u':
            buf.kill_to_bol()
            return
        if name == 'ctrl-l':
            self.renderer.clear_screen()
            return
        if name == 'ctrl-c':
            raise _Abort
        if name == 'ctrl-d':
            if not buf.text:
                raise _Eof
            buf.delete()
            return
        if name == 'ctrl-r':
            self._search_mode(buf)
            return

    def _search_mode(self, buf: Buffer) -> None:
        """Reverse-i-search sub-mode.

        Saves the current buffer; types-pattern extends or shrinks the search
        string; Ctrl-R steps to the previous match; Enter accepts the current
        match and submits; Esc / Ctrl-G / Ctrl-C cancels and restores the buffer.
        """
        saved = Buffer(
            lines=list(buf.lines),
            row=buf.row,
            col=buf.col,
            desired_col=buf.desired_col,
        )
        pattern = ""
        match_idx: Optional[int] = None
        search_from: Optional[int] = None

        def apply_match() -> None:
            if match_idx is not None:
                self._replace_buf(buf, self.history.entries[match_idx])
            else:
                buf.replace_with(saved)

        def render_search() -> None:
            shown = pattern
            self.renderer.render(buf, footer=f"(reverse-i-search)`{shown}': ")

        while True:
            render_search()
            key = read_key(self.terminal)
            name = key.name

            if name == 'char':
                pattern += key.char
                match_idx = self.history.search_back(pattern)
                search_from = match_idx
                apply_match()
                continue
            if name == 'backspace':
                pattern = pattern[:-1]
                if pattern:
                    match_idx = self.history.search_back(pattern)
                else:
                    match_idx = None
                search_from = match_idx
                apply_match()
                continue
            if name == 'ctrl-r':
                if pattern and search_from is not None:
                    new_match = self.history.search_back(pattern, before=search_from)
                    if new_match is not None:
                        match_idx = new_match
                        search_from = new_match
                        apply_match()
                continue
            if name in ('escape', 'ctrl-g', 'ctrl-c'):
                buf.replace_with(saved)
                return
            if name == 'enter':
                raise _Submit
            return
