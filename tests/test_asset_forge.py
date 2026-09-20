from pathlib import Path
from unittest.mock import patch

from production_os.asset_forge import build_asset_forge_request, dispatch_asset_forge, execute_asset_forge, execute_asset_forge_batch


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

    def commit_files(self, repository, files, *, message, branch):
        self.calls.append({
            "repository": repository,
            "files": dict(files),
            "message": message,
            "branch": branch,
        })
        return {"commit_sha": "batch-sha", "branch": branch, "files": sorted(files)}


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

    def fake_run(cmd, check=False, **kwargs):
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

    def fake_run(cmd, check=False, **kwargs):
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

    def fake_run(cmd, check=False, **kwargs):
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


def test_execute_asset_forge_batch_delivers_only_after_all_validate(tmp_path):
    out = tmp_path / "batch"
    worktree = tmp_path / "repo"
    requests = [
        {
            "request": build_asset_forge_request(
                request_id="batch-a",
                project="deadline-zero",
                asset_id="a",
                asset_type="icon",
                instruction="premium icon a",
                target_format="svg",
            ),
            "target_path": "assets/art/a.svg",
        },
        {
            "request": build_asset_forge_request(
                request_id="batch-b",
                project="deadline-zero",
                asset_id="b",
                asset_type="icon",
                instruction="premium icon b",
                target_format="svg",
            ),
            "target_path": "assets/art/b.svg",
        },
    ]

    def fake_run(cmd, check=False, **kwargs):
        request_path = Path(cmd[cmd.index("fulfill") + 1])
        request = __import__("json").loads(request_path.read_text())
        output = Path(cmd[cmd.index("--output-dir") + 1])
        output.mkdir(parents=True, exist_ok=True)
        artifact = output / f'{request["manifest"]["id"]}.svg'
        artifact.write_text(f'<svg id="{request["manifest"]["id"]}"/>', encoding="utf-8")
        (output / "production-report.json").write_text(
            __import__("json").dumps({"success": True, "artifact": str(artifact)}),
            encoding="utf-8",
        )
        class Result:
            returncode = 0
        return Result()

    with patch("production_os.asset_forge.shutil.which", return_value="/usr/bin/asset-forge"), patch(
        "production_os.asset_forge.subprocess.run", side_effect=fake_run
    ):
        result = execute_asset_forge_batch(
            requests,
            output_root=str(out),
            target_worktree=str(worktree),
            mode="local",
        )

    assert result["success"] is True
    assert result["count"] == 2
    assert (worktree / "assets/art/a.svg").is_file()
    assert (worktree / "assets/art/b.svg").is_file()


def test_execute_asset_forge_batch_aborts_delivery_when_one_asset_fails(tmp_path):
    out = tmp_path / "batch"
    worktree = tmp_path / "repo"
    existing = worktree / "assets/art/a.svg"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("old", encoding="utf-8")
    requests = [
        {
            "request": build_asset_forge_request(
                request_id="batch-a",
                project="deadline-zero",
                asset_id="a",
                asset_type="icon",
                instruction="premium icon a",
                target_format="svg",
            ),
            "target_path": "assets/art/a.svg",
        },
        {
            "request": build_asset_forge_request(
                request_id="batch-b",
                project="deadline-zero",
                asset_id="b",
                asset_type="icon",
                instruction="premium icon b",
                target_format="svg",
            ),
            "target_path": "assets/art/b.svg",
        },
    ]

    calls = 0
    def fake_run(cmd, check=False, **kwargs):
        nonlocal calls
        calls += 1
        output = Path(cmd[cmd.index("--output-dir") + 1])
        output.mkdir(parents=True, exist_ok=True)
        if calls == 2:
            class Failed:
                returncode = 1
            return Failed()
        artifact = output / "a.svg"
        artifact.write_text("<svg/>", encoding="utf-8")
        (output / "production-report.json").write_text(
            __import__("json").dumps({"success": True, "artifact": str(artifact)}),
            encoding="utf-8",
        )
        class Result:
            returncode = 0
        return Result()

    with patch("production_os.asset_forge.shutil.which", return_value="/usr/bin/asset-forge"), patch(
        "production_os.asset_forge.subprocess.run", side_effect=fake_run
    ):
        try:
            execute_asset_forge_batch(
                requests,
                output_root=str(out),
                target_worktree=str(worktree),
                mode="local",
            )
        except RuntimeError:
            pass
        else:
            raise AssertionError("expected batch failure")

    assert existing.read_text(encoding="utf-8") == "old"
    assert not (worktree / "assets/art/b.svg").exists()


def test_execute_asset_forge_batch_uses_single_github_commit(tmp_path):
    fake = FakeGitHub()
    out = tmp_path / "batch"
    requests = [
        {
            "request": build_asset_forge_request(
                request_id=f"batch-{name}",
                project="deadline-zero",
                asset_id=name,
                asset_type="icon",
                instruction=f"premium icon {name}",
                target_format="svg",
            ),
            "target_path": f"assets/art/{name}.svg",
        }
        for name in ("a", "b")
    ]

    def fake_run(cmd, check=False, **kwargs):
        request_path = Path(cmd[cmd.index("fulfill") + 1])
        request = __import__("json").loads(request_path.read_text())
        output = Path(cmd[cmd.index("--output-dir") + 1])
        output.mkdir(parents=True, exist_ok=True)
        asset_id = request["manifest"]["id"]
        artifact = output / f"{asset_id}.svg"
        artifact.write_text(f"<svg id='{asset_id}'/>", encoding="utf-8")
        (output / "production-report.json").write_text(
            __import__("json").dumps({"success": True, "artifact": str(artifact)}),
            encoding="utf-8",
        )
        class Result:
            returncode = 0
        return Result()

    with patch("production_os.asset_forge.shutil.which", return_value="/usr/bin/asset-forge"), patch(
        "production_os.asset_forge.subprocess.run", side_effect=fake_run
    ):
        result = execute_asset_forge_batch(
            requests,
            output_root=str(out),
            target_repository="dbrckk/deadline-zero",
            target_ref="main",
            client=fake,
            mode="local",
        )

    commits = [call for call in fake.calls if "files" in call]
    assert len(commits) == 1
    assert sorted(commits[0]["files"]) == ["assets/art/a.svg", "assets/art/b.svg"]
    assert result["delivery_mode"] == "github"


def test_execute_asset_forge_batch_respects_dependency_order(tmp_path):
    out = tmp_path / "batch"
    worktree = tmp_path / "repo"
    items = []
    chain = [
        ("character", []),
        ("animation", ["character"]),
        ("spritesheet", ["animation"]),
        ("atlas", ["spritesheet"]),
    ]
    for name, deps in reversed(chain):
        items.append({
            "id": name,
            "depends_on": deps,
            "request": build_asset_forge_request(
                request_id=f"dep-{name}",
                project="deadline-zero",
                asset_id=name,
                asset_type="icon",
                instruction=f"premium {name}",
                target_format="svg",
            ),
            "target_path": f"assets/art/{name}.svg",
        })

    seen = []
    def fake_run(cmd, check=False, **kwargs):
        request_path = Path(cmd[cmd.index("fulfill") + 1])
        request = __import__("json").loads(request_path.read_text())
        asset_id = request["manifest"]["id"]
        seen.append(asset_id)
        output = Path(cmd[cmd.index("--output-dir") + 1])
        output.mkdir(parents=True, exist_ok=True)
        artifact = output / f"{asset_id}.svg"
        artifact.write_text(f"<svg id='{asset_id}'/>", encoding="utf-8")
        (output / "production-report.json").write_text(
            __import__("json").dumps({"success": True, "artifact": str(artifact)}),
            encoding="utf-8",
        )
        class Result:
            returncode = 0
        return Result()

    with patch("production_os.asset_forge.shutil.which", return_value="/usr/bin/asset-forge"), patch(
        "production_os.asset_forge.subprocess.run", side_effect=fake_run
    ):
        result = execute_asset_forge_batch(
            items,
            output_root=str(out),
            target_worktree=str(worktree),
            mode="local",
        )

    assert seen == ["character", "animation", "spritesheet", "atlas"]
    assert result["execution_order"] == seen
    assert result["items"][-1]["depends_on"] == ["spritesheet"]
    dependency = result["items"][-1]["dependency_artifacts"][0]
    assert dependency["id"] == "spritesheet"
    assert len(dependency["sha256"]) == 64
    assert len(result["items"][-1]["sha256"]) == 64


def test_execute_asset_forge_batch_rejects_dependency_cycles(tmp_path):
    items = [
        {
            "id": "a",
            "depends_on": ["b"],
            "request": build_asset_forge_request(
                request_id="cycle-a",
                project="deadline-zero",
                asset_id="a",
                asset_type="icon",
                instruction="premium a",
                target_format="svg",
            ),
            "target_path": "assets/art/a.svg",
        },
        {
            "id": "b",
            "depends_on": ["a"],
            "request": build_asset_forge_request(
                request_id="cycle-b",
                project="deadline-zero",
                asset_id="b",
                asset_type="icon",
                instruction="premium b",
                target_format="svg",
            ),
            "target_path": "assets/art/b.svg",
        },
    ]

    with patch("production_os.asset_forge.shutil.which", return_value="/usr/bin/asset-forge"):
        try:
            execute_asset_forge_batch(
                items,
                output_root=str(tmp_path / "out"),
                target_worktree=str(tmp_path / "repo"),
                mode="local",
            )
        except ValueError as exc:
            assert "cyclic" in str(exc)
        else:
            raise AssertionError("expected cyclic dependency rejection")


def test_execute_asset_forge_batch_rejects_unknown_dependency(tmp_path):
    item = {
        "id": "atlas",
        "depends_on": ["missing-spritesheet"],
        "request": build_asset_forge_request(
            request_id="unknown-dep",
            project="deadline-zero",
            asset_id="atlas",
            asset_type="icon",
            instruction="premium atlas",
            target_format="svg",
        ),
        "target_path": "assets/art/atlas.svg",
    }

    with patch("production_os.asset_forge.shutil.which", return_value="/usr/bin/asset-forge"):
        try:
            execute_asset_forge_batch(
                [item],
                output_root=str(tmp_path / "out"),
                target_worktree=str(tmp_path / "repo"),
                mode="local",
            )
        except ValueError as exc:
            assert "unknown" in str(exc)
        else:
            raise AssertionError("expected unknown dependency rejection")


def test_dependent_raster_asset_receives_validated_parent_reference(tmp_path):
    out = tmp_path / "batch"
    worktree = tmp_path / "repo"
    items = [
        {
            "id": "character",
            "request": build_asset_forge_request(
                request_id="ref-character",
                project="deadline-zero",
                asset_id="character",
                asset_type="sprite-sheet",
                instruction="premium character sprite",
                target_format="png",
            ),
            "target_path": "assets/art/character.png",
        },
        {
            "id": "animation",
            "depends_on": ["character"],
            "request": build_asset_forge_request(
                request_id="ref-animation",
                project="deadline-zero",
                asset_id="animation",
                asset_type="sprite-sheet",
                instruction="premium animation sprite",
                target_format="png",
            ),
            "target_path": "assets/art/animation.png",
        },
    ]
    commands = []

    def fake_run(cmd, check=False, **kwargs):
        commands.append(list(cmd))
        request_path = Path(cmd[cmd.index("fulfill") + 1])
        request = __import__("json").loads(request_path.read_text())
        output = Path(cmd[cmd.index("--output-dir") + 1])
        output.mkdir(parents=True, exist_ok=True)
        asset_id = request["manifest"]["id"]
        artifact = output / f"{asset_id}.png"
        artifact.write_bytes(asset_id.encode("utf-8"))
        (output / "production-report.json").write_text(
            __import__("json").dumps({"success": True, "artifact": str(artifact)}),
            encoding="utf-8",
        )
        class Result:
            returncode = 0
        return Result()

    with patch("production_os.asset_forge.shutil.which", return_value="/usr/bin/asset-forge"), patch(
        "production_os.asset_forge.subprocess.run", side_effect=fake_run
    ):
        result = execute_asset_forge_batch(
            items,
            output_root=str(out),
            target_worktree=str(worktree),
            mode="local",
        )

    child = commands[1]
    assert "--reference" in child
    reference = Path(child[child.index("--reference") + 1])
    assert reference.name == "character.png"
    assert result["items"][1]["visual_references"] == [str(reference)]


def test_batch_receipt_surfaces_visual_similarity_quality_summary(tmp_path):
    out = tmp_path / "batch"
    worktree = tmp_path / "repo"
    item = {
        "id": "character",
        "request": build_asset_forge_request(
            request_id="quality-character",
            project="deadline-zero",
            asset_id="character",
            asset_type="sprite-sheet",
            instruction="premium character sprite",
            target_format="png",
        ),
        "target_path": "assets/art/character.png",
    }

    def fake_run(cmd, check=False, **kwargs):
        output = Path(cmd[cmd.index("--output-dir") + 1])
        output.mkdir(parents=True, exist_ok=True)
        artifact = output / "character.png"
        artifact.write_bytes(b"character")
        (output / "production-report.json").write_text(
            __import__("json").dumps({
                "success": True,
                "artifact": str(artifact),
                "generation": {
                    "visualSimilarity": {
                        "threshold": 0.55,
                        "passed": True,
                        "attempts": [
                            {"score": 0.31, "passed": False},
                            {"score": 0.82, "passed": True},
                        ],
                    }
                },
            }),
            encoding="utf-8",
        )
        class Result:
            returncode = 0
        return Result()

    with patch("production_os.asset_forge.shutil.which", return_value="/usr/bin/asset-forge"), patch(
        "production_os.asset_forge.subprocess.run", side_effect=fake_run
    ):
        result = execute_asset_forge_batch(
            [item],
            output_root=str(out),
            target_worktree=str(worktree),
            mode="local",
        )

    assert result["quality_summary"] == {
        "checked": 1,
        "regenerated": 1,
        "minimum_score": 0.82,
    }
    assert result["items"][0]["visual_similarity"]["passed"] is True
