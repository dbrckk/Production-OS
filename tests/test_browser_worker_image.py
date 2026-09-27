from pathlib import Path


def test_browser_worker_image_pins_playwright_and_installs_chromium():
    payload = Path("Dockerfile.browser-worker").read_text(encoding="utf-8")

    assert '"playwright==1.63.0"' in payload
    assert "python -m playwright install --with-deps chromium" in payload
    assert "PLAYWRIGHT_BROWSERS_PATH=/ms-playwright" in payload
    assert "chmod -R a+rX /ms-playwright" in payload
    assert 'USER productionos' in payload



def test_browser_worker_image_includes_git_for_repository_materialization():
    payload = Path("Dockerfile.browser-worker").read_text(encoding="utf-8")
    assert "git ca-certificates" in payload
