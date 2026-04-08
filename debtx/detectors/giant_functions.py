"""Detect functions over 100 lines (50 in strict mode)."""

from __future__ import annotations

from debtx.detectors import register_detector
from debtx.languages import FileContext
from debtx.models import Finding, Severity


class GiantFunctionsDetector:
    @property
    def detector_id(self) -> str:
        return "giant_functions"

    @property
    def category_name(self) -> str:
        return "Giant Functions"

    def detect(self, context: FileContext, strict: bool = False) -> tuple[Finding, ...]:
        threshold = 50 if strict else 100
        findings: list[Finding] = []

        for func in context.functions:
            length = func.end - func.start + 1
            if length > threshold:
                severity = Severity.CRITICAL if length > 200 else Severity.HIGH
                findings.append(
                    Finding(
                        file_path=context.path,
                        line=func.start + 1,
                        end_line=func.end + 1,
                        detector=self.detector_id,
                        message=f"Function '{func.name}' is {length} lines (threshold: {threshold})",
                        severity=severity,
                    )
                )

        return tuple(findings)


register_detector(GiantFunctionsDetector())
