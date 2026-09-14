from production_os.observability import build_observability_payload


def test_observability_payload_contains_all_sections():
    payload = build_observability_payload(
        health={"status":"healthy"},
        metrics={"cycles":1},
        runtime_records=[{"status":"running"}],
    )
    assert payload["health"]["status"] == "healthy"
    assert payload["metrics"]["cycles"] == 1
    assert payload["runtime_records"][0]["status"] == "running"
