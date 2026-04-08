"""Detect hardcoded URLs, IPs, ports, magic numbers, and potential secrets."""

from __future__ import annotations

import re

from debtx.detectors import register_detector
from debtx.languages import FileContext
from debtx.models import Finding, Severity

_URL_RE = re.compile(r'https?://[^\s\'"`,)}\]]+')
_IP_RE = re.compile(r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b")
_SECRET_RE = re.compile(
    r"""(?:api[_-]?key|secret|password|token|auth)\s*[:=]\s*['"][^'"]{8,}['"]""",
    re.IGNORECASE,
)
_MAGIC_NUM_RE = re.compile(r"(?<![a-zA-Z_.\d])(\d{4,})(?![a-zA-Z_\d])")

_SAFE_IPS = {"127.0.0.1", "0.0.0.0", "255.255.255.255", "255.255.255.0"}
_SAFE_URLS = {"localhost", "example.com", "127.0.0.1", "0.0.0.0", "schemas."}
_SAFE_NUMBERS = {
    "1000", "1024", "2048", "4096", "8080", "8000", "3000", "5000",
    "65535", "9999", "10000", "100000", "1000000",
}


def _is_test_file(path: str) -> bool:
    lower = path.lower().replace("\\", "/")
    return "test" in lower or "spec" in lower or "fixture" in lower


class HardcodedValuesDetector:
    @property
    def detector_id(self) -> str:
        return "hardcoded_values"

    @property
    def category_name(self) -> str:
        return "Hardcoded Values"

    def detect(self, context: FileContext, strict: bool = False) -> tuple[Finding, ...]:
        if _is_test_file(context.path):
            return ()

        findings: list[Finding] = []
        lang = context.language_name

        for i, line in enumerate(context.lines):
            stripped = line.strip()

            if lang == "python" and stripped.startswith("#"):
                continue
            if lang == "typescript" and (stripped.startswith("//") or stripped.startswith("*")):
                continue

            for url_match in _URL_RE.finditer(stripped):
                url = url_match.group()
                if any(safe in url for safe in _SAFE_URLS):
                    continue
                findings.append(
                    Finding(
                        file_path=context.path,
                        line=i + 1,
                        detector=self.detector_id,
                        message=f"Hardcoded URL: {url[:60]}",
                        severity=Severity.MEDIUM,
                    )
                )

            for ip_match in _IP_RE.finditer(stripped):
                ip = ip_match.group(1)
                if ip in _SAFE_IPS:
                    continue
                findings.append(
                    Finding(
                        file_path=context.path,
                        line=i + 1,
                        detector=self.detector_id,
                        message=f"Hardcoded IP: {ip}",
                        severity=Severity.MEDIUM,
                    )
                )

            if _SECRET_RE.search(stripped):
                findings.append(
                    Finding(
                        file_path=context.path,
                        line=i + 1,
                        detector=self.detector_id,
                        message="Possible hardcoded secret or API key",
                        severity=Severity.CRITICAL,
                    )
                )

            if strict:
                for num_match in _MAGIC_NUM_RE.finditer(stripped):
                    num = num_match.group(1)
                    if num in _SAFE_NUMBERS:
                        continue
                    upper_line = stripped.split("=")[0].strip() if "=" in stripped else ""
                    if upper_line == upper_line.upper() and upper_line.replace("_", "").isalpha():
                        continue
                    findings.append(
                        Finding(
                            file_path=context.path,
                            line=i + 1,
                            detector=self.detector_id,
                            message=f"Magic number: {num}",
                            severity=Severity.LOW,
                        )
                    )

        return tuple(findings)


register_detector(HardcodedValuesDetector())
