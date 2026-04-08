"""Rich terminal output for scan reports."""

from __future__ import annotations

from debtx.models import ScanReport, Severity

GRADE_COLORS = {
    "A": "bold green",
    "B": "bold blue",
    "C": "bold yellow",
    "D": "bold red",
    "F": "bold white on red",
}

SEVERITY_COLORS = {
    Severity.INFO: "dim",
    Severity.LOW: "cyan",
    Severity.MEDIUM: "yellow",
    Severity.HIGH: "red",
    Severity.CRITICAL: "bold white on red",
}


def _grade_color(grade: str) -> str:
    return GRADE_COLORS.get(grade, "white")


def render_terminal(report: ScanReport) -> None:
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        _render_rich(report)
    except ImportError:
        _render_plain(report)


def _render_rich(report: ScanReport) -> None:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    console = Console()
    console.print()

    # Header
    grade_text = Text(f"  {report.overall_grade}  ", style=_grade_color(report.overall_grade))
    title_line = Text.assemble(
        ("debtx", "bold white"),
        (" scan results", "dim"),
    )
    console.print(Panel(title_line, border_style="blue"))

    # Grade + Vibe Score
    console.print()
    grade_display = Text(f" {report.overall_grade} ", style=_grade_color(report.overall_grade))
    console.print(Text.assemble(("  Grade: ", "bold"), grade_display))
    console.print()

    vibe_bar = _build_vibe_bar_rich(report.vibe_score)
    console.print(Text.assemble(("  Vibe Score: ", "bold"), (f"{report.vibe_score}/100 ", "white")))
    console.print(Text.assemble(("  ", ""), vibe_bar))
    console.print()

    # Stats line
    total_findings = sum(len(r.findings) for r in report.file_reports)
    console.print(
        Text.assemble(
            ("  Files: ", "dim"),
            (str(report.files_scanned), "white"),
            ("  Lines: ", "dim"),
            (str(report.total_lines), "white"),
            ("  Issues: ", "dim"),
            (str(total_findings), "white"),
        )
    )
    console.print()

    # Category table
    table = Table(
        title="Category Breakdown",
        title_style="bold",
        border_style="dim",
        show_lines=False,
        pad_edge=True,
    )
    table.add_column("Category", style="white", min_width=24)
    table.add_column("Grade", justify="center", min_width=6)
    table.add_column("Score", justify="right", min_width=8)
    table.add_column("Issues", justify="right", min_width=8)

    for cs in sorted(report.category_scores, key=lambda x: x.score):
        grade_styled = Text(f" {cs.grade} ", style=_grade_color(cs.grade))
        table.add_row(
            cs.name,
            grade_styled,
            f"{cs.score:.0f}",
            str(cs.finding_count),
        )

    console.print(table)
    console.print()

    # Top issues by file
    files_with_issues = [r for r in report.file_reports if r.findings]
    files_with_issues.sort(key=lambda r: len(r.findings), reverse=True)

    if files_with_issues:
        console.print(Text("  Hotspots", style="bold"))
        console.print()

        for fr in files_with_issues[:10]:
            high_count = sum(
                1 for f in fr.findings if f.severity >= Severity.HIGH
            )
            color = "red" if high_count > 0 else "yellow"
            console.print(
                Text.assemble(
                    ("  ", ""),
                    (f"{fr.path}", color),
                    (f"  {len(fr.findings)} issues", "dim"),
                    (f"  ({fr.lines} lines)", "dim"),
                )
            )

            for finding in sorted(fr.findings, key=lambda f: -f.severity)[:3]:
                sev_color = SEVERITY_COLORS.get(finding.severity, "white")
                sev_name = finding.severity.name
                console.print(
                    Text.assemble(
                        ("    ", ""),
                        (f"L{finding.line} ", "dim"),
                        (f"[{sev_name}]", sev_color),
                        (f" {finding.message}", "white"),
                    )
                )

            if len(fr.findings) > 3:
                console.print(
                    Text(f"    ... and {len(fr.findings) - 3} more", style="dim")
                )
            console.print()

    # Summary footer
    console.print(
        Panel(
            Text(report.summary_line, style="bold"),
            border_style=_grade_color(report.overall_grade).replace("bold ", ""),
        )
    )
    console.print()


def _build_vibe_bar_rich(score: int) -> "Text":
    from rich.text import Text

    filled = score // 5
    empty = 20 - filled

    if score >= 75:
        color = "green"
    elif score >= 55:
        color = "yellow"
    elif score >= 35:
        color = "red"
    else:
        color = "bold red"

    bar = Text()
    bar.append("#" * filled, style=color)
    bar.append("-" * empty, style="dim")
    return bar


def _render_plain(report: ScanReport) -> None:
    print()
    print(f"debtx scan results")
    print(f"=" * 40)
    print(f"Grade: {report.overall_grade}")
    print(f"Vibe Score: {report.vibe_score}/100")
    print(f"Files: {report.files_scanned} | Lines: {report.total_lines}")
    print()

    print("Category Breakdown:")
    print(f"{'Category':<28} {'Grade':>5} {'Score':>6} {'Issues':>6}")
    print("-" * 50)
    for cs in sorted(report.category_scores, key=lambda x: x.score):
        print(f"{cs.name:<28} {cs.grade:>5} {cs.score:>6.0f} {cs.finding_count:>6}")

    print()
    print(report.summary_line)
    print()
