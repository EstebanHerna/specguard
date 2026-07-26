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


def test_added_lines_track_new_file_line_numbers_across_context_and_removals():
    diff = (
        "diff --git a/foo.py b/foo.py\n"
        "index 1111111..2222222 100644\n"
        "--- a/foo.py\n"
        "+++ b/foo.py\n"
        "@@ -1,3 +1,6 @@\n"
        " line one\n"
        "+added line two\n"
        "+added line three\n"
        " line four\n"
        "-removed line five\n"
        "+added line five replacement\n"
        " line six\n"
    )
    changes = parse_diff(diff)
    hunk = changes[0].hunks[0]
    assert hunk.added == ["added line two", "added line three", "added line five replacement"]
    assert hunk.added_lines == [2, 3, 5]
