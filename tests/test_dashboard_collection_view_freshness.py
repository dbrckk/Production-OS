from production_os.dashboard_ui import DASHBOARD_HTML


def test_project_and_worker_collections_ignore_older_responses():
    projects = DASHBOARD_HTML.split(
        "async function loadProjectsView(){", 1
    )[1].split("async function loadProjectDetail(repository){", 1)[0]
    assert "let projectsViewLoadSequence=0;" in DASHBOARD_HTML
    assert "const requestSequence=++projectsViewLoadSequence;" in projects
    assert projects.count("requestSequence!==projectsViewLoadSequence") >= 2

    workers = DASHBOARD_HTML.split(
        "async function loadWorkersView(){", 1
    )[1].split("function confirmControlAction", 1)[0]
    assert "let workersViewLoadSequence=0;" in DASHBOARD_HTML
    assert "const requestSequence=++workersViewLoadSequence;" in workers
    assert workers.count("requestSequence!==workersViewLoadSequence") >= 2


def test_attention_collection_ignores_older_responses():
    attention = DASHBOARD_HTML.split(
        "async function loadAttention(){", 1
    )[1].split("let managedProjectsLoadSequence=0;", 1)[0]

    assert "let attentionLoadSequence=0;" in DASHBOARD_HTML
    assert "const requestSequence=++attentionLoadSequence;" in attention
    assert attention.count("requestSequence!==attentionLoadSequence") >= 2

    await_index = attention.index(
        'const data=await api("/v1/dashboard/attention?limit=50");'
    )
    guard_index = attention.index("requestSequence!==attentionLoadSequence")
    render_index = attention.index("count.textContent=")
    assert await_index < guard_index < render_index


def test_autopilot_and_managed_delayed_scrolls_stay_current():
    focused_scroll = DASHBOARD_HTML.split(
        "function scrollToFocusedItemOnce(", 1
    )[1].split("function clearViewPolls(){", 1)[0]
    assert "requestSequence!==currentSequence()" in focused_scroll
    assert "appState.focusScrollKey===key" in focused_scroll
    assert "!focused.isConnected" in focused_scroll
    assert (
        focused_scroll.index("requestSequence!==currentSequence()")
        < focused_scroll.index("focused.scrollIntoView(")
    )

    autopilot = DASHBOARD_HTML.split(
        "async function loadAutopilot(){", 1
    )[1].split("async function acknowledgeIncident", 1)[0]
    assert "let autopilotLoadSequence=0;" in DASHBOARD_HTML
    assert "const requestSequence=++autopilotLoadSequence;" in autopilot
    assert autopilot.count("requestSequence!==autopilotLoadSequence") >= 2
    assert "scrollToFocusedItemOnce(el," in autopilot
    assert "function(){return autopilotLoadSequence}" in autopilot

    managed = DASHBOARD_HTML.split(
        "async function loadManagedProjects(){", 1
    )[1].split("let activityLoadSequence=0;", 1)[0]
    assert "let managedProjectsLoadSequence=0;" in DASHBOARD_HTML
    assert "const requestSequence=++managedProjectsLoadSequence;" in managed
    assert managed.count("requestSequence!==managedProjectsLoadSequence") >= 2
    assert "scrollToFocusedItemOnce(el," in managed
    assert "function(){return managedProjectsLoadSequence}" in managed
