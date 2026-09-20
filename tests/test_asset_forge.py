from pathlib import Path
from unittest.mock import patch

from production_os.asset_forge import build_asset_forge_request, dispatch_asset_forge, execute_asset_forge


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

    def put_file(self, repository, path, content, *, message, branch):
        self.calls.append({
            "repository": repository,
            "path": path,
            "content": content,
            "message": message,
            "branch": branch,
        })
        return {"content": {"path": path}}


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


def test_execute_asset_forge_auto_prefers_local_cli(tmp_path):
    request = build_asset_forge_request(
        request_id="local-001",
        project="deadline-zero",
        asset_id="hud-icon",
        asset_type="icon",
        instruction="premium HUD icon",
        target_format="svg",
    )
    out = tmp_path / "out"

    def fake_run(cmd, check=False):
        out.mkdir(parents=True, exist_ok=True)
        artifact = out / "hud-icon.svg"
        artifact.write_text("<svg/>", encoding="utf-8")
        (out / "production-report.json").write_text(
            '{"success":true,"artifact":"' + str(artifact).replace("\\","\\\\") + '"}',
            encoding="utf-8",
        )
        class Result:
            returncode = 0
        return Result()

    with patch("production_os.asset_forge.shutil.which", return_value="/usr/bin/asset-forge"), patch(
        "production_os.asset_forge.subprocess.run", side_effect=fake_run
    ) as run:
        receipt = execute_asset_forge(request, output_dir=str(out), mode="auto")

    assert receipt.mode == "local"
    assert receipt.report_path == str(out / "production-report.json")
    assert run.call_args.args[0][0] == "/usr/bin/asset-forge"
    assert "fulfill" in run.call_args.args[0]


def test_execute_asset_forge_auto_falls_back_to_github():
    fake = FakeGitHub()
    request = build_asset_forge_request(
        request_id="remote-001",
        project="deadline-zero",
        asset_id="hero",
        asset_type="icon",
        instruction="premium hero icon",
        target_format="svg",
    )
    with patch("production_os.asset_forge.shutil.which", return_value=None):
        receipt = execute_asset_forge(request, client=fake, mode="auto")
    assert receipt.mode == "github"
    assert len(fake.calls) == 1


def test_execute_asset_forge_delivers_to_worktree(tmp_path):
    request = build_asset_forge_request(
        request_id="deliver-local-001",
        project="deadline-zero",
        asset_id="hud-icon",
        asset_type="icon",
        instruction="premium HUD icon",
        target_format="svg",
    )
    out = tmp_path / "out"
    worktree = tmp_path / "repo"

    def fake_run(cmd, check=False):
        out.mkdir(parents=True, exist_ok=True)
        artifact = out / "hud-icon.svg"
        artifact.write_text("<svg/>", encoding="utf-8")
        (out / "production-report.json").write_text(
            '{"success":true,"artifact":"' + str(artifact).replace("\\","\\\\") + '"}',
            encoding="utf-8",
        )
        class Result:
            returncode = 0
        return Result()

    with patch("production_os.asset_forge.shutil.which", return_value="/usr/bin/asset-forge"), patch(
        "production_os.asset_forge.subprocess.run", side_effect=fake_run
    ):
        receipt = execute_asset_forge(
            request,
            output_dir=str(out),
            mode="local",
            target_worktree=str(worktree),
            target_path="assets/art/hud-icon.svg",
        )

    delivered = worktree / "assets/art/hud-icon.svg"
    assert delivered.read_text(encoding="utf-8") == "<svg/>"
    assert receipt.delivery_mode == "worktree"
    assert receipt.delivered_to == str(delivered.resolve())


def test_execute_asset_forge_delivers_with_existing_github_client(tmp_path):
    fake = FakeGitHub()
    request = build_asset_forge_request(
        request_id="deliver-github-001",
        project="deadline-zero",
        asset_id="hud-icon",
        asset_type="icon",
        instruction="premium HUD icon",
        target_format="svg",
    )
    out = tmp_path / "out"

    def fake_run(cmd, check=False):
        out.mkdir(parents=True, exist_ok=True)
        artifact = out / "hud-icon.svg"
        artifact.write_bytes(b"<svg/>")
        (out / "production-report.json").write_text(
            '{"success":true,"artifact":"' + str(artifact).replace("\\","\\\\") + '"}',
            encoding="utf-8",
        )
        class Result:
            returncode = 0
        return Result()

    with patch("production_os.asset_forge.shutil.which", return_value="/usr/bin/asset-forge"), patch(
        "production_os.asset_forge.subprocess.run", side_effect=fake_run
    ):
        receipt = execute_asset_forge(
            request,
            output_dir=str(out),
            mode="local",
            target_repository="dbrckk/deadline-zero",
            target_path="assets/art/hud-icon.svg",
            client=fake,
        )

    write = [call for call in fake.calls if "path" in call][0]
    assert write["repository"] == "dbrckk/deadline-zero"
    assert write["path"] == "assets/art/hud-icon.svg"
    assert write["content"] == b"<svg/>"
    assert receipt.delivery_mode == "github"
