from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .migrations import migrate_state_file


@dataclass(frozen=True, slots=True)
class MigrationResult:
    path: str
    migrated: bool
    source_schema: str
    target_schema: str

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "migrated": self.migrated,
            "source_schema": self.source_schema,
            "target_schema": self.target_schema,
        }


def migrate_many(paths: list[str]) -> list[MigrationResult]:
    results = []
    for raw in paths:
        result = migrate_state_file(raw)
        results.append(
            MigrationResult(
                path=str(Path(raw)),
                migrated=bool(result.get("migrated")),
                source_schema=str(result.get("from", "")),
                target_schema=str(result.get("to", "")),
            )
        )
    return results
