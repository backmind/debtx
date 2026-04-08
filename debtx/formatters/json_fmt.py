"""JSON report formatter."""

from __future__ import annotations

import json
from dataclasses import asdict

from debtx.models import ScanReport


def _serialize(obj: object) -> object:
    if hasattr(obj, "value"):
        return obj.value
    if hasattr(obj, "_asdict"):
        return obj._asdict()
    return str(obj)


def render_json(report: ScanReport) -> str:
    data = asdict(report)
    return json.dumps(data, indent=2, default=_serialize)
