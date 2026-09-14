from production_os.api_auth import TokenAuthorizer, token_digest


def test_token_authorizer_roles():
    auth=TokenAuthorizer([
        {
            "name":"worker-a",
            "role":"worker",
            "sha256":token_digest("secret"),
        }
    ])
    principal=auth.authenticate("secret")
    assert principal is not None
    assert principal.role=="worker"
    assert principal.allows("viewer")
    assert principal.allows("operator") is False
    assert auth.authenticate("wrong") is None
