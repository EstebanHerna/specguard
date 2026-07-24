import json

from click.testing import CliRunner

from specguard.cli import main

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def test_specguard_audits_its_own_repository(tmp_path):
    output_dir = tmp_path / "reports"
    result = CliRunner().invoke(
        main,
        [
            "audit",
            "--spec", ".kiro/specs/specguard-core",
            "--diff", EMPTY_TREE,
            "--output", str(output_dir),
        ],
    )
    assert result.exit_code == 0, result.output
    assert (output_dir / "report.json").exists()
    assert (output_dir / "report.md").exists()

    report = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
    assert report["requirements"]

    phantom_tasks = [f for f in report["findings"] if f["verdict"] == "phantom_task"]
    assert phantom_tasks == [], f"Self-audit found phantom tasks: {phantom_tasks}"

    uncovered = [f for f in report["findings"] if f["verdict"] == "uncovered_requirement"]
    assert uncovered == [], f"Self-audit found uncovered requirements: {uncovered}"
