from __future__ import annotations

from dataclasses import dataclass

from .models import RepoAssessment


@dataclass(frozen=True, slots=True)
class GraphEdge:
    source: str
    relation: str
    target: str
    confidence: float = 1.0

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "relation": self.relation,
            "target": self.target,
            "confidence": self.confidence,
        }


def build_knowledge_graph(assessments: list[RepoAssessment]) -> dict:
    nodes: dict[str, dict] = {}
    edges: list[GraphEdge] = []

    for assessment in assessments:
        repo_id = f"repo:{assessment.evidence.full_name}"
        nodes[repo_id] = {
            "id": repo_id,
            "type": "repository",
            "name": assessment.evidence.full_name,
            "profile": assessment.profile,
            "score": assessment.score.total,
        }

        profile_id = f"profile:{assessment.profile}"
        nodes.setdefault(profile_id, {
            "id": profile_id,
            "type": "profile",
            "name": assessment.profile,
        })
        edges.append(GraphEdge(repo_id, "classified_as", profile_id, assessment.profile_confidence))

        for capability in assessment.capabilities:
            cap_id = f"capability:{capability.name}"
            nodes.setdefault(cap_id, {
                "id": cap_id,
                "type": "capability",
                "name": capability.name,
                "portable": capability.portable,
            })
            edges.append(GraphEdge(repo_id, "provides", cap_id, capability.confidence))

        component_ids: dict[tuple[str, str], str] = {}
        for component in assessment.components:
            component_id = (
                f"component:{assessment.evidence.full_name}:"
                f"{component.path}:{component.kind}:{component.name}"
            )
            component_ids[(component.path, component.name)] = component_id
            nodes[component_id] = {
                "id": component_id,
                "type": "component",
                "name": component.name,
                "kind": component.kind,
                "path": component.path,
                "language": component.language,
                "test_like": component.test_like,
            }
            edges.append(GraphEdge(repo_id, "contains", component_id, component.confidence))

            for capability in component.capability_hints:
                cap_id = f"capability:{capability}"
                nodes.setdefault(cap_id, {
                    "id": cap_id,
                    "type": "capability",
                    "name": capability,
                    "portable": True,
                })
                edges.append(GraphEdge(component_id, "implements", cap_id, 0.88))

            for dependency in component.dependencies:
                dep_id = f"dependency:{dependency}"
                nodes.setdefault(dep_id, {
                    "id": dep_id,
                    "type": "dependency",
                    "name": dependency,
                })
                edges.append(GraphEdge(component_id, "depends_on", dep_id, 0.90))

    return {
        "schema_version": "production-os/knowledge-graph/v2",
        "nodes": sorted(nodes.values(), key=lambda node: node["id"]),
        "edges": [edge.to_dict() for edge in edges],
    }
