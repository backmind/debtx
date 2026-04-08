"""Detect unused imports."""

from __future__ import annotations

from debtx.detectors import register_detector
from debtx.languages import FileContext
from debtx.models import Finding, Severity


class OrphanedImportsDetector:
    @property
    def detector_id(self) -> str:
        return "orphaned_imports"

    @property
    def category_name(self) -> str:
        return "Orphaned Imports"

    def detect(self, context: FileContext, strict: bool = False) -> tuple[Finding, ...]:
        findings: list[Finding] = []

        non_import_content = ""
        for i, line in enumerate(context.lines):
            stripped = line.strip()
            if context.language_name == "python":
                if stripped.startswith("import ") or stripped.startswith("from "):
                    continue
            elif context.language_name == "typescript":
                if stripped.startswith("import ") or "require(" in stripped:
                    continue
            non_import_content += stripped + "\n"

        for imp in context.imports:
            for name in imp.names:
                if not name or name == "*":
                    continue
                clean_name = name.strip("()")
                if not clean_name:
                    continue
                if clean_name == "annotations":
                    continue

                if clean_name not in non_import_content:
                    findings.append(
                        Finding(
                            file_path=context.path,
                            line=imp.line + 1,
                            detector=self.detector_id,
                            message=f"Unused import: '{clean_name}'",
                            severity=Severity.LOW,
                        )
                    )

        return tuple(findings)


register_detector(OrphanedImportsDetector())
