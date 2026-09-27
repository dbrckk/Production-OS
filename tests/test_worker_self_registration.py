from production_os.api_auth import Principal
from production_os.control_plane import ControlPlane


def test_worker_token_can_only_self_register_matching_worker_id():
    principal = Principal(name="ai-dev-server-1", role="worker")

    assert ControlPlane.worker_registration_allowed(
        principal,
        "ai-dev-server-1",
    ) is True
    assert ControlPlane.worker_registration_allowed(
        principal,
        "other-worker",
    ) is False


def test_operator_and_admin_can_register_workers():
    assert ControlPlane.worker_registration_allowed(
        Principal(name="operator-one", role="operator"),
        "ai-dev-server-1",
    ) is True
    assert ControlPlane.worker_registration_allowed(
        Principal(name="admin-one", role="admin"),
        "worker-browser",
    ) is True


def test_viewer_cannot_register_workers():
    assert ControlPlane.worker_registration_allowed(
        Principal(name="viewer-one", role="viewer"),
        "viewer-one",
    ) is False
