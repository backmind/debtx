"""Tests for data models."""

import pytest

from debtx.models import CategoryScore, FileReport, Finding, ScanReport, Severity


def test_severity_ordering():
    assert Severity.INFO < Severity.LOW < Severity.MEDIUM < Severity.HIGH < Severity.CRITICAL


def test_finding_frozen():
    f = Finding(file_path="test.py", line=1, detector="test", message="msg", severity=Severity.LOW)
    with pytest.raises(AttributeError):
        f.line = 2  # type: ignore[misc]


def test_finding_defaults():
    f = Finding(file_path="test.py", line=1, detector="test", message="msg", severity=Severity.LOW)
    assert f.end_line is None
    assert f.context == ""


def test_file_report_frozen():
    fr = FileReport(path="test.py", language="python", lines=10, findings=())
    with pytest.raises(AttributeError):
        fr.lines = 20  # type: ignore[misc]


def test_scan_report_creation():
    report = ScanReport(
        path="/test",
        timestamp="2026-01-01T00:00:00Z",
        files_scanned=5,
        total_lines=100,
        file_reports=(),
        category_scores=(),
        vibe_score=85,
        overall_grade="B",
        summary_line="debtx: B | Vibe Score: 85/100 | 0 issues found",
    )
    assert report.overall_grade == "B"
    assert report.vibe_score == 85
