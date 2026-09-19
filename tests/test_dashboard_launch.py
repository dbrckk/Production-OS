from production_os.control_plane import DASHBOARD_HTML


def test_dashboard_exposes_workflow_launcher():
    assert 'id="repository"' in DASHBOARD_HTML
    assert 'value="dbrckk/Jumpy"' in DASHBOARD_HTML
    assert 'id="task"' in DASHBOARD_HTML
    assert 'id="budget"' in DASHBOARD_HTML
    assert 'id="agent"' in DASHBOARD_HTML
    assert 'onclick="launchWorkflow()"' in DASHBOARD_HTML
    assert "api('/v1/workflows'" in DASHBOARD_HTML
    assert "'/dispatch'" in DASHBOARD_HTML
    assert "token_budget:budget" in DASHBOARD_HTML
    assert "agent_preference:agent" in DASHBOARD_HTML
