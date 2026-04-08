"""Detect TODO, FIXME, HACK, and other marker comments."""

from __future__ import annotations

import re

from debtx.detectors import register_detector
from debtx.languages import FileContext
from debtx.models import Finding, Severity

_MARKERS = {
    "TODO": Severity.INFO,
    "FIXME": Severity.LOW,
    "HACK": Severity.LOW,
    "XXX": Severity.MEDIUM,
    "TEMP": Severity.MEDIUM,
    "WORKAROUND": Severity.LOW,
}

_MARKER_RE = re.compile(r"\b(" + "|".join(_MARKERS.keys()) + r")\b", re.IGNORECASE)


class TodoCommentsDetector:
    @property
    def detector_id(self) -> str:
        return "todo_comments"

    @property
    def category_name(self) -> str:
        return "TODO/FIXME Comments"

    def detect(self, context: FileContext, strict: bool = False) -> tuple[Finding, ...]:
        findings: list[Finding] = []

        for i, line in enumerate(context.lines):
            match = _MARKER_RE.search(line)
            if match:
                marker = match.group(1).upper()
                severity = _MARKERS.get(marker, Severity.INFO)
                findings.append(
                    Finding(
                        file_path=context.path,
                        line=i + 1,
                        detector=self.detector_id,
                        message=f"{marker} comment: {line.strip()[:80]}",
                        severity=severity,
                    )
                )

        return tuple(findings)


register_detector(TodoCommentsDetector())
