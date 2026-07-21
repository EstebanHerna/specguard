from __future__ import annotations

import re
from pathlib import Path

from specguard.models import AcceptanceCriterion, Requirement, SpecTask

REQ_HEADER = re.compile(r"^#{2,4}\s*Requirement\s+(\d+)\s*:?\s*(.*)$", re.IGNORECASE)
REQ_HEADER_ES = re.compile(r"^#{2,4}\s*Requisito\s+(\d+)\s*:?\s*(.*)$", re.IGNORECASE)
USER_STORY = re.compile(r"\*\*User Story:?\*\*\s*(.*)", re.IGNORECASE)
CRITERION = re.compile(r"^\s*(\d+)[.)]\s+(WHEN|IF|WHILE|WHERE|THE SYSTEM|CUANDO|SI)\b(.*)", re.IGNORECASE)
TASK_LINE = re.compile(r"^\s*-\s*\[( |x|X)\]\s*(\d+(?:\.\d+)*)?\.?\s*(.*)$")
REQ_REFS = re.compile(r"_?Requirements?:\s*([\d.,\s]+)_?", re.IGNORECASE)


def parse_requirements(path: Path) -> list[Requirement]:
    requirements: list[Requirement] = []
    current: Requirement | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        m = REQ_HEADER.match(line) or REQ_HEADER_ES.match(line)
        if m:
            current = Requirement(id=m.group(1), title=m.group(2).strip() or f"Requirement {m.group(1)}")
            requirements.append(current)
            continue
        if current is None:
            continue
        m = USER_STORY.search(line)
        if m:
            current.user_story = m.group(1).strip()
            continue
        m = CRITERION.match(line)
        if m:
            cid = f"{current.id}.{m.group(1)}"
            text = (m.group(2) + m.group(3)).strip()
            current.criteria.append(AcceptanceCriterion(id=cid, text=text))
    return requirements


def parse_tasks(path: Path) -> list[SpecTask]:
    tasks: list[SpecTask] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    auto_id = 0
    for i, raw in enumerate(lines):
        m = TASK_LINE.match(raw)
        if not m:
            continue
        auto_id += 1
        done = m.group(1).lower() == "x"
        task_id = m.group(2) or str(auto_id)
        text = m.group(3).strip()
        refs: list[str] = []
        for lookahead in lines[i + 1 : i + 8]:
            if TASK_LINE.match(lookahead):
                break
            r = REQ_REFS.search(lookahead)
            if r:
                refs = [x.strip() for x in r.group(1).split(",") if x.strip()]
                break
        tasks.append(SpecTask(id=task_id, text=text, done=done, requirement_refs=refs))
    return tasks


def load_spec(spec_dir: Path) -> tuple[list[Requirement], list[SpecTask]]:
    req_file = spec_dir / "requirements.md"
    task_file = spec_dir / "tasks.md"
    requirements = parse_requirements(req_file) if req_file.exists() else []
    tasks = parse_tasks(task_file) if task_file.exists() else []
    return requirements, tasks
