"""Detect empty except/catch blocks."""

from __future__ import annotations

from debtx.detectors import register_detector
from debtx.languages import FileContext
from debtx.models import Finding, Severity


class EmptyCatchesDetector:
    @property
    def detector_id(self) -> str:
        return "empty_catches"

    @property
    def category_name(self) -> str:
        return "Empty Catches"

    def detect(self, context: FileContext, strict: bool = False) -> tuple[Finding, ...]:
        if context.language_name == "python":
            return self._detect_python(context)
        return self._detect_typescript(context)

    def _detect_python(self, context: FileContext) -> tuple[Finding, ...]:
        findings: list[Finding] = []
        lines = context.lines

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped.startswith("except"):
                continue

            for j in range(i + 1, min(i + 5, len(lines))):
                next_line = lines[j].strip()
                if not next_line:
                    continue
                if next_line.startswith("#"):
                    continue
                if next_line == "pass":
                    findings.append(
                        Finding(
                            file_path=context.path,
                            line=i + 1,
                            detector="empty_catches",
                            message="Empty except block (only 'pass')",
                            severity=Severity.HIGH,
                        )
                    )
                break

        return tuple(findings)

    def _detect_typescript(self, context: FileContext) -> tuple[Finding, ...]:
        findings: list[Finding] = []
        lines = context.lines

        for i, line in enumerate(lines):
            stripped = line.strip()
            if "catch" not in stripped:
                continue
            if not any(p in stripped for p in ["catch(", "catch ("]):
                continue

            for j in range(i, min(i + 3, len(lines))):
                current = lines[j].strip()
                if "{}" in current or current == "}":
                    if j == i or (j == i + 1 and lines[j].strip() == "}"):
                        findings.append(
                            Finding(
                                file_path=context.path,
                                line=i + 1,
                                detector="empty_catches",
                                message="Empty catch block",
                                severity=Severity.HIGH,
                            )
                        )
                    break

        return tuple(findings)


register_detector(EmptyCatchesDetector())
