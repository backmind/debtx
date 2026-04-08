"""Detect inconsistent naming conventions (e.g., mixing camelCase and snake_case)."""

from __future__ import annotations

import re

from debtx.detectors import register_detector
from debtx.languages import FileContext
from debtx.models import Finding, Severity

_PY_DEF_RE = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)")
_TS_FUNC_RE = re.compile(
    r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)"
    r"|^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*="
)
_SKIP_NAMES = {"__init__", "__main__", "__all__", "__str__", "__repr__", "__eq__", "__hash__"}


class InconsistentNamingDetector:
    @property
    def detector_id(self) -> str:
        return "inconsistent_naming"

    @property
    def category_name(self) -> str:
        return "Inconsistent Naming"

    def detect(self, context: FileContext, strict: bool = False) -> tuple[Finding, ...]:
        if context.language_name == "python":
            return self._detect_python(context)
        return self._detect_typescript(context)

    def _detect_python(self, context: FileContext) -> tuple[Finding, ...]:
        findings: list[Finding] = []

        for func in context.functions:
            name = func.name
            if name.startswith("_") and name.endswith("_"):
                continue
            if name in _SKIP_NAMES:
                continue

            if re.match(r"^[a-z][a-zA-Z0-9]*$", name) and re.search(r"[A-Z]", name):
                findings.append(
                    Finding(
                        file_path=context.path,
                        line=func.start + 1,
                        detector=self.detector_id,
                        message=f"Function '{name}' uses camelCase (expected snake_case in Python)",
                        severity=Severity.LOW,
                    )
                )

        return tuple(findings)

    def _detect_typescript(self, context: FileContext) -> tuple[Finding, ...]:
        findings: list[Finding] = []

        for func in context.functions:
            name = func.name
            if name.startswith("_"):
                continue

            if re.match(r"^[a-z_][a-z0-9_]*$", name) and "_" in name:
                findings.append(
                    Finding(
                        file_path=context.path,
                        line=func.start + 1,
                        detector=self.detector_id,
                        message=(
                            f"Function '{name}' uses snake_case "
                            "(expected camelCase in TypeScript)"
                        ),
                        severity=Severity.LOW,
                    )
                )

        return tuple(findings)


register_detector(InconsistentNamingDetector())
