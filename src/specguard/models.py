from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum


class Verdict(str, Enum):
    COVERED = "covered"
    PHANTOM_TASK = "phantom_task"
    ORPHAN_CODE = "orphan_code"
    UNTESTED_CRITERION = "untested_criterion"
    UNCOVERED_REQUIREMENT = "uncovered_requirement"


@dataclass
class AcceptanceCriterion:
    id: str
    text: str


@dataclass
class Requirement:
    id: str
    title: str
    user_story: str = ""
    criteria: list[AcceptanceCriterion] = field(default_factory=list)


@dataclass
class SpecTask:
    id: str
    text: str
    done: bool = False
    requirement_refs: list[str] = field(default_factory=list)


@dataclass
class Hunk:
    header: str
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    added_lines: list[int] = field(default_factory=list)


@dataclass
class FileChange:
    path: str
    status: str = "modified"
    hunks: list[Hunk] = field(default_factory=list)
    symbols: list[str] = field(default_factory=list)

    @property
    def is_test(self) -> bool:
        p = self.path.lower()
        return "test" in p or "spec." in p


@dataclass
class Finding:
    verdict: Verdict
    subject_id: str
    detail: str
    evidence: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class AuditReport:
    spec_name: str
    diff_ref: str
    requirements: list[Requirement] = field(default_factory=list)
    tasks: list[SpecTask] = field(default_factory=list)
    changes: list[FileChange] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    coverage: dict[str, list[str]] = field(default_factory=dict)
    semantic_used: bool = False

    @property
    def score(self) -> float:
        total = len(self.requirements)
        if total == 0:
            return 0.0
        covered = sum(1 for r in self.requirements if self.coverage.get(r.id))
        return round(100.0 * covered / total, 1)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["score"] = self.score
        for f in data["findings"]:
            v = f["verdict"]
            f["verdict"] = v.value if isinstance(v, Verdict) else v
        return data
