"""Detect deeply nested code (4+ levels of indentation)."""

from __future__ import annotations

from debtx.detectors import register_detector
from debtx.languages import FileContext
from debtx.models import Finding, Severity


class DeepNestingDetector:
    @property
    def detector_id(self) -> str:
        return "deep_nesting"

    @property
    def category_name(self) -> str:
        return "Deep Nesting"

    def detect(self, context: FileContext, strict: bool = False) -> tuple[Finding, ...]:
        threshold = 4 if strict else 5
        findings: list[Finding] = []
        reported_ranges: list[tuple[int, int]] = []

        for i, line in enumerate(context.lines):
            if not line.strip():
                continue

            if context.language_name == "python":
                spaces = len(line) - len(line.lstrip())
                level = spaces // 4
            else:
                spaces = len(line) - len(line.lstrip())
                level = spaces // 2

            if level >= threshold:
                already_reported = any(start <= i <= end for start, end in reported_ranges)
                if already_reported:
                    continue

                end_line = i
                for j in range(i + 1, min(i + 20, len(context.lines))):
                    next_line = context.lines[j]
                    if not next_line.strip():
                        continue
                    next_spaces = len(next_line) - len(next_line.lstrip())
                    next_level = next_spaces // (4 if context.language_name == "python" else 2)
                    if next_level >= threshold:
                        end_line = j
                    else:
                        break

                reported_ranges.append((i, end_line))
                severity = Severity.HIGH if level >= 5 else Severity.MEDIUM

                findings.append(
                    Finding(
                        file_path=context.path,
                        line=i + 1,
                        end_line=end_line + 1,
                        detector=self.detector_id,
                        message=f"Nesting level {level} (threshold: {threshold})",
                        severity=severity,
                    )
                )

        return tuple(findings)


register_detector(DeepNestingDetector())
