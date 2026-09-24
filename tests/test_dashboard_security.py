from production_os.dashboard_security import redact_log_value


def test_recursive_redaction_removes_sensitive_values():
    value = {
        "authorization": "Bearer abc",
        "nested": {
            "api_key": "secret-key",
            "password": "hunter2",
            "message": "Authorization: Bearer visible-secret",
        },
    }
    redacted = redact_log_value(value)
    assert redacted["authorization"] == "[REDACTED]"
    assert redacted["nested"]["api_key"] == "[REDACTED]"
    assert redacted["nested"]["password"] == "[REDACTED]"
    assert "visible-secret" not in redacted["nested"]["message"]
