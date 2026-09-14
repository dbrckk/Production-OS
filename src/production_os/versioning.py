from __future__ import annotations

import re
from dataclasses import dataclass

from .models import RepoAssessment


@dataclass(frozen=True, slots=True)
class VersionCompatibility:
    dependency: str
    source_version: str | None
    target_version: str | None
    status: str
    confidence: float

    def to_dict(self) -> dict:
        return {
            "dependency": self.dependency,
            "source_version": self.source_version,
            "target_version": self.target_version,
            "status": self.status,
            "confidence": self.confidence,
        }


def _extract_versions(assessment: RepoAssessment) -> dict[str, str]:
    versions: dict[str, str] = {}
    combined = "\\n".join(assessment.evidence.source_documents.values())

    patterns = [
        re.compile(r'["\']([A-Za-z0-9_.-]+):([A-Za-z0-9_.-]+):([0-9][A-Za-z0-9_.+-]*)["\']'),
        re.compile(r'(?m)^\\s*([A-Za-z0-9_.-]+)\\s*(?:==|>=|~=|\\^|=)\\s*([0-9][A-Za-z0-9_.+-]*)\\s*
    ]

    for pattern in patterns:
        for match in pattern.finditer(combined):
            groups = match.groups()
            if len(groups) == 3:
                key = f"{groups[0]}:{groups[1]}".lower()
                version = groups[2]
            else:
                key = groups[0].lower()
                version = groups[1]
            versions[key] = version

    return versions


def compare_dependency_versions(
    source: RepoAssessment,
    target: RepoAssessment,
) -> list[VersionCompatibility]:
    source_versions = _extract_versions(source)
    target_versions = _extract_versions(target)
    results: list[VersionCompatibility] = []

    for dep, source_version in sorted(source_versions.items()):
        target_version = target_versions.get(dep)
        if target_version is None:
            status = "not-present-in-target"
            confidence = 0.92
        elif target_version == source_version:
            status = "exact-match"
            confidence = 0.99
        else:
            source_major = source_version.split(".", 1)[0]
            target_major = target_version.split(".", 1)[0]
            if source_major == target_major:
                status = "same-major-review-required"
                confidence = 0.85
            else:
                status = "major-version-mismatch"
                confidence = 0.95

        results.append(
            VersionCompatibility(
                dependency=dep,
                source_version=source_version,
                target_version=target_version,
                status=status,
                confidence=confidence,
            )
        )

    return results
),
    ]

    for pattern in patterns:
        for match in pattern.finditer(combined):
            groups = match.groups()
            if len(groups) == 3:
                key = f"{groups[0]}:{groups[1]}".lower()
                version = groups[2]
            else:
                key = groups[0].lower()
                version = groups[1]
            versions[key] = version

    return versions


def compare_dependency_versions(
    source: RepoAssessment,
    target: RepoAssessment,
) -> list[VersionCompatibility]:
    source_versions = _extract_versions(source)
    target_versions = _extract_versions(target)
    results: list[VersionCompatibility] = []

    for dep, source_version in sorted(source_versions.items()):
        target_version = target_versions.get(dep)
        if target_version is None:
            status = "not-present-in-target"
            confidence = 0.92
        elif target_version == source_version:
            status = "exact-match"
            confidence = 0.99
        else:
            source_major = source_version.split(".", 1)[0]
            target_major = target_version.split(".", 1)[0]
            if source_major == target_major:
                status = "same-major-review-required"
                confidence = 0.85
            else:
                status = "major-version-mismatch"
                confidence = 0.95

        results.append(
            VersionCompatibility(
                dependency=dep,
                source_version=source_version,
                target_version=target_version,
                status=status,
                confidence=confidence,
            )
        )

    return results
