"""Markdown report formatter."""

from __future__ import annotations

from debtx.models import ScanReport, Severity


def render_markdown(report: ScanReport) -> str:
    lines: list[str] = []

    lines.append(f"# debtx Report: {report.overall_grade} | Vibe Score: {report.vibe_score}/100")
    lines.append("")
    lines.append(
        f"**{report.files_scanned}** files scanned | "
        f"**{report.total_lines}** total lines | "
        f"**{sum(len(r.findings) for r in report.file_reports)}** issues found"
    )
    lines.append("")

    # Category table
    lines.append("## Category Breakdown")
    lines.append("")
    lines.append("| Category | Grade | Score | Issues |")
    lines.append("|----------|:-----:|------:|-------:|")
    for cs in sorted(report.category_scores, key=lambda x: x.score):
        lines.append(f"| {cs.name} | {cs.grade} | {cs.score:.0f} | {cs.finding_count} |")
    lines.append("")

    # Hotspots
    files_with_issues = [r for r in report.file_reports if r.findings]
    files_with_issues.sort(key=lambda r: len(r.findings), reverse=True)

    if files_with_issues:
        lines.append("## Hotspots")
        lines.append("")
        for fr in files_with_issues[:15]:
            lines.append(f"### `{fr.path}` ({len(fr.findings)} issues, {fr.lines} lines)")
            lines.append("")
            for finding in sorted(fr.findings, key=lambda f: -f.severity):
                sev = finding.severity.name
                lines.append(f"- **L{finding.line}** [{sev}] {finding.message}")
            lines.append("")

    # Summary
    lines.append("---")
    lines.append(f"*{report.summary_line}*")
    lines.append("")

    return "\n".join(lines)
