from __future__ import annotations

import ast
import re
from dataclasses import dataclass

from .models import RepoEvidence


@dataclass(frozen=True, slots=True)
class Component:
    name: str
    kind: str
    path: str
    language: str
    confidence: float
    dependencies: tuple[str, ...] = ()
    capability_hints: tuple[str, ...] = ()
    test_like: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "kind": self.kind,
            "path": self.path,
            "language": self.language,
            "confidence": self.confidence,
            "dependencies": list(self.dependencies),
            "capability_hints": list(self.capability_hints),
            "test_like": self.test_like,
        }


CAPABILITY_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("android-play-billing", ("billingclient", "purchase", "acknowledgepurchase", "billing")),
    ("android-admob", ("admob", "mobileads", "interstitialad", "rewardedad")),
    ("android-consent", ("consentinformation", "usermessagingplatform", "consent")),
    ("android-device-qa", ("androidtest", "espresso", "uiautomator", "instrumentation")),
    ("queued-workers", ("celery", "redis", "queue", "worker")),
    ("audit-trail", ("audit", "auditlog", "eventlog")),
    ("backtesting", ("backtest", "backtesting")),
    ("paper-broker", ("paperbroker", "papertrading")),
    ("independent-risk-engine", ("riskengine", "risk_manager", "riskmanager")),
    ("experiment-registry", ("experimentregistry", "mlflow")),
)


def _capability_hints(text: str) -> tuple[str, ...]:
    lower = text.lower()
    result = []
    for capability, terms in CAPABILITY_PATTERNS:
        if any(term in lower for term in terms):
            result.append(capability)
    return tuple(sorted(set(result)))


def _python_components(path: str, text: str) -> list[Component]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    result: list[Component] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            segment = ast.get_source_segment(text, node) or node.name
            result.append(
                Component(
                    name=node.name,
                    kind="class",
                    path=path,
                    language="python",
                    confidence=0.99,
                    dependencies=tuple(sorted(imports)),
                    capability_hints=_capability_hints(segment),
                    test_like="test" in path.lower() or node.name.lower().startswith("test"),
                )
            )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            segment = ast.get_source_segment(text, node) or node.name
            result.append(
                Component(
                    name=node.name,
                    kind="function",
                    path=path,
                    language="python",
                    confidence=0.98,
                    dependencies=tuple(sorted(imports)),
                    capability_hints=_capability_hints(segment),
                    test_like="test" in path.lower() or node.name.lower().startswith("test"),
                )
            )
    return result


def _jvm_components(path: str, text: str) -> list[Component]:
    language = "kotlin" if path.lower().endswith((".kt", ".kts")) else "java"
    imports = tuple(sorted(set(
        match.group(1).split(".")[-1]
        for match in re.finditer(r"(?m)^\s*import\s+([\w.]+)", text)
    )))
    pattern = re.compile(
        r"(?m)^\s*(?:public\s+|private\s+|internal\s+|protected\s+|open\s+|abstract\s+|data\s+|sealed\s+)*"
        r"(class|interface|object|enum\s+class)\s+([A-Za-z_][A-Za-z0-9_]*)"
    )
    result = []
    for match in pattern.finditer(text):
        kind = match.group(1).replace(" ", "-")
        name = match.group(2)
        window = text[match.start(): match.start() + 6000]
        result.append(
            Component(
                name=name,
                kind=kind,
                path=path,
                language=language,
                confidence=0.97,
                dependencies=imports,
                capability_hints=_capability_hints(window),
                test_like="test" in path.lower() or name.lower().endswith("test"),
            )
        )
    return result


def extract_components(e: RepoEvidence, limit: int = 250) -> list[Component]:
    result: list[Component] = []
    seen: set[tuple[str, str, str]] = set()

    for path, text in e.source_documents.items():
        lower = path.lower()
        if lower.endswith(".py"):
            components = _python_components(path, text)
        elif lower.endswith((".kt", ".kts", ".java")):
            components = _jvm_components(path, text)
        else:
            continue

        for component in components:
            key = (component.path, component.kind, component.name)
            if key in seen:
                continue
            seen.add(key)
            result.append(component)
            if len(result) >= limit:
                return result

    return sorted(result, key=lambda item: (item.path, item.kind, item.name))
