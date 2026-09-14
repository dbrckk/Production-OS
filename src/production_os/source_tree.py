from __future__ import annotations

from dataclasses import dataclass

TEXT_EXTENSIONS = {
    ".py", ".kt", ".kts", ".java", ".js", ".ts", ".tsx", ".jsx",
    ".go", ".rs", ".cs", ".rb", ".php", ".swift", ".dart", ".gd",
    ".toml", ".yml", ".yaml", ".json", ".xml", ".gradle", ".md",
}

PRIORITY_DIRS = (
    "src", "app", "core", "android", "backend", "studio", "tests", "test",
    "lib", "server", "services", "packages",
)


@dataclass(frozen=True, slots=True)
class TreeSamplePolicy:
    max_depth: int = 3
    max_files: int = 40
    max_chars_per_file: int = 12000


def is_candidate_file(path: str) -> bool:
    lower = path.lower()
    if any(part in lower.split("/") for part in (
        "node_modules", ".git", "build", "dist", ".gradle", ".venv", "venv",
        "vendor", "target", "generated",
    )):
        return False
    if lower.endswith(("lock", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".zip", ".jar", ".aar", ".so")):
        return False
    filename = lower.rsplit("/", 1)[-1]
    if filename in {"dockerfile", "makefile"}:
        return True
    return any(filename.endswith(ext) for ext in TEXT_EXTENSIONS)


def path_priority(path: str) -> tuple[int, int, str]:
    parts = path.lower().split("/")
    top = parts[0] if parts else ""
    priority = PRIORITY_DIRS.index(top) if top in PRIORITY_DIRS else len(PRIORITY_DIRS)
    return (priority, len(parts), path)
