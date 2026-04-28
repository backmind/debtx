"""CLI entry point for debtx."""

from __future__ import annotations

import click

from debtx import __version__


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="debtx")
@click.pass_context
def main(ctx: click.Context) -> None:
    """debtx - AI-generated code debt scanner. Grade your codebase A-F."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["terminal", "md", "json"]), default="terminal")
@click.option("--lang", type=click.Choice(["python", "typescript", "all"]), default="all")
@click.option("--strict", is_flag=True, help="Use stricter thresholds.")
@click.option("--output", "-o", type=click.Path(), help="Write report to file.")
@click.option("--exclude", multiple=True, help="Glob patterns to exclude.")
@click.option(
    "--fail-under",
    "fail_under",
    type=click.Choice(["A", "B", "C", "D", "F"]),
    default=None,
    help=(
        "Exit non-zero if overall grade is worse than this threshold. "
        "Default: never fail (exit 0 regardless). Use this to opt into "
        "gating; debtx is informative-only by default."
    ),
)
def scan(
    path: str,
    fmt: str,
    lang: str,
    strict: bool,
    output: str | None,
    exclude: tuple[str, ...],
    fail_under: str | None,
) -> None:
    """Scan a codebase for AI-generated technical debt."""
    from debtx.scanner import run_scan

    report = run_scan(
        path=path,
        language_filter=None if lang == "all" else lang,
        strict=strict,
        exclude_patterns=exclude,
    )

    if fmt == "terminal":
        from debtx.display import render_terminal

        render_terminal(report)
    elif fmt == "md":
        from debtx.formatters.markdown import render_markdown

        content = render_markdown(report)
        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(content)
            click.echo(f"Report written to {output}")
        else:
            click.echo(content)
    elif fmt == "json":
        from debtx.formatters.json_fmt import render_json

        content = render_json(report)
        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(content)
            click.echo(f"Report written to {output}")
        else:
            click.echo(content)

    if fail_under is not None:
        from debtx.scoring import grade_meets_threshold

        if not grade_meets_threshold(report.overall_grade, fail_under):
            raise click.exceptions.Exit(1)


@main.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default="debtx-badge.svg")
def badge(path: str, output: str) -> None:
    """Generate a README badge with your grade."""
    from debtx.formatters.badge import generate_badge
    from debtx.scanner import run_scan

    report = run_scan(path=path)
    generate_badge(report.overall_grade, report.vibe_score, output)
    click.echo(f"Badge saved to {output}")
