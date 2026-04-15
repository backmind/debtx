"""Detect TODO, FIXME, HACK, and other marker comments."""

from __future__ import annotations

import re

from debtx.detectors import register_detector
from debtx.detectors._text import comment_portion, docstring_line_indices
from debtx.languages import FileContext
from debtx.models import Finding, Severity

_MARKERS = {
    "TODO": Severity.INFO,
    "FIXME": Severity.LOW,
    "HACK": Severity.LOW,
    "XXX": Severity.MEDIUM,
}

_MARKER_RE = re.compile(r"\b(" + "|".join(_MARKERS.keys()) + r")\b(?=[\s:\-(]|$)")


class TodoCommentsDetector:
    @property
    def detector_id(self) -> str:
        return "todo_comments"

    @property
    def category_name(self) -> str:
        return "TODO/FIXME Comments"

    def detect(self, context: FileContext, strict: bool = False) -> tuple[Finding, ...]:
        findings: list[Finding] = []
        doc_lines = docstring_line_indices(context.lines, context.language_name)

        for i, line in enumerate(context.lines):
            if i in doc_lines:
                continue

            comment = comment_portion(line, context.language_name)
            if not comment:
                continue

            match = _MARKER_RE.search(comment)
            if not match:
                continue

            marker = match.group(1)
            severity = _MARKERS[marker]
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
