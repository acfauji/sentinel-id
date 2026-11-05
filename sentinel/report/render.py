"""Bilingual Markdown report renderers for SENTINEL-ID."""
from __future__ import annotations

import json
from pathlib import Path

from ..labeling.evidence import Evidence


def _render_evidence_section(evidence_list: list[Evidence]) -> str:
    lines = ["## Evidence", ""]
    lines.append("| # | Category | Value | Source | Confidence | Notes |")
    lines.append("|---|---|---|---|---|---|")
    for i, e in enumerate(evidence_list, 1):
        lines.append(
            f"| {i} | {e.category} | `{e.value}` | {e.source} | "
            f"{e.confidence:.2f} | {e.notes} |"
        )
    return "\n".join(lines) + "\n"


def render_report(
    evidence_list: list[Evidence],
    analysis_en: str,
    analysis_id: str,
    subject: str,
) -> dict[str, str]:
    """Return {en, id} Markdown report strings."""
    evidence_md = _render_evidence_section(evidence_list)

    en = f"""# SENTINEL-ID Investigation Report

**Subject:** {subject}
**Generated:** (UTC) · **Evidence items:** {len(evidence_list)}

{evidence_md}
## AI Analysis (English)

{analysis_en or "_No AI analysis available._"}

---
*This report separates collected evidence from AI commentary. AI analysis is advisory only. Verify before acting.*

###### SENTINEL-ID v0.1.0
"""
    id_version = f"""# Laporan Investigasi SENTINEL-ID

**Subjek:** {subject}
**Dibuat:** (UTC) · **Jumlah bukti:** {len(evidence_list)}

{evidence_md}
## Analisis AI (Bahasa Indonesia)

{analysis_id or "_Analisis AI tidak tersedia._"}

---
*Laporan ini memisahkan bukti yang dikumpulkan dari komentar AI. Analisis AI hanya bersifat saran. Verifikasi sebelum bertindak.*

###### SENTINEL-ID v0.1.0
"""
    return {"en": en, "id": id_version}


def write_reports(
    output_dir: Path,
    reports: dict[str, str],
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for lang, text in reports.items():
        p = output_dir / f"report_{lang}.md"
        p.write_text(text, encoding="utf-8")
        paths.append(p)
    return paths
