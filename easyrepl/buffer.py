from dataclasses import dataclass, field
from typing import List


def _is_word_char(c: str) -> bool:
    return c.isalnum() or c == '_'


@dataclass
class Buffer:
    """A multi-line text buffer with a cursor.

    `lines` always has at least one entry. `row`/`col` index into it. `desired_col`
    tracks the column the cursor "wants" to be in across vertical movement, so that
    moving up from a short line into a long line preserves the original column.
    """

    lines: List[str] = field(default_factory=lambda: [""])
    row: int = 0
    col: int = 0
    desired_col: int = 0

    @property
    def text(self) -> str:
        return '\n'.join(self.lines)

    @classmethod
    def from_text(cls, text: str) -> 'Buffer':
        lines = text.split('\n') if text else [""]
        buf = cls(lines=lines)
        buf.move_end_of_buffer()
        return buf

    def replace_with(self, other: 'Buffer') -> None:
        self.lines = list(other.lines)
        self.row = other.row
        self.col = other.col
        self.desired_col = other.desired_col

    def insert_char(self, c: str) -> None:
        line = self.lines[self.row]
        self.lines[self.row] = line[:self.col] + c + line[self.col:]
        self.col += len(c)
        self.desired_col = self.col

    def insert_newline(self) -> None:
        line = self.lines[self.row]
        before = line[:self.col]
        after = line[self.col:]
        self.lines[self.row] = before
        self.lines.insert(self.row + 1, after)
        self.row += 1
        self.col = 0
        self.desired_col = 0

    def backspace(self) -> None:
        if self.col > 0:
            line = self.lines[self.row]
            self.lines[self.row] = line[:self.col - 1] + line[self.col:]
            self.col -= 1
        elif self.row > 0:
            prev = self.lines[self.row - 1]
            cur = self.lines[self.row]
            self.col = len(prev)
            self.lines[self.row - 1] = prev + cur
            del self.lines[self.row]
            self.row -= 1
        self.desired_col = self.col

    def delete(self) -> None:
        line = self.lines[self.row]
        if self.col < len(line):
            self.lines[self.row] = line[:self.col] + line[self.col + 1:]
        elif self.row < len(self.lines) - 1:
            self.lines[self.row] = line + self.lines[self.row + 1]
            del self.lines[self.row + 1]
        self.desired_col = self.col

    def move_left(self) -> bool:
        if self.col > 0:
            self.col -= 1
        elif self.row > 0:
            self.row -= 1
            self.col = len(self.lines[self.row])
        else:
            return False
        self.desired_col = self.col
        return True

    def move_right(self) -> bool:
        line = self.lines[self.row]
        if self.col < len(line):
            self.col += 1
        elif self.row < len(self.lines) - 1:
            self.row += 1
            self.col = 0
        else:
            return False
        self.desired_col = self.col
        return True

    def move_up(self) -> bool:
        if self.row > 0:
            self.row -= 1
            self.col = min(self.desired_col, len(self.lines[self.row]))
            return True
        return False

    def move_down(self) -> bool:
        if self.row < len(self.lines) - 1:
            self.row += 1
            self.col = min(self.desired_col, len(self.lines[self.row]))
            return True
        return False

    def move_bol(self) -> None:
        self.col = 0
        self.desired_col = 0

    def move_eol(self) -> None:
        self.col = len(self.lines[self.row])
        self.desired_col = self.col

    def move_end_of_buffer(self) -> None:
        self.row = len(self.lines) - 1
        self.col = len(self.lines[self.row])
        self.desired_col = self.col

    def is_at_end_of_buffer(self) -> bool:
        return self.row == len(self.lines) - 1 and self.col == len(self.lines[-1])

    def _word_left_col(self) -> int:
        line = self.lines[self.row]
        i = self.col
        while i > 0 and not _is_word_char(line[i - 1]):
            i -= 1
        while i > 0 and _is_word_char(line[i - 1]):
            i -= 1
        return i

    def _word_right_col(self) -> int:
        line = self.lines[self.row]
        i = self.col
        while i < len(line) and not _is_word_char(line[i]):
            i += 1
        while i < len(line) and _is_word_char(line[i]):
            i += 1
        return i

    def move_word_left(self) -> None:
        if self.col == 0 and self.row > 0:
            self.row -= 1
            self.col = len(self.lines[self.row])
        else:
            self.col = self._word_left_col()
        self.desired_col = self.col

    def move_word_right(self) -> None:
        line = self.lines[self.row]
        if self.col == len(line) and self.row < len(self.lines) - 1:
            self.row += 1
            self.col = 0
        else:
            self.col = self._word_right_col()
        self.desired_col = self.col

    def delete_word_left(self) -> None:
        if self.col == 0:
            if self.row > 0:
                self.backspace()
            return
        new_col = self._word_left_col()
        line = self.lines[self.row]
        self.lines[self.row] = line[:new_col] + line[self.col:]
        self.col = new_col
        self.desired_col = self.col

    def delete_word_right(self) -> None:
        line = self.lines[self.row]
        if self.col == len(line):
            if self.row < len(self.lines) - 1:
                self.delete()
            return
        new_col = self._word_right_col()
        self.lines[self.row] = line[:self.col] + line[new_col:]
        self.desired_col = self.col

    def kill_to_eol(self) -> None:
        line = self.lines[self.row]
        if self.col < len(line):
            self.lines[self.row] = line[:self.col]
        elif self.row < len(self.lines) - 1:
            self.lines[self.row] = line + self.lines[self.row + 1]
            del self.lines[self.row + 1]
        self.desired_col = self.col

    def kill_to_bol(self) -> None:
        line = self.lines[self.row]
        self.lines[self.row] = line[self.col:]
        self.col = 0
        self.desired_col = 0
