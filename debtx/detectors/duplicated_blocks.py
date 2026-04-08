"""Detect duplicated code blocks within a file."""

from __future__ import annotations

from debtx.detectors import register_detector
from debtx.languages import FileContext
from debtx.models import Finding, Severity

MIN_BLOCK_SIZE = 6


def _normalize_line(line: str) -> str:
    return line.strip().lower()


class DuplicatedBlocksDetector:
    @property
    def detector_id(self) -> str:
        return "duplicated_blocks"

    @property
    def category_name(self) -> str:
        return "Duplicated Blocks"

    def detect(self, context: FileContext, strict: bool = False) -> tuple[Finding, ...]:
        block_size = 5 if strict else MIN_BLOCK_SIZE
        lines = context.lines

        if len(lines) < block_size * 2:
            return ()

        normalized = tuple(_normalize_line(line) for line in lines)
        findings: list[Finding] = []
        reported_lines: set[int] = set()

        seen_blocks: dict[tuple[str, ...], int] = {}

        for i in range(len(normalized) - block_size + 1):
            block = tuple(normalized[i : i + block_size])

            if all(not b for b in block):
                continue

            non_empty = sum(1 for b in block if b)
            if non_empty < block_size // 2:
                continue

            if block in seen_blocks:
                original = seen_blocks[block]
                if i not in reported_lines and original not in reported_lines:
                    findings.append(
                        Finding(
                            file_path=context.path,
                            line=i + 1,
                            end_line=i + block_size,
                            detector=self.detector_id,
                            message=(
                                f"Duplicated block ({block_size} lines), "
                                f"same as line {original + 1}"
                            ),
                            severity=Severity.MEDIUM,
                        )
                    )
                    reported_lines.add(i)
                    reported_lines.add(original)
            else:
                seen_blocks[block] = i

        return tuple(findings)


register_detector(DuplicatedBlocksDetector())
