from __future__ import annotations

import json
import os

from specguard.models import AuditReport, Finding, Verdict

DEFAULT_MODEL = "anthropic.claude-3-5-haiku-20241022-v1:0"

PROMPT_TEMPLATE = """You are a traceability auditor. Given the requirements of a Kiro spec
and the code diff of a pull request, refine the preliminary findings.

Requirements:
{requirements}

Tasks marked as done:
{tasks}

Changed files and added lines (truncated):
{changes}

Preliminary findings:
{findings}

Return ONLY a JSON array. Each element:
{{"verdict": "covered|phantom_task|orphan_code|untested_criterion|uncovered_requirement",
  "subject_id": "...", "detail": "...", "confidence": 0.0-1.0}}
Adjust, confirm or discard preliminary findings based on semantic analysis."""


def _serialize_for_prompt(report: AuditReport) -> dict[str, str]:
    reqs = "\n".join(
        f"- [{r.id}] {r.title}: {r.user_story} | criteria: "
        + "; ".join(c.text for c in r.criteria)
        for r in report.requirements
    )
    tasks = "\n".join(
        f"- [{t.id}] {t.text} (refs: {', '.join(t.requirement_refs) or 'none'})"
        for t in report.tasks
        if t.done
    )
    changes = []
    for c in report.changes[:20]:
        added = []
        for h in c.hunks[:5]:
            added.extend(h.added[:15])
        changes.append(f"## {c.path} ({c.status})\n" + "\n".join(added[:40]))
    findings = "\n".join(
        f"- {f.verdict.value} | {f.subject_id} | {f.detail}" for f in report.findings
    )
    return {
        "requirements": reqs or "(none)",
        "tasks": tasks or "(none)",
        "changes": "\n\n".join(changes) or "(none)",
        "findings": findings or "(none)",
    }


def refine_with_bedrock(report: AuditReport) -> AuditReport:
    try:
        import boto3

        client = boto3.client(
            "bedrock-runtime",
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
        )
        prompt = PROMPT_TEMPLATE.format(**_serialize_for_prompt(report))
        response = client.converse(
            modelId=os.environ.get("SPECGUARD_BEDROCK_MODEL", DEFAULT_MODEL),
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 4000, "temperature": 0.0},
        )
        text = response["output"]["message"]["content"][0]["text"]
        start, end = text.find("["), text.rfind("]") + 1
        raw_findings = json.loads(text[start:end])
        refined = [
            Finding(
                verdict=Verdict(f["verdict"]),
                subject_id=str(f["subject_id"]),
                detail=str(f["detail"]),
                confidence=float(f.get("confidence", 0.8)),
            )
            for f in raw_findings
        ]
        report.findings = refined
        report.semantic_used = True
    except Exception:
        report.semantic_used = False
    return report
