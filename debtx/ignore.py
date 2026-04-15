"""Inline ignore directives: drop findings marked with `debtx: ignore` comments.

Supported forms (inside a `#` or `//` comment):

    # debtx: ignore                      → all detectors on this line
    # debtx: ignore[id1, id2]            → specific detectors on this line
    # debtx: ignore-next-line            → all detectors on the next line
    # debtx: ignore-next-line[id]        → specific detector on the next line
"""

from __future__ import annotations

import re

from debtx.detectors._text import comment_portion
from debtx.models import Finding

_DIRECTIVE_RE = re.compile(
    r"\bdebtx\s*:\s*ignore(-next-line)?(?:\[([^\]]*)\])?"
)

_ALL = "*"


def _parse_comment(comment: str) -> tuple[frozenset[str], bool] | None:
    match = _DIRECTIVE_RE.search(comment)
    if not match:
        return None
    next_line = match.group(1) is not None
    inner = match.group(2)
    if inner is None:
        return frozenset({_ALL}), next_line
    ids = frozenset(x.strip() for x in inner.split(",") if x.strip())
    return (ids or frozenset({_ALL})), next_line


def build_ignore_map(lines: tuple[str, ...], lang: str) -> dict[int, frozenset[str]]:
    result: dict[int, frozenset[str]] = {}
    for i, line in enumerate(lines):
        comment = comment_portion(line, lang)
        if not comment:
            continue
        parsed = _parse_comment(comment)
        if parsed is None:
            continue
        ids, next_line = parsed
        target = i + 1 if next_line else i
        existing = result.get(target)
        result[target] = ids if existing is None else existing | ids
    return result


def apply_inline_ignores(
    findings: tuple[Finding, ...],
    ignore_map: dict[int, frozenset[str]],
) -> tuple[Finding, ...]:
    if not ignore_map:
        return findings
    kept: list[Finding] = []
    for finding in findings:
        idx = finding.line - 1
        ids = ignore_map.get(idx)
        if ids and (_ALL in ids or finding.detector in ids):
            continue
        kept.append(finding)
    return tuple(kept)
