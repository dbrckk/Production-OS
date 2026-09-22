from production_os.dashboard_security import redact_log_value


def test_log_redaction_masks_credentials_recursively():
    payload = {
        "message": (
            "Authorization: Bearer abcdefghijklmnopqrstuvwxyz "
            "and Bearer zyxwvutsrqponmlkjihgfedcba"
        ),
        "meta": {
            "api_key": "sk-secret-value",
            "password": "plain-password",
            "safe": "ok",
        },
        "items": [
            {"token": "nested-secret"},
            "cookie=super-secret-cookie",
        ],
    }

    redacted = redact_log_value(payload)
    rendered = str(redacted)

    assert "abcdefghijklmnopqrstuvwxyz" not in rendered
    assert "zyxwvutsrqponmlkjihgfedcba" not in rendered
    assert "sk-secret-value" not in rendered
    assert "plain-password" not in rendered
    assert "nested-secret" not in rendered
    assert "super-secret-cookie" not in rendered
    assert redacted["meta"]["safe"] == "ok"
