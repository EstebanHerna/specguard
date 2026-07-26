from click.testing import CliRunner

from specguard.cli import main
from specguard.models import AuditReport
from specguard.report.badge import write_badge


def _report(score_requirements: int, covered: int) -> AuditReport:
    from specguard.models import Requirement

    report = AuditReport(spec_name="demo", diff_ref="HEAD~1")
    report.requirements = [Requirement(id=str(i), title=f"Req {i}") for i in range(score_requirements)]
    for i in range(covered):
        report.coverage[str(i)] = ["file.py"]
    return report


def test_green_badge_at_or_above_90(tmp_path):
    report = _report(10, 9)
    assert report.score == 90.0
    path = tmp_path / "badge.svg"
    write_badge(report, path)
    svg = path.read_text(encoding="utf-8")
    assert "#4c1" in svg
    assert "90.0%" in svg


def test_yellow_badge_between_70_and_90(tmp_path):
    report = _report(10, 7)
    assert report.score == 70.0
    path = tmp_path / "badge.svg"
    write_badge(report, path)
    svg = path.read_text(encoding="utf-8")
    assert "#dfb317" in svg
    assert "70.0%" in svg


def test_red_badge_below_70(tmp_path):
    report = _report(10, 1)
    assert report.score == 10.0
    path = tmp_path / "badge.svg"
    write_badge(report, path)
    svg = path.read_text(encoding="utf-8")
    assert "#e05d44" in svg
    assert "10.0%" in svg


def test_write_badge_creates_missing_output_directory(tmp_path):
    path = tmp_path / "nested" / "dir" / "badge.svg"
    write_badge(_report(4, 4), path)
    assert path.exists()


def test_cli_does_not_write_badge_by_default(tmp_path):
    output = tmp_path / "reports"
    result = CliRunner().invoke(
        main,
        ["audit", "--spec", ".kiro/specs/specguard-core", "--diff",
         "4b825dc642cb6eb9a060e54bf8d69288fbee4904", "--output", str(output)],
    )
    assert result.exit_code == 0, result.output
    assert not (output / "badge.svg").exists()


def test_cli_writes_badge_when_flag_passed(tmp_path):
    output = tmp_path / "reports"
    result = CliRunner().invoke(
        main,
        ["audit", "--spec", ".kiro/specs/specguard-core", "--diff",
         "4b825dc642cb6eb9a060e54bf8d69288fbee4904", "--output", str(output), "--badge"],
    )
    assert result.exit_code == 0, result.output
    assert (output / "badge.svg").exists()
    assert "100.0%" in (output / "badge.svg").read_text(encoding="utf-8")
