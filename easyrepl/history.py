import json
from pathlib import Path
from os import PathLike
from typing import List, Optional, Union


class History:
    """In-memory command history with optional JSON-lines persistence.

    The cursor behavior mirrors readline: a fresh entry is added at the bottom,
    `prev()` walks backwards through past entries, and `next()` walks forward,
    returning to the user's pending unsubmitted text once past the most recent.
    """

    def __init__(
        self,
        path: Optional[Union[str, PathLike]] = None,
        dedup: bool = True,
    ):
        self.path: Optional[Path] = None
        self.entries: List[str] = []
        self.dedup = dedup
        self.cursor: Optional[int] = None
        self.pending: str = ""

        if path is not None:
            self.path = Path(path).expanduser().resolve()
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            text = self.path.read_text(encoding='utf-8')
        except OSError:
            return
        for raw_line in text.splitlines():
            if not raw_line:
                continue
            try:
                entry = json.loads(raw_line)
                if isinstance(entry, str):
                    self.entries.append(entry)
                    continue
            except json.JSONDecodeError:
                pass
            # legacy format: each file line is a single history entry
            self.entries.append(raw_line)

    def _save(self) -> None:
        if self.path is None:
            return
        try:
            lines = [json.dumps(e) for e in self.entries]
            self.path.write_text('\n'.join(lines) + ('\n' if lines else ''), encoding='utf-8')
        except OSError:
            pass

    def append(self, entry: str) -> None:
        if not entry:
            return
        if self.dedup:
            self.entries = [e for e in self.entries if e != entry]
        self.entries.append(entry)
        self._save()
        self.reset()

    def reset(self) -> None:
        self.cursor = None
        self.pending = ""

    def _start(self, current: str) -> None:
        if self.cursor is None:
            self.pending = current
            self.cursor = len(self.entries)

    def prev(self, current: str) -> Optional[str]:
        if not self.entries:
            return None
        self._start(current)
        if self.cursor > 0:
            self.cursor -= 1
            return self.entries[self.cursor]
        return None

    def next(self, current: str) -> Optional[str]:
        if self.cursor is None:
            return None
        if self.cursor < len(self.entries) - 1:
            self.cursor += 1
            return self.entries[self.cursor]
        if self.cursor == len(self.entries) - 1:
            self.cursor = len(self.entries)
            return self.pending
        return None

    def search_back(self, pattern: str, before: Optional[int] = None) -> Optional[int]:
        if not pattern:
            return None
        if before is None:
            before = len(self.entries)
        for i in range(before - 1, -1, -1):
            if pattern in self.entries[i]:
                return i
        return None


_cache: 'dict[Optional[Path], History]' = {}


def get_history(path: Optional[Union[str, PathLike]] = None, dedup: bool = True) -> 'History':
    """Return the process-wide History for `path` (or the shared in-memory one if None).

    First caller for a given key sets the History's `dedup` behavior; subsequent
    callers reuse the same instance regardless of the `dedup` they pass.
    """
    key = Path(path).expanduser().resolve() if path is not None else None
    if key not in _cache:
        _cache[key] = History(path=path, dedup=dedup)
    return _cache[key]
