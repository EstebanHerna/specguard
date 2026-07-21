from __future__ import annotations

import re
import subprocess
from pathlib import Path

from specguard.models import FileChange, Hunk

FILE_HEADER = re.compile(r"^diff --git a/(.+?) b/(.+)$")
HUNK_HEADER = re.compile(r"^@@ .* @@(.*)$")
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
            hunk = Hunk(header=m.group(1).strip())
            current.hunks.append(hunk)
            continue
        if hunk is None:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            hunk.added.append(line[1:])
            s = SYMBOL_DEF.match(line)
            if s:
                name = next(g for g in s.groups() if g)
                if name not in current.symbols:
                    current.symbols.append(name)
        elif line.startswith("-") and not line.startswith("---"):
            hunk.removed.append(line[1:])
    return changes


def collect_changes(diff_ref: str, repo: Path | None = None) -> list[FileChange]:
    return parse_diff(run_git_diff(diff_ref, repo))
