from typing import List
from wcwidth import wcswidth

from .buffer import Buffer
from .terminal import Terminal


class Renderer:
    """Differential renderer.

    Tracks the position the cursor was left in after the previous render and
    rewrites the prompt area on each call by moving back to the start of the
    prompt area, erasing to end of screen, and emitting fresh content.
    """

    def __init__(self, terminal: Terminal, prompt: str, continuation_prompt: str):
        self.terminal = terminal
        self.prompt = prompt
        self.continuation_prompt = continuation_prompt
        self.last_cursor_row = 0
        self.last_total_rows = 0

    def reset(self) -> None:
        self.last_cursor_row = 0
        self.last_total_rows = 0

    def _prompt_for_row(self, row: int) -> str:
        return self.prompt if row == 0 else self.continuation_prompt

    @staticmethod
    def _width(s: str) -> int:
        w = wcswidth(s)
        return w if w >= 0 else len(s)

    def render(self, buf: Buffer, footer: str = "") -> None:
        term_width = max(1, self.terminal.size().columns)
        out: List[str] = []

        if self.last_cursor_row > 0:
            out.append(f'\x1b[{self.last_cursor_row}A')
        out.append('\r')
        out.append('\x1b[J')

        rendered_rows: List[int] = []
        for i, line in enumerate(buf.lines):
            if i > 0:
                out.append('\r\n')
            prefix = self._prompt_for_row(i)
            full = prefix + line
            out.append(full)
            line_width = self._width(full)
            base_rows = max(1, (line_width + term_width - 1) // term_width)
            if line_width > 0 and line_width % term_width == 0:
                out.append(' \b')
                base_rows += 1
            rendered_rows.append(base_rows)

        footer_rows = 0
        if footer:
            out.append('\r\n' + footer)
            fw = self._width(footer)
            footer_rows = max(1, (fw + term_width - 1) // term_width)

        target_line = buf.lines[buf.row]
        target_prefix = self._prompt_for_row(buf.row)
        before_cursor_width = self._width(target_prefix + target_line[:buf.col])
        target_visual_row = before_cursor_width // term_width
        target_visual_col = before_cursor_width % term_width

        rows_before = sum(rendered_rows[:buf.row])
        target_row_from_start = rows_before + target_visual_row

        current_row_from_start = sum(rendered_rows) - 1
        if footer:
            current_row_from_start = sum(rendered_rows) + footer_rows - 1

        delta = current_row_from_start - target_row_from_start
        if delta > 0:
            out.append(f'\x1b[{delta}A')
        elif delta < 0:
            out.append(f'\x1b[{-delta}B')
        out.append('\r')
        if target_visual_col > 0:
            out.append(f'\x1b[{target_visual_col}C')

        self.last_total_rows = sum(rendered_rows) + footer_rows
        self.last_cursor_row = target_row_from_start

        self.terminal.write(''.join(out))

    def finalize(self) -> None:
        """Move the cursor past the rendered area and emit a final newline."""
        out: List[str] = []
        if self.last_total_rows == 0:
            return
        delta = (self.last_total_rows - 1) - self.last_cursor_row
        if delta > 0:
            out.append(f'\x1b[{delta}B')
        out.append('\r\n')
        self.terminal.write(''.join(out))
        self.last_cursor_row = 0
        self.last_total_rows = 0

    def clear_screen(self) -> None:
        self.terminal.write('\x1b[2J\x1b[H')
        self.last_cursor_row = 0
        self.last_total_rows = 0
