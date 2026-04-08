"""Immutable data models for debtx scan results."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import NamedTuple


class Severity(IntEnum):
    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


class FunctionSpan(NamedTuple):
    name: str
    start: int
    end: int
    indent: int


class ImportInfo(NamedTuple):
    module: str
    names: tuple[str, ...]
    line: int


@dataclass(frozen=True)
class Finding:
    file_path: str
    line: int
    detector: str
    message: str
    severity: Severity
    end_line: int | None = None
    context: str = ""


@dataclass(frozen=True)
class FileReport:
    path: str
    language: str
    lines: int
    findings: tuple[Finding, ...]


@dataclass(frozen=True)
class CategoryScore:
    name: str
    detector_id: str
    grade: str
    score: float
    finding_count: int
    weight: float


@dataclass(frozen=True)
class ScanReport:
    path: str
    timestamp: str
    files_scanned: int
    total_lines: int
    file_reports: tuple[FileReport, ...]
    category_scores: tuple[CategoryScore, ...]
    vibe_score: int
    overall_grade: str
    summary_line: str
