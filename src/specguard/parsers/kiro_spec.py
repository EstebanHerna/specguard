from __future__ import annotations

import re
from pathlib import Path

from specguard.models import AcceptanceCriterion, Requirement, SpecTask

REQ_HEADER = re.compile(
    r"^(?P<level>#{2,4})(?!#)[ \t]+(?:Requirement|Requisito)[ \t]+"
    r"(?P<id>\d+)(?=$|[ \t]|:)(?:[ \t]*:[ \t]*|[ \t]+)?"
    r"(?P<title>.*?)[ \t]*$",
    re.IGNORECASE,
)
HEADING = re.compile(r"^(?P<level>#{1,6})(?!#)[ \t]+(?P<text>.*?)[ \t]*$")
CRITERIA_HEADING_TEXT = re.compile(
    r"^(?:Acceptance Criteria|Criterios de Aceptaci[oó]n):?$", re.IGNORECASE
)
CRITERION_ENTRY = re.compile(r"^[ \t]*(?:\d+[.)]|[-*])[ \t]+(?P<text>\S.*?)\s*$")
USER_STORY = re.compile(
    r"^[ \t]*\*\*(?:User Story|Historia de Usuario):?\*\*[ \t]*(?P<text>.*?)\s*$",
    re.IGNORECASE,
)
BOLD_LABEL = re.compile(r"^[ \t]*\*\*[^*]+\*\*")
TASK_LINE = re.compile(
    r"^[ \t]*-[ \t]+\[(?P<state>[ xX])\][ \t]+"
    r"(?P<id>\d+(?:\.\d+)*)(?:\.)?[ \t]+(?P<text>.*?)\s*$"
)
REQ_REFS = re.compile(r"_?Requirements?:\s*([\d.,\s]+)_?", re.IGNORECASE)


def _requirement_bodies(lines: list[str]) -> list[tuple[str, str, list[str]]]:
    headers: list[tuple[int, str, str]] = []
    for i, line in enumerate(lines):
        m = REQ_HEADER.match(line.rstrip())
        if m:
            headers.append((i, m.group("id"), m.group("title").strip()))
    bodies = []
    for idx, (start, req_id, title) in enumerate(headers):
        end = headers[idx + 1][0] if idx + 1 < len(headers) else len(lines)
        bodies.append((req_id, title or f"Requirement {req_id}", lines[start + 1 : end]))
    return bodies


def _collect_user_story(body: list[str], start: int) -> tuple[str, int]:
    """Join a user-story label line with any hard-wrapped continuation lines.

    Continuation stops at the first blank line, heading, list entry, or a new
    bold label, so nothing beyond the story itself is ever absorbed.
    """
    parts = [USER_STORY.match(body[start].rstrip()).group("text").strip()]
    j = start + 1
    while j < len(body):
        nxt = body[j].rstrip()
        if not nxt.strip():
            break
        if HEADING.match(nxt) or CRITERION_ENTRY.match(nxt) or BOLD_LABEL.match(nxt):
            break
        parts.append(nxt.strip())
        j += 1
    return " ".join(p for p in parts if p).strip(), j


def _parse_body(req_id: str, body: list[str]) -> tuple[str, list[AcceptanceCriterion]]:
    user_story = ""
    criteria: list[AcceptanceCriterion] = []
    in_criteria = False
    criteria_level = 0
    ordinal = 0
    i = 0
    while i < len(body):
        line = body[i].rstrip()
        h = HEADING.match(line)
        if h:
            level = len(h.group("level"))
            if CRITERIA_HEADING_TEXT.match(h.group("text").strip()):
                in_criteria, criteria_level = True, level
            elif in_criteria and level <= criteria_level:
                in_criteria, criteria_level = False, 0
            i += 1
            continue
        if not user_story and USER_STORY.match(line):
            user_story, i = _collect_user_story(body, i)
            continue
        if in_criteria:
            m = CRITERION_ENTRY.match(line)
            if m:
                ordinal += 1
                criteria.append(
                    AcceptanceCriterion(id=f"{req_id}.{ordinal}", text=m.group("text").strip())
                )
        i += 1
    return user_story, criteria


def parse_requirements(path: Path) -> list[Requirement]:
    lines = path.read_text(encoding="utf-8").splitlines()
    requirements = []
    for req_id, title, body in _requirement_bodies(lines):
        user_story, criteria = _parse_body(req_id, body)
        requirements.append(
            Requirement(id=req_id, title=title, user_story=user_story, criteria=criteria)
        )
    return requirements


def parse_tasks(path: Path) -> list[SpecTask]:
    tasks: list[SpecTask] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, raw in enumerate(lines):
        m = TASK_LINE.match(raw.rstrip())
        if not m:
            continue
        done = m.group("state").lower() == "x"
        refs: list[str] = []
        for lookahead in lines[i + 1 :]:
            if TASK_LINE.match(lookahead.rstrip()):
                break
            r = REQ_REFS.search(lookahead)
            if r:
                refs = [x.strip() for x in r.group(1).split(",") if x.strip()]
                break
        tasks.append(
            SpecTask(id=m.group("id"), text=m.group("text").strip(), done=done, requirement_refs=refs)
        )
    return tasks


def load_spec(spec_dir: Path) -> tuple[list[Requirement], list[SpecTask]]:
    req_file = spec_dir / "requirements.md"
    task_file = spec_dir / "tasks.md"
    requirements = parse_requirements(req_file) if req_file.exists() else []
    tasks = parse_tasks(task_file) if task_file.exists() else []
    return requirements, tasks
