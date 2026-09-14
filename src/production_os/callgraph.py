from __future__ import annotations

import ast
import re
from dataclasses import dataclass

from .models import RepoAssessment


@dataclass(frozen=True, slots=True)
class CallEdge:
    source_component: str
    target_symbol: str
    relation: str
    confidence: float

    def to_dict(self) -> dict:
        return {
            "source_component": self.source_component,
            "target_symbol": self.target_symbol,
            "relation": self.relation,
            "confidence": self.confidence,
        }


def build_call_import_graph(assessment: RepoAssessment) -> dict:
    edges: list[CallEdge] = []
    components_by_path: dict[str, list] = {}
    for component in assessment.components:
        components_by_path.setdefault(component.path, []).append(component)

    for path, text in assessment.evidence.source_documents.items():
        lower = path.lower()
        if lower.endswith(".py"):
            try:
                tree = ast.parse(text)
            except SyntaxError:
                continue

            calls = {
                node.func.id
                for node in ast.walk(tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            }
            attrs = {
                node.func.attr
                for node in ast.walk(tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            }
            for component in components_by_path.get(path, []):
                cid = f"{component.path}:{component.name}"
                for symbol in sorted(calls | attrs):
                    edges.append(CallEdge(cid, symbol, "calls", 0.82))

        elif lower.endswith((".kt", ".kts", ".java")):
            call_names = set(
                match.group(1)
                for match in re.finditer(r"([A-Za-z_][A-Za-z0-9_]*)s*(", text)
            )
            keywords = {
                "if","for","while","when","switch","return","catch","super","this",
                "class","interface","object","fun","new","try","synchronized"
            }
            call_names -= keywords
            for component in components_by_path.get(path, []):
                cid = f"{component.path}:{component.name}"
                for symbol in sorted(call_names):
                    if symbol != component.name:
                        edges.append(CallEdge(cid, symbol, "calls", 0.72))

    return {
        "schema_version": "production-os/call-graph/v1",
        "edges": [edge.to_dict() for edge in edges[:2000]],
    }
