from production_os.asset_forge import build_asset_forge_request, dispatch_asset_forge


class FakeGitHub:
    def __init__(self):
        self.calls = []

    def dispatch_workflow(self, repository, workflow, *, ref, inputs):
        self.calls.append({
            "repository": repository,
            "workflow": workflow,
            "ref": ref,
            "inputs": inputs,
        })


def test_build_asset_forge_request():
    request = build_asset_forge_request(
        request_id="hero-icon-001",
        project="deadline-zero",
        asset_id="hero-icon",
        asset_type="icon",
        instruction="premium survivor game hero icon",
        target_format="svg",
        engine="godot",
    )
    assert request["schema"] == "asset-forge/production-request/v1"
    assert request["manifest"]["source"]["mode"] == "generated"
    assert request["manifest"]["target"]["format"] == "svg"
    assert request["delivery"]["engine"] == "godot"


def test_dispatch_asset_forge_uses_existing_workflow_contract():
    fake = FakeGitHub()
    request = build_asset_forge_request(
        request_id="enemy-001",
        project="deadline-zero",
        asset_id="enemy-grunt",
        asset_type="prop",
        instruction="premium zombie enemy",
        target_format="glb",
    )

    receipt = dispatch_asset_forge(request, client=fake)

    assert receipt.request_id == "enemy-001"
    assert fake.calls[0]["repository"] == "dbrckk/asset-forge"
    assert fake.calls[0]["workflow"] == "production-os-dispatch.yml"
    assert fake.calls[0]["inputs"]["backend"] == "auto"
    assert '"requestId":"enemy-001"' in fake.calls[0]["inputs"]["request_json"]
