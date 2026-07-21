from pathlib import Path

from specguard.parsers.kiro_spec import parse_requirements, parse_tasks

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_requirements():
    reqs = parse_requirements(FIXTURES / "requirements.md")
    assert len(reqs) == 2
    assert reqs[0].id == "1"
    assert "spec" in reqs[0].title.lower() or reqs[0].title
    assert len(reqs[0].criteria) == 2
    assert reqs[0].criteria[0].id == "1.1"


def test_parse_tasks():
    tasks = parse_tasks(FIXTURES / "tasks.md")
    assert len(tasks) == 3
    assert tasks[0].done is True
    assert tasks[0].requirement_refs == ["1.1", "1.2"]
    assert tasks[2].done is False
