from __future__ import annotations

import re
import subprocess
from pathlib import Path

from specguard.models import FileChange, Hunk
from specguard.parsers.symbols import symbols_touching_lines

FILE_HEADER = re.compile(r"^diff --git a/(.+?) b/(.+)$")
HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(?P<new_start>\d+)(?:,\d+)? @@(?P<context>.*)$")
SYMBOL_DEF = re.compile(
    r"^\+?\s*(?:def|class)\s+(\w+)"
    r"|^\+?\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)"
    r"|^\+?\s*(?:export\s+)?(?:const|let)\s+(\w+)\s*="
    r"|^\+?\s*(?:public|private|protected)?\s*(?:static\s+)?\w+\s+(\w+)\s*\("
)


def run_git_diff(diff_ref: str, repo: Path | None = None) -> str:
    cmd = ["git", "diff", "--unified=3", diff_ref]
    result = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, check=True)
    return result.stdout


def parse_diff(diff_text: str) -> list[FileChange]:
    changes: list[FileChange] = []
    current: FileChange | None = None
    hunk: Hunk | None = None
    new_line_num = 0
    for line in diff_text.splitlines():
        m = FILE_HEADER.match(line)
        if m:
            current = FileChange(path=m.group(2))
            changes.append(current)
            hunk = None
            continue
        if current is None:
            continue
        if line.startswith("new file"):
            current.status = "added"
            continue
        if line.startswith("deleted file"):
            current.status = "deleted"
            continue
        m = HUNK_HEADER.match(line)
        if m:
            hunk = Hunk(header=m.group("context").strip())
            current.hunks.append(hunk)
            new_line_num = int(m.group("new_start"))
            continue
        if hunk is None:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            hunk.added.append(line[1:])
            hunk.added_lines.append(new_line_num)
            new_line_num += 1
            s = SYMBOL_DEF.match(line)
            if s:
                name = next(g for g in s.groups() if g)
                if name not in current.symbols:
                    current.symbols.append(name)
        elif line.startswith("-") and not line.startswith("---"):
            hunk.removed.append(line[1:])
        elif line.startswith("\\"):
            continue
        else:
            new_line_num += 1
    return changes


def enhance_symbols_with_treesitter(changes: list[FileChange], repo: Path | None = None) -> None:
    # change.path comes from parsed diff text, which callers may source from
    # untrusted input (e.g. a network API). Refuse absolute paths and any
    # path that would resolve outside `base` before ever touching disk.
    base = (repo or Path.cwd()).resolve()
    for change in changes:
        if change.status == "deleted":
            continue
        touched_lines = {n for hunk in change.hunks for n in hunk.added_lines}
        if not touched_lines:
            continue
        candidate = Path(change.path)
        if candidate.is_absolute():
            continue
        file_path = (base / candidate).resolve()
        try:
            file_path.relative_to(base)
        except ValueError:
            continue
        try:
            source = file_path.read_bytes()
        except OSError:
            continue
        symbols = symbols_touching_lines(source, file_path.suffix, touched_lines)
        if symbols is not None:
            change.symbols = symbols


def collect_changes(diff_ref: str, repo: Path | None = None) -> list[FileChange]:
    changes = parse_diff(run_git_diff(diff_ref, repo))
    enhance_symbols_with_treesitter(changes, repo)
    return changes
