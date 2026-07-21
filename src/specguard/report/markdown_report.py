from __future__ import annotations

from pathlib import Path

from specguard.models import AuditReport, Verdict

EMOJI = {
    Verdict.COVERED: "OK",
    Verdict.PHANTOM_TASK: "PHANTOM",
    Verdict.ORPHAN_CODE: "ORPHAN",
    Verdict.UNTESTED_CRITERION: "NO-TEST",
    Verdict.UNCOVERED_REQUIREMENT: "MISSING",
}

TITLES = {
    Verdict.COVERED: "Requisitos cubiertos",
    Verdict.UNCOVERED_REQUIREMENT: "Requisitos sin implementacion",
    Verdict.PHANTOM_TASK: "Tareas fantasma (marcadas sin codigo)",
    Verdict.ORPHAN_CODE: "Codigo huerfano (sin requisito)",
    Verdict.UNTESTED_CRITERION: "Criterios sin test",
}


def render_markdown(report: AuditReport) -> str:
    lines = [
        f"# SpecGuard - Auditoria de `{report.spec_name}`",
        "",
        f"**Diff:** `{report.diff_ref}` | **Score de trazabilidad:** {report.score}% "
        f"| **Analisis semantico:** {'si' if report.semantic_used else 'no (heuristico)'}",
        "",
        "## Matriz de trazabilidad",
        "",
        "| Requisito | Archivos que lo implementan |",
        "|---|---|",
    ]
    for req in report.requirements:
        files = report.coverage.get(req.id) or ["(ninguno)"]
        lines.append(f"| **{req.id}** {req.title} | {', '.join(f'`{f}`' for f in files)} |")
    lines.append("")
    for verdict in [
        Verdict.UNCOVERED_REQUIREMENT,
        Verdict.PHANTOM_TASK,
        Verdict.ORPHAN_CODE,
        Verdict.UNTESTED_CRITERION,
        Verdict.COVERED,
    ]:
        group = [f for f in report.findings if f.verdict == verdict]
        if not group:
            continue
        lines.append(f"## [{EMOJI[verdict]}] {TITLES[verdict]}")
        lines.append("")
        for f in group:
            evidence = f" ({', '.join(f.evidence)})" if f.evidence else ""
            lines.append(f"- `{f.subject_id}`: {f.detail}{evidence} - confianza {f.confidence:.0%}")
        lines.append("")
    return "\n".join(lines)


def write_markdown(report: AuditReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(report), encoding="utf-8")
