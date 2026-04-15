"""File discovery and scan orchestration."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path

from debtx.ignore import apply_inline_ignores, build_ignore_map
from debtx.languages import FileContext, get_language
from debtx.models import FileReport, ScanReport
from debtx.scoring import (
    build_summary_line,
    calculate_category_scores,
    calculate_overall_grade,
    calculate_vibe_score,
)

_ALWAYS_SKIP = {
    "node_modules",
    "__pycache__",
    ".git",
    "venv",
    ".venv",
    "dist",
    "build",
    ".egg-info",
    ".tox",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "site-packages",
    ".next",
    "coverage",
    ".coverage",
    "htmlcov",
}

_SKIP_EXTENSIONS = {
    ".min.js",
    ".min.css",
    ".map",
    ".lock",
    ".svg",
    ".png",
    ".jpg",
    ".gif",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".pyc",
    ".pyo",
}

_SKIP_FILES = {
    "package-lock.json",
    "yarn.lock",
    "poetry.lock",
    "pnpm-lock.yaml",
    "Pipfile.lock",
}


def _should_skip_dir(dirname: str) -> bool:
    return dirname in _ALWAYS_SKIP or dirname.startswith(".")


def _should_skip_file(filename: str) -> bool:
    if filename in _SKIP_FILES:
        return True
    for ext in _SKIP_EXTENSIONS:
        if filename.endswith(ext):
            return True
    return False


def _matches_exclude(path: str, patterns: tuple[str, ...]) -> bool:
    normalized = path.replace("\\", "/")
    return any(fnmatch(normalized, p) for p in patterns)


def _discover_files(
    root: str,
    language_filter: str | None,
    exclude_patterns: tuple[str, ...],
) -> list[str]:
    # Import here to trigger language registration
    import debtx.languages.python_lang  # noqa: F401
    import debtx.languages.typescript_lang  # noqa: F401

    files: list[str] = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not _should_skip_dir(d)]

        for filename in filenames:
            if _should_skip_file(filename):
                continue

            full_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(full_path, root)

            if exclude_patterns and _matches_exclude(rel_path, exclude_patterns):
                continue

            lang = get_language(filename)
            if lang is None:
                continue

            if language_filter and lang.name != language_filter:
                continue

            files.append(full_path)

    return sorted(files)


def _parse_file(path: str) -> FileContext | None:
    lang = get_language(path)
    if lang is None:
        return None

    try:
        content = Path(path).read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return None

    lines = tuple(content.splitlines())

    if len(lines) > 50000:
        return None

    return lang.parse_file(path, lines)


def run_scan(
    path: str,
    language_filter: str | None = None,
    strict: bool = False,
    exclude_patterns: tuple[str, ...] = (),
    progress_callback: object | None = None,
) -> ScanReport:
    from debtx.detectors import run_all
    from debtx.detectors.no_test_coverage import get_test_coverage_detector

    # Import all detectors to trigger registration
    import debtx.detectors.giant_functions  # noqa: F401
    import debtx.detectors.empty_catches  # noqa: F401
    import debtx.detectors.hardcoded_values  # noqa: F401
    import debtx.detectors.duplicated_blocks  # noqa: F401
    import debtx.detectors.missing_error_handling  # noqa: F401
    import debtx.detectors.orphaned_imports  # noqa: F401
    import debtx.detectors.no_test_coverage  # noqa: F401
    import debtx.detectors.massive_files  # noqa: F401
    import debtx.detectors.todo_comments  # noqa: F401
    import debtx.detectors.inconsistent_naming  # noqa: F401
    import debtx.detectors.deep_nesting  # noqa: F401
    import debtx.detectors.dead_code  # noqa: F401

    root = os.path.abspath(path)
    discovered = _discover_files(root, language_filter, exclude_patterns)

    test_detector = get_test_coverage_detector()
    test_detector.set_all_files(set(discovered))

    file_reports: list[FileReport] = []
    total_lines = 0

    for file_path in discovered:
        context = _parse_file(file_path)
        if context is None:
            continue

        findings = run_all(context, strict)
        ignore_map = build_ignore_map(context.lines, context.language_name)
        findings = apply_inline_ignores(findings, ignore_map)
        rel_path = os.path.relpath(file_path, root)

        file_reports.append(
            FileReport(
                path=rel_path,
                language=context.language_name,
                lines=len(context.lines),
                findings=findings,
            )
        )
        total_lines += len(context.lines)

    reports_tuple = tuple(file_reports)
    category_scores = calculate_category_scores(reports_tuple, strict)
    vibe_score = calculate_vibe_score(category_scores)
    overall_grade = calculate_overall_grade(category_scores)
    total_findings = sum(len(r.findings) for r in reports_tuple)
    summary = build_summary_line(overall_grade, vibe_score, total_findings)

    return ScanReport(
        path=root,
        timestamp=datetime.now(timezone.utc).isoformat(),
        files_scanned=len(reports_tuple),
        total_lines=total_lines,
        file_reports=reports_tuple,
        category_scores=category_scores,
        vibe_score=vibe_score,
        overall_grade=overall_grade,
        summary_line=summary,
    )
