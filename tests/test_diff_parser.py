from pathlib import Path

from specguard.parsers.git_diff import parse_diff

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_diff():
    diff = (FIXTURES / "sample.diff").read_text(encoding="utf-8")
    changes = parse_diff(diff)
    assert len(changes) == 2
    assert changes[0].path == "src/specguard/parsers/kiro_spec.py"
    assert "parse_requirements" in changes[0].symbols
    assert changes[1].status == "added"
