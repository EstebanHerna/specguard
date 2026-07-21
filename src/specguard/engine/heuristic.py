from __future__ import annotations

import re

from specguard.models import (
    AuditReport,
    FileChange,
    Finding,
    Requirement,
    SpecTask,
    Verdict,
)

STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "for", "with", "shall",
    "when", "then", "if", "system", "user", "should", "will", "that", "this",
    "el", "la", "los", "las", "un", "una", "de", "del", "en", "para", "con",
    "que", "cuando", "si", "debe", "sistema", "usuario", "se", "y", "o",
}

TOKEN = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]{2,}")


def tokenize(text: str) -> set[str]:
    words = set()
    for tok in TOKEN.findall(text.lower()):
        if tok not in STOPWORDS:
            words.add(tok)
            if tok.endswith("s") and len(tok) > 3:
                words.add(tok[:-1])
            for part in re.split(r"_", tok):
                if len(part) > 2 and part not in STOPWORDS:
                    words.add(part)
                    if part.endswith("s") and len(part) > 3:
                        words.add(part[:-1])
    return words


def change_tokens(change: FileChange) -> set[str]:
    toks = tokenize(change.path)
    for sym in change.symbols:
        toks |= tokenize(sym)
        toks |= tokenize(re.sub(r"(?<!^)(?=[A-Z])", " ", sym))
    for hunk in change.hunks:
        for line in hunk.added[:80]:
            toks |= tokenize(line)
    return toks


def match_score(req_tokens: set[str], file_tokens: set[str]) -> float:
    if not req_tokens or not file_tokens:
        return 0.0
    overlap = req_tokens & file_tokens
    ratio = len(overlap) / len(req_tokens)
    if len(overlap) >= 3:
        return max(ratio, 0.5)
    if len(overlap) == 2:
        return max(ratio, 0.2)
    return ratio


def build_coverage(
    requirements: list[Requirement],
    changes: list[FileChange],
    threshold: float = 0.15,
) -> dict[str, list[str]]:
    coverage: dict[str, list[str]] = {}
    file_token_map = {c.path: change_tokens(c) for c in changes}
    for req in requirements:
        req_text = " ".join([req.title, req.user_story] + [c.text for c in req.criteria])
        req_tokens = tokenize(req_text)
        matched = [
            path
            for path, toks in file_token_map.items()
            if match_score(req_tokens, toks) >= threshold
        ]
        coverage[req.id] = matched
    return coverage


def detect_findings(
    requirements: list[Requirement],
    tasks: list[SpecTask],
    changes: list[FileChange],
    coverage: dict[str, list[str]],
) -> list[Finding]:
    findings: list[Finding] = []
    matched_paths = {p for paths in coverage.values() for p in paths}
    test_paths = {c.path for c in changes if c.is_test}

    for req in requirements:
        if not coverage.get(req.id):
            findings.append(
                Finding(
                    verdict=Verdict.UNCOVERED_REQUIREMENT,
                    subject_id=req.id,
                    detail=f"Requisito {req.id} ({req.title}) sin evidencia de implementacion en el diff",
                    confidence=0.7,
                )
            )
        elif not any(p in test_paths for p in coverage[req.id]) and not test_paths:
            findings.append(
                Finding(
                    verdict=Verdict.UNTESTED_CRITERION,
                    subject_id=req.id,
                    detail=f"Requisito {req.id} tiene codigo asociado pero ningun test lo valida",
                    evidence=coverage[req.id],
                    confidence=0.5,
                )
            )
        else:
            findings.append(
                Finding(
                    verdict=Verdict.COVERED,
                    subject_id=req.id,
                    detail=f"Requisito {req.id} cubierto",
                    evidence=coverage[req.id],
                    confidence=0.6,
                )
            )

    for task in tasks:
        if not task.done:
            continue
        refs = task.requirement_refs
        req_ids = {r.split(".")[0] for r in refs} if refs else set()
        has_code = any(coverage.get(rid) for rid in req_ids) if req_ids else bool(matched_paths)
        if not has_code:
            findings.append(
                Finding(
                    verdict=Verdict.PHANTOM_TASK,
                    subject_id=task.id,
                    detail=f"Tarea {task.id} marcada como completa sin cambio de codigo asociado: {task.text}",
                    confidence=0.6,
                )
            )

    for change in changes:
        if change.path not in matched_paths and not change.is_test and change.status != "deleted":
            findings.append(
                Finding(
                    verdict=Verdict.ORPHAN_CODE,
                    subject_id=change.path,
                    detail=f"Cambios en {change.path} sin requisito que los respalde",
                    evidence=change.symbols,
                    confidence=0.5,
                )
            )
    return findings


def run_heuristic_audit(
    spec_name: str,
    diff_ref: str,
    requirements: list[Requirement],
    tasks: list[SpecTask],
    changes: list[FileChange],
) -> AuditReport:
    coverage = build_coverage(requirements, changes)
    findings = detect_findings(requirements, tasks, changes, coverage)
    return AuditReport(
        spec_name=spec_name,
        diff_ref=diff_ref,
        requirements=requirements,
        tasks=tasks,
        changes=changes,
        findings=findings,
        coverage=coverage,
    )
