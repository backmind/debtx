"""Detect TODO, FIXME, HACK, and other marker comments."""

from __future__ import annotations

import re

from debtx.detectors import register_detector
from debtx.detectors._text import docstring_line_indices
from debtx.languages import FileContext
from debtx.models import Finding, Severity

_MARKERS = {
    "TODO": Severity.INFO,
    "FIXME": Severity.LOW,
    "HACK": Severity.LOW,
    "XXX": Severity.MEDIUM,
}

_MARKER_RE = re.compile(r"\b(" + "|".join(_MARKERS.keys()) + r")\b(?=[\s:\-(]|$)")


def _comment_portion(line: str, lang: str) -> str:
    if lang == "python":
        in_string: str | None = None
        i = 0
        n = len(line)
        while i < n:
            c = line[i]
            if in_string:
                if c == "\\":
                    i += 2
                    continue
                if c == in_string:
                    in_string = None
                i += 1
                continue
            if c in ('"', "'"):
                in_string = c
                i += 1
                continue
            if c == "#":
                return line[i:]
            i += 1
        return ""

    if lang == "typescript":
        in_string: str | None = None
        i = 0
        n = len(line)
        while i < n:
            c = line[i]
            if in_string:
                if c == "\\":
                    i += 2
                    continue
                if c == in_string:
                    in_string = None
                i += 1
                continue
            if c in ('"', "'", "`"):
                in_string = c
                i += 1
                continue
            if c == "/" and i + 1 < n and line[i + 1] == "/":
                return line[i:]
            i += 1
        return ""

    return ""


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

            comment = _comment_portion(line, context.language_name)
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
