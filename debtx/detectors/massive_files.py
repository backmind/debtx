"""Detect files over 500 lines (300 in strict mode)."""

from __future__ import annotations

from debtx.detectors import register_detector
from debtx.languages import FileContext
from debtx.models import Finding, Severity


class MassiveFilesDetector:
    @property
    def detector_id(self) -> str:
        return "massive_files"

    @property
    def category_name(self) -> str:
        return "Massive Files"

    def detect(self, context: FileContext, strict: bool = False) -> tuple[Finding, ...]:
        threshold = 300 if strict else 500
        line_count = len(context.lines)

        if line_count <= threshold:
            return ()

        severity = Severity.HIGH if line_count > 1000 else Severity.MEDIUM

        return (
            Finding(
                file_path=context.path,
                line=1,
                detector=self.detector_id,
                message=f"File is {line_count} lines (threshold: {threshold})",
                severity=severity,
            ),
        )


register_detector(MassiveFilesDetector())
