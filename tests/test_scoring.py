"""Tests for scoring engine."""

import pytest

from debtx.models import FileReport, Finding, Severity
from debtx.scoring import (
    build_summary_line,
    calculate_category_scores,
    calculate_overall_grade,
    calculate_vibe_score,
    grade_meets_threshold,
    score_to_grade,
)


def test_score_to_grade_boundaries():
    assert score_to_grade(100) == "A"
    assert score_to_grade(90) == "A"
    assert score_to_grade(89) == "B"
    assert score_to_grade(75) == "B"
    assert score_to_grade(74) == "C"
    assert score_to_grade(55) == "C"
    assert score_to_grade(54) == "D"
    assert score_to_grade(35) == "D"
    assert score_to_grade(34) == "F"
    assert score_to_grade(0) == "F"


def test_vibe_score_empty():
    assert calculate_vibe_score(()) == 100


def test_vibe_score_clamped():
    score = calculate_vibe_score(())
    assert 0 <= score <= 100


def test_summary_line_singular():
    line = build_summary_line("A", 95, 1)
    assert "1 issue found" in line


def test_summary_line_plural():
    line = build_summary_line("C", 60, 42)
    assert "42 issues found" in line
    assert "debtx: C" in line
    assert "Vibe Score: 60/100" in line


def test_category_scores_no_findings():
    reports = (FileReport(path="a.py", language="python", lines=50, findings=()),)
    scores = calculate_category_scores(reports)
    assert len(scores) > 0
    for cs in scores:
        assert cs.grade == "A"
        assert cs.finding_count == 0


def test_category_scores_with_findings():
    findings = (
        Finding(
            file_path="a.py",
            line=1,
            detector="giant_functions",
            message="too long",
            severity=Severity.HIGH,
        ),
    )
    reports = (FileReport(path="a.py", language="python", lines=50, findings=findings),)
    scores = calculate_category_scores(reports)
    giant = next(cs for cs in scores if cs.detector_id == "giant_functions")
    assert giant.finding_count == 1
    assert giant.score < 100


def test_overall_grade_empty():
    assert calculate_overall_grade(()) == "A"


def test_grade_meets_threshold_equal():
    assert grade_meets_threshold("A", "A") is True


def test_grade_meets_threshold_better():
    assert grade_meets_threshold("A", "C") is True


def test_grade_meets_threshold_worse():
    assert grade_meets_threshold("C", "A") is False


def test_grade_meets_threshold_floor_passes_anything():
    for g in ("A", "B", "C", "D", "F"):
        assert grade_meets_threshold(g, "F") is True


def test_grade_meets_threshold_unknown_grade():
    with pytest.raises(ValueError):
        grade_meets_threshold("Z", "A")
    with pytest.raises(ValueError):
        grade_meets_threshold("A", "z")


def test_strict_mode_lowers_scores():
    findings = (
        Finding(
            file_path="a.py",
            line=1,
            detector="empty_catches",
            message="empty catch",
            severity=Severity.HIGH,
        ),
    )
    reports = (FileReport(path="a.py", language="python", lines=50, findings=findings),)
    normal = calculate_category_scores(reports, strict=False)
    strict = calculate_category_scores(reports, strict=True)

    normal_catch = next(cs for cs in normal if cs.detector_id == "empty_catches")
    strict_catch = next(cs for cs in strict if cs.detector_id == "empty_catches")
    assert strict_catch.score <= normal_catch.score
