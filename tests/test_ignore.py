"""Tests for inline ignore directives."""

import os
import tempfile

from debtx.ignore import apply_inline_ignores, build_ignore_map
from debtx.models import Finding, Severity
from debtx.scanner import run_scan


def _finding(line: int, detector: str) -> Finding:
    return Finding(
        file_path="x.py",
        line=line,
        detector=detector,
        message="...",
        severity=Severity.HIGH,
    )


def test_build_ignore_map_all_detectors():
    lines = ("x = 1  # debtx: ignore", "y = 2")
    result = build_ignore_map(lines, "python")
    assert result == {0: frozenset({"*"})}


def test_build_ignore_map_specific_detector():
    lines = ("x = 1  # debtx: ignore[dead_code]",)
    result = build_ignore_map(lines, "python")
    assert result == {0: frozenset({"dead_code"})}


def test_build_ignore_map_multiple_detectors():
    lines = ("x = 1  # debtx: ignore[dead_code, empty_catches]",)
    result = build_ignore_map(lines, "python")
    assert result == {0: frozenset({"dead_code", "empty_catches"})}


def test_build_ignore_map_typescript():
    lines = ("const x = 1; // debtx: ignore[hardcoded_values]",)
    result = build_ignore_map(lines, "typescript")
    assert result == {0: frozenset({"hardcoded_values"})}


def test_directive_in_string_literal_ignored():
    lines = ('msg = "debtx: ignore[dead_code]"',)
    result = build_ignore_map(lines, "python")
    assert result == {}


def test_apply_filters_matching_detector():
    findings = (_finding(1, "dead_code"), _finding(2, "dead_code"))
    ignores = {0: frozenset({"dead_code"})}
    kept = apply_inline_ignores(findings, ignores)
    assert len(kept) == 1
    assert kept[0].line == 2


def test_apply_wildcard_filters_all():
    findings = (_finding(1, "dead_code"), _finding(1, "empty_catches"))
    ignores = {0: frozenset({"*"})}
    kept = apply_inline_ignores(findings, ignores)
    assert kept == ()


def test_apply_specific_does_not_filter_others():
    findings = (_finding(1, "dead_code"), _finding(1, "empty_catches"))
    ignores = {0: frozenset({"dead_code"})}
    kept = apply_inline_ignores(findings, ignores)
    assert len(kept) == 1
    assert kept[0].detector == "empty_catches"


def test_apply_no_ignores_is_noop():
    findings = (_finding(1, "dead_code"),)
    assert apply_inline_ignores(findings, {}) == findings


def test_end_to_end_scan_respects_inline_ignore():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "app.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(
                "def f():\n"
                "    try:\n"
                "        do_thing()\n"
                "    except Exception:  # debtx: ignore[empty_catches]\n"
                "        pass\n"
            )
        report = run_scan(tmp)
        all_findings = [fi for fr in report.file_reports for fi in fr.findings]
        assert not any(f.detector == "empty_catches" for f in all_findings)


def test_ignore_next_line_directive():
    lines = ("# debtx: ignore-next-line[dead_code]", "x = 2")
    result = build_ignore_map(lines, "python")
    assert result == {1: frozenset({"dead_code"})}


def test_ignore_next_line_applies_to_following_finding():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "app.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(
                "def f():\n"
                "    return 1\n"
                "    # debtx: ignore-next-line[dead_code]\n"
                "    x = 2\n"
            )
        report = run_scan(tmp)
        detectors = [
            fi.detector for fr in report.file_reports for fi in fr.findings
        ]
        assert "dead_code" not in detectors
