"""Detector registry and runner."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from debtx.languages import FileContext
from debtx.models import Finding


@runtime_checkable
class Detector(Protocol):
    @property
    def detector_id(self) -> str: ...

    @property
    def category_name(self) -> str: ...

    def detect(self, context: FileContext, strict: bool = False) -> tuple[Finding, ...]: ...


_DETECTORS: list[Detector] = []


def register_detector(detector: Detector) -> None:
    _DETECTORS.append(detector)


def get_all_detectors() -> list[Detector]:
    return list(_DETECTORS)


def run_all(context: FileContext, strict: bool = False) -> tuple[Finding, ...]:
    findings: list[Finding] = []
    for detector in _DETECTORS:
        findings.extend(detector.detect(context, strict))
    return tuple(findings)
