"""Shared text utilities for detectors: string-literal stripping and docstring detection."""

from __future__ import annotations


def docstring_line_indices(lines: tuple[str, ...], lang: str) -> frozenset[int]:
    result: set[int] = set()

    if lang == "python":
        in_doc = False
        quote: str | None = None
        for i, line in enumerate(lines):
            if in_doc:
                result.add(i)
                if quote and quote in line:
                    in_doc = False
                    quote = None
                continue

            rest = line
            while True:
                idx_dq = rest.find('"""')
                idx_sq = rest.find("'''")
                candidates = [x for x in (idx_dq, idx_sq) if x != -1]
                if not candidates:
                    break
                idx = min(candidates)
                q = '"""' if idx == idx_dq else "'''"
                after = rest[idx + 3 :]
                close = after.find(q)
                result.add(i)
                if close == -1:
                    in_doc = True
                    quote = q
                    break
                rest = after[close + 3 :]

    elif lang == "typescript":
        in_block = False
        for i, line in enumerate(lines):
            if in_block:
                result.add(i)
                if "*/" in line:
                    in_block = False
                continue
            start = line.find("/*")
            if start != -1 and "*/" not in line[start + 2 :]:
                in_block = True
                result.add(i)

    return frozenset(result)


def strip_string_literals(line: str) -> str:
    out: list[str] = []
    i = 0
    n = len(line)
    while i < n:
        c = line[i]
        if c in ('"', "'", "`"):
            j = i + 1
            while j < n:
                if line[j] == "\\":
                    j += 2
                    continue
                if line[j] == c:
                    j += 1
                    break
                j += 1
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)
