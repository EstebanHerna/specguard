from specguard.engine.heuristic import run_heuristic_audit, tokenize
from specguard.models import FileChange, Hunk, Requirement, SpecTask, Verdict


def _req(rid, title, story=""):
    return Requirement(id=rid, title=title, user_story=story)


def test_tokenize_splits_snake_case():
    toks = tokenize("parse_requirements file")
    assert "parse" in toks and "requirements" in toks


def test_phantom_task_detected():
    reqs = [_req("1", "Parse spec files", "As a dev I want to parse requirements")]
    tasks = [SpecTask(id="2", text="Implement dashboard", done=True, requirement_refs=["9.1"])]
    changes = [
        FileChange(
            path="src/parser.py",
            symbols=["parse_requirements"],
            hunks=[Hunk(header="", added=["def parse_requirements(path):"])],
        )
    ]
    report = run_heuristic_audit("demo", "HEAD~1", reqs, tasks, changes)
    verdicts = {f.verdict for f in report.findings}
    assert Verdict.PHANTOM_TASK in verdicts


def test_score_zero_without_requirements():
    report = run_heuristic_audit("demo", "HEAD~1", [], [], [])
    assert report.score == 0.0


def test_untested_criterion_not_masked_by_unrelated_test_file():
    reqs = [_req("1", "Parse spec files", "As a dev I want to parse requirements")]
    changes = [
        FileChange(
            path="src/parser.py",
            symbols=["parse_requirements"],
            hunks=[Hunk(header="", added=["def parse_requirements(path):"])],
        ),
        FileChange(
            path="tests/test_unrelated_thing.py",
            symbols=["test_something_else"],
            hunks=[Hunk(header="", added=["def test_something_else():", "    assert unrelated_module.compute() == 1"])],
        ),
    ]
    report = run_heuristic_audit("demo", "HEAD~1", reqs, [], changes)
    finding = next(f for f in report.findings if f.subject_id == "1")
    assert finding.verdict == Verdict.UNTESTED_CRITERION
