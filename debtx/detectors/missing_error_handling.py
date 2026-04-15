"""Detect IO/network operations without error handling."""

from __future__ import annotations

import re

from debtx.detectors import register_detector
from debtx.detectors._text import docstring_line_indices, strip_string_literals
from debtx.languages import FileContext
from debtx.models import Finding, Severity

_PY_IO_PATTERNS = [
    re.compile(r"\bopen\s*\("),
    re.compile(r"\brequests\.\w+\s*\("),
    re.compile(r"\bhttpx\.\w+\s*\("),
    re.compile(r"\burllib\."),
    re.compile(r"\bsubprocess\.\w+\s*\("),
    re.compile(r"\bsocket\."),
    re.compile(r"\baiohttp\."),
]

_TS_IO_PATTERNS = [
    re.compile(r"\bfetch\s*\("),
    re.compile(r"\baxios\.\w+\s*\("),
    re.compile(r"\bfs\.\w+(?:Sync)?\s*\("),
    re.compile(r"\bJSON\.parse\s*\("),
    re.compile(r"\bexecSync\s*\("),
    re.compile(r"\bspawnSync\s*\("),
]


def _is_test_file(path: str) -> bool:
    lower = path.lower().replace("\\", "/")
    return "test" in lower or "spec" in lower


def _line_is_inside_try(lines: tuple[str, ...], line_idx: int, lang: str) -> bool:
    indent = len(lines[line_idx]) - len(lines[line_idx].lstrip())

    for i in range(line_idx - 1, max(line_idx - 30, -1), -1):
        check = lines[i].strip()
        check_indent = len(lines[i]) - len(lines[i].lstrip())

        if check_indent < indent:
            if lang == "python" and check.startswith("try:"):
                return True
            if lang == "typescript" and check.startswith("try"):
                return True

    return False


class MissingErrorHandlingDetector:
    @property
    def detector_id(self) -> str:
        return "missing_error_handling"

    @property
    def category_name(self) -> str:
        return "Missing Error Handling"

    def detect(self, context: FileContext, strict: bool = False) -> tuple[Finding, ...]:
        if _is_test_file(context.path):
            return ()

        patterns = _PY_IO_PATTERNS if context.language_name == "python" else _TS_IO_PATTERNS
        findings: list[Finding] = []
        doc_lines = docstring_line_indices(context.lines, context.language_name)

        for i, line in enumerate(context.lines):
            if i in doc_lines:
                continue

            stripped = line.strip()

            if context.language_name == "python" and stripped.startswith("#"):
                continue
            if context.language_name == "typescript" and stripped.startswith("//"):
                continue

            code = strip_string_literals(stripped)

            for pattern in patterns:
                if pattern.search(code):
                    if not _line_is_inside_try(context.lines, i, context.language_name):
                        findings.append(
                            Finding(
                                file_path=context.path,
                                line=i + 1,
                                detector=self.detector_id,
                                message=f"IO operation without try/except: {stripped[:60]}",
                                severity=Severity.MEDIUM,
                            )
                        )
                    break

        return tuple(findings)


register_detector(MissingErrorHandlingDetector())
