"""Detect unreachable code after return, break, continue, raise."""

from __future__ import annotations

from debtx.detectors import register_detector
from debtx.languages import FileContext
from debtx.models import Finding, Severity

_PY_TERMINAL = {"return", "break", "continue", "raise"}
_TS_TERMINAL = {"return", "break", "continue", "throw"}


class DeadCodeDetector:
    @property
    def detector_id(self) -> str:
        return "dead_code"

    @property
    def category_name(self) -> str:
        return "Dead Code"

    def detect(self, context: FileContext, strict: bool = False) -> tuple[Finding, ...]:
        terminal_keywords = (
            _PY_TERMINAL if context.language_name == "python" else _TS_TERMINAL
        )
        findings: list[Finding] = []
        lines = context.lines

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue

            first_word = stripped.split("(")[0].split(" ")[0].rstrip(";")
            if first_word not in terminal_keywords:
                continue

            current_indent = len(line) - len(line.lstrip())

            for j in range(i + 1, min(i + 10, len(lines))):
                next_line = lines[j]
                next_stripped = next_line.strip()

                if not next_stripped:
                    continue

                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent < current_indent:
                    break
                if next_indent > current_indent:
                    break

                if next_indent == current_indent:
                    skip_keywords = {"except", "finally", "elif", "else", "case", "}", "catch"}
                    first_next = next_stripped.split("(")[0].split(" ")[0].split(":")[0]
                    if first_next in skip_keywords:
                        break

                    if context.language_name == "python":
                        if next_stripped.startswith("@"):
                            break
                        if next_stripped.startswith("def ") or next_stripped.startswith("class "):
                            break

                    findings.append(
                        Finding(
                            file_path=context.path,
                            line=j + 1,
                            detector=self.detector_id,
                            message=f"Unreachable code after '{first_word}' on line {i + 1}",
                            severity=Severity.MEDIUM,
                        )
                    )
                    break

        return tuple(findings)


register_detector(DeadCodeDetector())
