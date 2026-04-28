"""Scoring engine: converts findings into grades and Vibe Score."""

from __future__ import annotations

from collections import defaultdict

from debtx.models import CategoryScore, FileReport, Finding, Severity

CATEGORY_WEIGHTS: dict[str, tuple[str, float]] = {
    "giant_functions": ("Giant Functions", 1.0),
    "empty_catches": ("Empty Catches", 1.2),
    "hardcoded_values": ("Hardcoded Values", 0.8),
    "duplicated_blocks": ("Duplicated Blocks", 1.0),
    "missing_error_handling": ("Missing Error Handling", 1.0),
    "orphaned_imports": ("Orphaned Imports", 0.5),
    "no_test_coverage": ("No Test Coverage", 1.1),
    "massive_files": ("Massive Files", 0.9),
    "todo_comments": ("TODO/FIXME Comments", 0.4),
    "inconsistent_naming": ("Inconsistent Naming", 0.7),
    "deep_nesting": ("Deep Nesting", 0.9),
    "dead_code": ("Dead Code", 0.8),
}

SEVERITY_PENALTY: dict[Severity, float] = {
    Severity.INFO: 0.5,
    Severity.LOW: 1.0,
    Severity.MEDIUM: 2.5,
    Severity.HIGH: 5.0,
    Severity.CRITICAL: 10.0,
}

GRADE_BOUNDARIES: tuple[tuple[str, int], ...] = (
    ("A", 90),
    ("B", 75),
    ("C", 55),
    ("D", 35),
    ("F", 0),
)

GRADE_ORDER: tuple[str, ...] = ("F", "D", "C", "B", "A")


def grade_meets_threshold(actual: str, minimum: str) -> bool:
    """True iff `actual` is at least as good as `minimum` on A>B>C>D>F."""
    if actual not in GRADE_ORDER or minimum not in GRADE_ORDER:
        raise ValueError(
            f"Unknown grade(s): actual={actual!r} minimum={minimum!r}"
        )
    return GRADE_ORDER.index(actual) >= GRADE_ORDER.index(minimum)


def score_to_grade(score: float) -> str:
    for grade, threshold in GRADE_BOUNDARIES:
        if score >= threshold:
            return grade
    return "F"


def _group_findings_by_detector(
    file_reports: tuple[FileReport, ...],
) -> dict[str, list[Finding]]:
    grouped: dict[str, list[Finding]] = defaultdict(list)
    for report in file_reports:
        for finding in report.findings:
            grouped[finding.detector].append(finding)
    return grouped


def _calculate_category_score(
    findings: list[Finding],
    total_files: int,
    strict: bool = False,
) -> float:
    if total_files == 0:
        return 100.0

    total_penalty = sum(SEVERITY_PENALTY[f.severity] for f in findings)
    penalty_per_file = total_penalty / max(total_files, 1)
    raw_score = max(0.0, 100.0 - (penalty_per_file * 10))

    if strict:
        raw_score = max(0.0, raw_score - 10)

    return round(raw_score, 1)


def calculate_category_scores(
    file_reports: tuple[FileReport, ...],
    strict: bool = False,
) -> tuple[CategoryScore, ...]:
    grouped = _group_findings_by_detector(file_reports)
    total_files = len(file_reports)
    scores: list[CategoryScore] = []

    for detector_id, (name, weight) in CATEGORY_WEIGHTS.items():
        findings = grouped.get(detector_id, [])
        raw_score = _calculate_category_score(findings, total_files, strict)
        effective_weight = weight * 1.3 if strict else weight

        scores.append(
            CategoryScore(
                name=name,
                detector_id=detector_id,
                grade=score_to_grade(raw_score),
                score=raw_score,
                finding_count=len(findings),
                weight=effective_weight,
            )
        )

    return tuple(scores)


def calculate_vibe_score(
    category_scores: tuple[CategoryScore, ...],
) -> int:
    if not category_scores:
        return 100

    total_weight = sum(cs.weight for cs in category_scores)
    if total_weight == 0:
        return 100

    weighted_sum = sum(cs.score * cs.weight for cs in category_scores)
    raw = weighted_sum / total_weight

    return max(0, min(100, round(raw)))


def build_summary_line(
    overall_grade: str,
    vibe_score: int,
    total_findings: int,
) -> str:
    issue_word = "issue" if total_findings == 1 else "issues"
    return f"debtx: {overall_grade} | Vibe Score: {vibe_score}/100 | {total_findings} {issue_word} found"


def calculate_overall_grade(category_scores: tuple[CategoryScore, ...]) -> str:
    if not category_scores:
        return "A"

    vibe = calculate_vibe_score(category_scores)
    return score_to_grade(vibe)
