from __future__ import annotations

import hashlib
import json
from typing import Any

from .builder_identity import (
    BuilderIdentityError,
    BuilderTrustPolicy,
)
from .signing import sign_payload, verify_payload


STATEMENT_TYPE = "https://in-toto.io/Statement/v1"
PREDICATE_TYPE = "https://slsa.dev/provenance/v1"


class SupplyChainError(ValueError):
    pass


def _sha256_digest(value: str) -> str:
    digest = str(value or "").lower()
    if (
        len(digest) != 64
        or any(ch not in "0123456789abcdef" for ch in digest)
    ):
        raise SupplyChainError("invalid artifact SHA-256")
    return digest


def create_slsa_statement(
    *,
    release: dict[str, Any],
    provenance: dict[str, Any],
    builder_id: str = "https://production-os.local/builder",
) -> dict[str, Any]:
    metadata = dict(release.get("metadata") or {})
    digest = _sha256_digest(metadata.get("artifact_sha256"))
    artifact_name = str(
        metadata.get("artifact_name")
        or release.get("artifact_id")
        or "artifact"
    )
    source_revision = release.get("source_revision")
    materials = []
    if source_revision:
        materials.append({
            "uri":str(release.get("repository") or ""),
            "digest":{"gitCommit":str(source_revision)},
        })

    return {
        "_type":STATEMENT_TYPE,
        "subject":[{
            "name":artifact_name,
            "digest":{"sha256":digest},
        }],
        "predicateType":PREDICATE_TYPE,
        "predicate":{
            "buildDefinition":{
                "buildType":
                    "https://production-os.local/build/v1",
                "externalParameters":{
                    "repository":release.get("repository"),
                    "workflow_id":release.get("workflow_id"),
                    "workflow_generation":
                        release.get("workflow_generation"),
                },
                "internalParameters":{},
                "resolvedDependencies":materials,
            },
            "runDetails":{
                "builder":{"id":builder_id},
                "metadata":{
                    "invocationId":release.get("workflow_id"),
                    "startedOn":None,
                    "finishedOn":release.get("created_at"),
                },
                "byproducts":[{
                    "name":"production-os-release-provenance",
                    "content":{
                        "release_id":release.get("id"),
                        "provenance_schema":
                            provenance.get("schema_version"),
                        "provenance_key_id":(
                            provenance.get("signature", {})
                            .get("key_id")
                        ),
                        "approval_key":
                            provenance.get("approval_key"),
                        "validator_id":
                            provenance.get("validator_id"),
                    },
                }],
            },
        },
    }


def sign_slsa_statement(
    *,
    statement: dict[str, Any],
    private_key_pem: str,
) -> dict[str, Any]:
    return {
        "schema_version":
            "production-os/signed-slsa-provenance/v1",
        "statement":statement,
        "signature":sign_payload(private_key_pem, statement),
        "signed_at":(
            statement.get("predicate", {})
            .get("runDetails", {})
            .get("metadata", {})
            .get("finishedOn")
        ),
    }


def verify_signed_slsa_statement(
    envelope: dict[str, Any],
    *,
    public_key_pem: str,
    expected_sha256: str | None = None,
) -> bool:
    if envelope.get("schema_version") != (
        "production-os/signed-slsa-provenance/v1"
    ):
        return False
    statement = envelope.get("statement")
    signature = envelope.get("signature")
    if not isinstance(statement, dict) or not isinstance(
        signature, dict
    ):
        return False
    if statement.get("_type") != STATEMENT_TYPE:
        return False
    if statement.get("predicateType") != PREDICATE_TYPE:
        return False
    if expected_sha256 is not None:
        subjects = statement.get("subject") or []
        if len(subjects) != 1:
            return False
        digest = dict(subjects[0].get("digest") or {}).get(
            "sha256"
        )
        if digest != _sha256_digest(expected_sha256):
            return False
    return verify_payload(
        public_key_pem,
        statement,
        signature,
    )


def statement_digest(statement: dict[str, Any]) -> str:
    encoded = json.dumps(
        statement,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()



def verify_trusted_slsa_statement(
    envelope: dict[str, Any],
    *,
    builder_policy: BuilderTrustPolicy,
    expected_repository: str,
    expected_sha256: str | None = None,
) -> bool:
    statement = envelope.get("statement")
    signature = envelope.get("signature")
    signed_at = str(envelope.get("signed_at") or "")
    if not isinstance(statement, dict) or not isinstance(
        signature, dict
    ):
        return False
    predicate = dict(statement.get("predicate") or {})
    run_details = dict(predicate.get("runDetails") or {})
    builder = dict(run_details.get("builder") or {})
    builder_id = str(builder.get("id") or "")
    build_definition = dict(
        predicate.get("buildDefinition") or {}
    )
    external = dict(
        build_definition.get("externalParameters") or {}
    )
    repository = str(external.get("repository") or "")
    if repository != expected_repository or not signed_at:
        return False
    try:
        public_key = builder_policy.resolve(
            builder_id=builder_id,
            key_id=str(signature.get("key_id") or ""),
            repository=repository,
            signed_at=signed_at,
        )
    except (BuilderIdentityError, ValueError):
        return False
    return verify_signed_slsa_statement(
        envelope,
        public_key_pem=public_key,
        expected_sha256=expected_sha256,
    )
