from production_os.capabilities import extract_capabilities
from production_os.graph import build_knowledge_graph
from production_os.models import RepoEvidence
from production_os.scoring import assess_repository


def evidence(name="demo", **kwargs):
    base = dict(
        name=name,
        full_name=f"owner/{name}",
        html_url=f"https://github.com/owner/{name}",
        pushed_at="2099-01-01T00:00:00Z",
    )
    base.update(kwargs)
    return RepoEvidence(**base)


def test_android_product_capabilities_are_extracted():
    caps = extract_capabilities(
        evidence(
            has_ci=True,
            has_tests=True,
            has_release_workflow=True,
            readme_text=(
                "Jetpack Compose Android app with Google Play Billing, "
                "AdMob, UMP consent, device testing and AAB publishing tooling."
            ),
        )
    )
    names = {cap.name for cap in caps}
    assert "android-play-billing" in names
    assert "android-admob" in names
    assert "android-consent" in names
    assert "android-device-qa" in names
    assert "android-artifact-build" in names


def test_knowledge_graph_contains_repo_capability_edges():
    assessment = assess_repository(
        evidence(
            "app",
            detected_files=["build.gradle.kts"],
            readme_text="Android app with Google Play Billing",
        )
    )
    graph = build_knowledge_graph([assessment])
    assert any(
        edge["source"] == "repo:owner/app"
        and edge["relation"] == "provides"
        and edge["target"] == "capability:android-play-billing"
        for edge in graph["edges"]
    )


def test_visual_asset_platform_capabilities_are_extracted():
    caps = extract_capabilities(
        evidence(
            "asset-forge",
            has_ci=True,
            has_tests=True,
            readme_text=(
                "Central visual-asset production pipeline for Asset Forge with "
                "sprite sheets, runtime atlas packing, SVG vector sanitization, "
                "glTF/GLB Blender export and Godot 4 handoff."
            ),
        )
    )
    names = {cap.name for cap in caps}
    assert "visual-asset-pipeline" in names
    assert "sprite-atlas-pipeline" in names
    assert "gltf-asset-pipeline" in names
    assert "vector-asset-pipeline" in names
    assert "godot-asset-handoff" in names
