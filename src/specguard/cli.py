from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from specguard import __version__
from specguard.engine.heuristic import run_heuristic_audit
from specguard.models import Verdict
from specguard.parsers.git_diff import collect_changes
from specguard.parsers.kiro_spec import load_spec
from specguard.report.badge import write_badge
from specguard.report.json_report import write_json
from specguard.report.markdown_report import write_markdown

console = Console()


@click.group()
@click.version_option(__version__)
def main() -> None:
    """SpecGuard: audita si tu codigo realmente implementa tu spec de Kiro."""


@main.command()
@click.option("--spec", "spec_dir", required=True, type=click.Path(exists=True, path_type=Path),
              help="Directorio del spec de Kiro (contiene requirements.md y tasks.md)")
@click.option("--diff", "diff_ref", default="HEAD~1", show_default=True,
              help="Referencia git a comparar (ej. HEAD~1, main...feature)")
@click.option("--semantic/--no-semantic", default=False, show_default=True,
              help="Refinar hallazgos con Bedrock (requiere credenciales AWS)")
@click.option("--output", "-o", type=click.Path(path_type=Path), default=Path("reports"),
              show_default=True, help="Directorio de salida")
@click.option("--fail-under", type=float, default=None,
              help="Codigo de salida 1 si el score queda debajo de este umbral")
@click.option("--badge/--no-badge", default=False, show_default=True,
              help="Emitir badge.svg con el score de trazabilidad")
def audit(
    spec_dir: Path, diff_ref: str, semantic: bool, output: Path, fail_under: float | None, badge: bool
) -> None:
    """Ejecuta la auditoria de trazabilidad spec vs diff."""
    requirements, tasks = load_spec(spec_dir)
    if not requirements:
        console.print(f"[red]No se encontraron requisitos en {spec_dir}[/red]")
        sys.exit(2)
    try:
        changes = collect_changes(diff_ref)
    except Exception as exc:
        console.print(f"[red]Error al obtener el diff: {exc}[/red]")
        sys.exit(2)

    report = run_heuristic_audit(spec_dir.name, diff_ref, requirements, tasks, changes)

    if semantic:
        from specguard.engine.semantic import refine_with_bedrock
        report = refine_with_bedrock(report)
        if not report.semantic_used:
            console.print("[yellow]Bedrock no disponible, usando resultado heuristico[/yellow]")

    write_json(report, output / "report.json")
    write_markdown(report, output / "report.md")
    if badge:
        try:
            write_badge(report, output / "badge.svg")
        except OSError as exc:
            console.print(f"[yellow]No se pudo escribir badge.svg: {exc}[/yellow]")

    table = Table(title=f"SpecGuard - {spec_dir.name} vs {diff_ref}")
    table.add_column("Veredicto")
    table.add_column("Sujeto")
    table.add_column("Detalle", overflow="fold")
    colors = {
        Verdict.COVERED: "green",
        Verdict.PHANTOM_TASK: "red",
        Verdict.ORPHAN_CODE: "yellow",
        Verdict.UNTESTED_CRITERION: "yellow",
        Verdict.UNCOVERED_REQUIREMENT: "red",
    }
    for f in report.findings:
        table.add_row(f"[{colors[f.verdict]}]{f.verdict.value}[/]", f.subject_id, f.detail)
    console.print(table)
    console.print(f"\nScore de trazabilidad: [bold]{report.score}%[/bold]")
    console.print(f"Reportes en: {output}/report.json, {output}/report.md")

    if fail_under is not None and report.score < fail_under:
        sys.exit(1)


if __name__ == "__main__":
    main()
