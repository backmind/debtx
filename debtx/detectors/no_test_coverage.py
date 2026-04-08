"""Detect source files with no corresponding test file."""

from __future__ import annotations

import os

from debtx.detectors import register_detector
from debtx.languages import FileContext
from debtx.models import Finding, Severity

_TEST_DIRS = {"test", "tests", "__tests__", "spec"}
_SKIP_FILES = {"__init__", "conftest", "setup", "__main__"}


def _is_test_file(path: str) -> bool:
    lower = os.path.basename(path).lower()
    return (
        lower.startswith("test_")
        or lower.endswith("_test.py")
        or lower.endswith(".test.ts")
        or lower.endswith(".test.tsx")
        or lower.endswith(".test.js")
        or lower.endswith(".test.jsx")
        or lower.endswith(".spec.ts")
        or lower.endswith(".spec.tsx")
        or lower.endswith(".spec.js")
        or lower.endswith(".spec.jsx")
    )


def _is_in_test_dir(path: str) -> bool:
    parts = path.replace("\\", "/").lower().split("/")
    return any(p in _TEST_DIRS for p in parts)


class NoTestCoverageDetector:
    """Operates differently: needs scan-level context to check for test files."""

    def __init__(self) -> None:
        self._all_files: set[str] = set()

    @property
    def detector_id(self) -> str:
        return "no_test_coverage"

    @property
    def category_name(self) -> str:
        return "No Test Coverage"

    def set_all_files(self, files: set[str]) -> None:
        self._all_files = files

    def detect(self, context: FileContext, strict: bool = False) -> tuple[Finding, ...]:
        if _is_test_file(context.path) or _is_in_test_dir(context.path):
            return ()

        basename = os.path.basename(context.path)
        name_without_ext = os.path.splitext(basename)[0]

        if name_without_ext.lower() in _SKIP_FILES:
            return ()

        if len(context.lines) < 10:
            return ()

        test_patterns = [
            f"test_{name_without_ext}",
            f"{name_without_ext}_test",
            f"{name_without_ext}.test",
            f"{name_without_ext}.spec",
        ]

        normalized_files = {os.path.basename(f).lower().split(".")[0] for f in self._all_files}

        for pattern in test_patterns:
            if pattern.lower() in normalized_files:
                return ()

        return (
            Finding(
                file_path=context.path,
                line=1,
                detector=self.detector_id,
                message=f"No test file found for '{basename}'",
                severity=Severity.LOW,
            ),
        )


_instance = NoTestCoverageDetector()
register_detector(_instance)


def get_test_coverage_detector() -> NoTestCoverageDetector:
    return _instance
