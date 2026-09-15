from __future__ import annotations

import json
import uuid

from .dual_sign import (
    DUAL_SCHEMA,
    DualSignError,
    verify_dual_attestation,
)
from .asymmetric_attestations import (
    AsymmetricAttestationError,
    create_release_provenance as create_release_provenance_v2,
    verify_release_provenance as verify_release_provenance_v2,
    verify_validation_attestation as verify_validation_attestation_v2,
)
from .transparency import (
    GENESIS_HASH,
    create_entry as create_transparency_entry,
    verify_chain as verify_transparency_chain,
)
from .builder_identity import BuilderTrustPolicy
from .supply_chain import (
    create_slsa_statement,
    sign_slsa_statement,
    statement_digest,
    verify_signed_slsa_statement,
    verify_trusted_slsa_statement,
)
from .attestations import (
    AttestationError,
    create_release_provenance,
    release_approval_key,
    verify_release_provenance,
    verify_validation_attestation,
)
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_postgres(backend) -> bool:
    return backend.__class__.__name__.startswith("Postgres")


def _sql(backend, statement: str) -> str:
    return statement.replace("?", "%s") if _is_postgres(backend) else statement


def _execute(db, backend, statement: str, params: tuple = ()):
    return db.execute(_sql(backend, statement), params)


def _canonical_sha256(value: dict) -> str:
    import hashlib
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _valid_sha256(value: str | None) -> bool:
    if not value or len(str(value)) != 64:
        return False
    try:
        int(str(value), 16)
    except ValueError:
        return False
    return True


class ReleaseLedger:
    def __init__(
        self,
        backend,
        workflows,
        *,
        trusted_validation_secrets: dict[str, str] | None = None,
        provenance_secret: str | None = None,
        attestation_max_age_seconds: int = 3600,
        trusted_validation_public_keys: dict[str, str] | None = None,
        provenance_private_key: str | None = None,
        provenance_public_key: str | None = None,
        validation_signature_policy: str = "compatible",
        builder_id: str = "https://production-os.local/builder",
        trusted_builders: dict | None = None,
        trusted_builder_keys: dict | None = None,
        require_trusted_builder: bool = False,
    ):
        self.backend = backend
        self.workflows = workflows
        self.trusted_validation_secrets = dict(
            trusted_validation_secrets or {}
        )
        self.provenance_secret = provenance_secret
        self.attestation_max_age_seconds = int(
            attestation_max_age_seconds
        )
        self.trusted_validation_public_keys = dict(
            trusted_validation_public_keys or {}
        )
        self.provenance_private_key = provenance_private_key
        self.provenance_public_key = provenance_public_key
        policy = str(validation_signature_policy).strip().lower()
        if policy not in {
            "compatible",
            "dual-required",
            "ed25519-only",
        }:
            raise ValueError(
                "validation_signature_policy must be compatible, "
                "dual-required, or ed25519-only"
            )
        self.validation_signature_policy = policy
        self.builder_id = str(builder_id)
        self.require_trusted_builder = bool(require_trusted_builder)
        self.builder_trust_policy = (
            BuilderTrustPolicy(
                builders=dict(trusted_builders or {}),
                signing_keys=dict(trusted_builder_keys or {}),
            )
            if trusted_builders or trusted_builder_keys
            else None
        )
        if (
            self.require_trusted_builder
            and self.builder_trust_policy is None
        ):
            raise ValueError(
                "trusted builder policy is required"
            )

    @staticmethod
    def _validation_passed(validation: dict) -> bool:
        if str(validation.get("status") or "") != "passed":
            return False
        if validation.get("blocking_failures"):
            return False
        if (
            "promotion_allowed" in validation
            and not bool(validation["promotion_allowed"])
        ):
            return False
        return True

    @staticmethod
    def _row(row) -> dict:
        return {
            "id":row["id"],
            "workflow_id":row["workflow_id"],
            "artifact_id":row["artifact_id"],
            "repository":row["repository"],
            "source_revision":row["source_revision"],
            "workflow_generation":row["workflow_generation"],
            "validation":json.loads(row["validation_json"]),
            "metadata":json.loads(row["metadata_json"]),
            "status":row["status"],
            "rollback_of":row["rollback_of"],
            "created_at":row["created_at"],
        }

    def get(self, release_id: str) -> dict:
        with self.backend.connect() as db:
            row = _execute(
                db,
                self.backend,
                "SELECT * FROM releases WHERE id=?",
                (release_id,),
            ).fetchone()
        if row is None:
            raise KeyError(release_id)
        return self._row(row)

    def list_for_workflow(self, workflow_id: str) -> list[dict]:
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """
                SELECT * FROM releases
                WHERE workflow_id=?
                ORDER BY created_at ASC, id ASC
                """,
                (workflow_id,),
            ).fetchall()
        return [self._row(row) for row in rows]

    def promote(
        self,
        *,
        workflow_id: str,
        artifact_id: str,
        validation: dict,
        attestation: dict,
        approval: dict,
        metadata: dict | None = None,
    ) -> dict:
        if not self._validation_passed(validation):
            raise RuntimeError(
                "validation must be passed before promotion"
            )

        release_id = uuid.uuid4().hex
        now = _now()

        with self.backend.transaction() as db:
            workflow_row = _execute(
                db,
                self.backend,
                (
                    "SELECT * FROM workflows WHERE id=? FOR UPDATE"
                    if _is_postgres(self.backend)
                    else "SELECT * FROM workflows WHERE id=?"
                ),
                (workflow_id,),
            ).fetchone()
            if workflow_row is None:
                raise KeyError(workflow_id)
            if workflow_row["status"] != "succeeded":
                raise RuntimeError(
                    "workflow must be succeeded before promotion"
                )

            workflow_metadata = json.loads(
                workflow_row["metadata_json"]
            )
            if bool(workflow_metadata.get("superseded", False)):
                raise RuntimeError(
                    "stale workflow generation: workflow is superseded"
                )

            artifact_row = _execute(
                db,
                self.backend,
                (
                    "SELECT * FROM artifacts "
                    "WHERE id=? AND workflow_id=? FOR UPDATE"
                    if _is_postgres(self.backend)
                    else
                    "SELECT * FROM artifacts "
                    "WHERE id=? AND workflow_id=?"
                ),
                (artifact_id, workflow_id),
            ).fetchone()
            if artifact_row is None:
                raise KeyError(f"artifact {artifact_id}")

            artifact_metadata = json.loads(
                artifact_row["metadata_json"]
            )
            artifact_sha256 = artifact_row["sha256"]
            if not _valid_sha256(artifact_sha256):
                raise RuntimeError(
                    "valid 64-character artifact sha256 is required "
                    "before promotion"
                )

            source_revision = artifact_metadata.get(
                "source_revision"
            )
            workflow_generation = artifact_metadata.get(
                "workflow_generation"
            )

            attestation_schema = str(
                dict(attestation or {}).get("schema_version") or ""
            )
            dual_signed = attestation_schema == DUAL_SCHEMA
            if (
                self.validation_signature_policy == "dual-required"
                and not dual_signed
            ):
                raise RuntimeError(
                    "validation signature policy requires dual-sign"
                )
            if (
                self.validation_signature_policy == "ed25519-only"
                and not attestation_schema.endswith(
                    "/validation-attestation/v2"
                )
            ):
                raise RuntimeError(
                    "validation signature policy requires Ed25519-only"
                )
            asymmetric = (
                dual_signed
                or attestation_schema.endswith(
                    "/validation-attestation/v2"
                )
            )
            try:
                if dual_signed:
                    if not self.trusted_validation_secrets:
                        raise RuntimeError(
                            "trusted validation HMAC keys "
                            "are not configured"
                        )
                    if not self.trusted_validation_public_keys:
                        raise RuntimeError(
                            "trusted validation public keys "
                            "are not configured"
                        )
                    if not self.provenance_private_key:
                        raise RuntimeError(
                            "release provenance private key "
                            "is not configured"
                        )
                    verified_bundle = verify_dual_attestation(
                        dict(attestation or {}),
                        trusted_secrets=(
                            self.trusted_validation_secrets
                        ),
                        trusted_public_keys=(
                            self.trusted_validation_public_keys
                        ),
                        workflow_id=workflow_id,
                        artifact_id=artifact_id,
                        artifact_sha256=artifact_sha256,
                        source_revision=source_revision,
                        workflow_generation=workflow_generation,
                        validation=validation,
                        max_age_seconds=(
                            self.attestation_max_age_seconds
                        ),
                    )
                    verified_attestation = (
                        verified_bundle["ed25519"]
                    )
                elif asymmetric:
                    if not self.trusted_validation_public_keys:
                        raise RuntimeError(
                            "trusted validation public keys are not configured"
                        )
                    if not self.provenance_private_key:
                        raise RuntimeError(
                            "release provenance private key is not configured"
                        )
                    verified_attestation = (
                        verify_validation_attestation_v2(
                            dict(attestation or {}),
                            trusted_public_keys=(
                                self.trusted_validation_public_keys
                            ),
                            workflow_id=workflow_id,
                            artifact_id=artifact_id,
                            artifact_sha256=artifact_sha256,
                            source_revision=source_revision,
                            workflow_generation=workflow_generation,
                            validation=validation,
                            max_age_seconds=(
                                self.attestation_max_age_seconds
                            ),
                        )
                    )
                else:
                    if not self.trusted_validation_secrets:
                        raise RuntimeError(
                            "trusted validation attestation keys "
                            "are not configured"
                        )
                    if not self.provenance_secret:
                        raise RuntimeError(
                            "release provenance signing secret "
                            "is not configured"
                        )
                    verified_attestation = (
                        verify_validation_attestation(
                            dict(attestation or {}),
                            trusted_secrets=(
                                self.trusted_validation_secrets
                            ),
                            workflow_id=workflow_id,
                            artifact_id=artifact_id,
                            artifact_sha256=artifact_sha256,
                            source_revision=source_revision,
                            workflow_generation=workflow_generation,
                            validation=validation,
                            max_age_seconds=(
                                self.attestation_max_age_seconds
                            ),
                        )
                    )
            except (
                AttestationError,
                AsymmetricAttestationError,
                DualSignError,
            ) as exc:
                raise RuntimeError(str(exc)) from exc

            approval = dict(approval or {})
            approved_by = str(
                approval.get("approved_by") or ""
            ).strip()
            approval_role = str(
                approval.get("role") or ""
            ).strip()
            if not bool(approval.get("approved", False)):
                raise RuntimeError("release approval is required")
            if not approved_by or not approval_role:
                raise RuntimeError(
                    "release approval requires approved_by and role"
                )

            computed_approval_key = release_approval_key(
                workflow_id=workflow_id,
                artifact_id=artifact_id,
                artifact_sha256=artifact_sha256,
                source_revision=source_revision,
                workflow_generation=workflow_generation,
            )
            supplied_approval_key = str(
                approval.get("approval_key") or ""
            )
            if (
                supplied_approval_key
                and supplied_approval_key != computed_approval_key
            ):
                raise RuntimeError(
                    "release approval binding mismatch"
                )
            approval_record = {
                "approved":True,
                "approved_by":approved_by,
                "role":approval_role,
                "approval_key":computed_approval_key,
                **(
                    {"reason":str(approval["reason"])}
                    if approval.get("reason") is not None
                    else {}
                ),
            }

            expected_revision = workflow_metadata.get(
                "github_pr_head_sha"
            )
            expected_generation = workflow_metadata.get(
                "github_pr_generation"
            )

            if expected_revision:
                if not source_revision:
                    raise RuntimeError(
                        "source revision required for PR workflow"
                    )
                if str(source_revision) != str(expected_revision):
                    raise RuntimeError(
                        "stale workflow generation: "
                        "source revision mismatch"
                    )

            if expected_generation is not None:
                if workflow_generation is None:
                    raise RuntimeError(
                        "workflow generation required for PR workflow"
                    )
                if int(workflow_generation) != int(
                    expected_generation
                ):
                    raise RuntimeError(
                        "stale workflow generation: "
                        "generation mismatch"
                    )

            existing = _execute(
                db,
                self.backend,
                """
                SELECT id FROM releases
                WHERE artifact_id=? AND status='promoted'
                """,
                (artifact_id,),
            ).fetchone()
            if existing is not None:
                raise RuntimeError(
                    "artifact already promoted as release "
                    f"{existing['id']}"
                )

            base_metadata = {
                **dict(metadata or {}),
                "artifact_name":artifact_row["name"],
                "artifact_uri":artifact_row["uri"],
                "artifact_sha256":artifact_sha256,
                "approval":approval_record,
            }
            release_preview = {
                "id":release_id,
                "workflow_id":workflow_id,
                "artifact_id":artifact_id,
                "repository":workflow_row["repository"],
                "source_revision":source_revision,
                "workflow_generation":(
                    int(workflow_generation)
                    if workflow_generation is not None
                    else None
                ),
                "metadata":base_metadata,
                "created_at":now,
            }
            if asymmetric:
                provenance = create_release_provenance_v2(
                    private_key_pem=self.provenance_private_key,
                    release=release_preview,
                    attestation=verified_attestation,
                )
                statement = create_slsa_statement(
                    release=release_preview,
                    provenance=provenance,
                    builder_id=self.builder_id,
                )
                signed_statement = sign_slsa_statement(
                    statement=statement,
                    private_key_pem=self.provenance_private_key,
                )
            else:
                provenance = create_release_provenance(
                    secret=self.provenance_secret,
                    release=release_preview,
                    attestation=verified_attestation,
                )
            release_metadata = {
                **base_metadata,
                "validation_attestation":(
                    dict(attestation)
                    if dual_signed
                    else verified_attestation
                ),
                "provenance":provenance,
                **(
                    {
                        "slsa_provenance":signed_statement,
                        "slsa_statement_sha256":
                            statement_digest(statement),
                    }
                    if asymmetric
                    else {}
                ),
            }

            _execute(
                db,
                self.backend,
                """
                INSERT INTO releases(
                    id, workflow_id, artifact_id, repository,
                    source_revision, workflow_generation,
                    validation_json, metadata_json, status,
                    rollback_of, created_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, 'promoted', NULL, ?)
                """,
                (
                    release_id,
                    workflow_id,
                    artifact_id,
                    workflow_row["repository"],
                    source_revision,
                    (
                        int(workflow_generation)
                        if workflow_generation is not None
                        else None
                    ),
                    json.dumps(validation, ensure_ascii=False),
                    json.dumps(release_metadata, ensure_ascii=False),
                    now,
                ),
            )
            previous_row = _execute(
                db,
                self.backend,
                """
                SELECT sequence, entry_hash
                FROM transparency_log
                ORDER BY sequence DESC
                LIMIT 1
                """,
            ).fetchone()
            sequence = (
                int(previous_row["sequence"]) + 1
                if previous_row is not None
                else 1
            )
            previous_hash = (
                previous_row["entry_hash"]
                if previous_row is not None
                else GENESIS_HASH
            )
            transparency_entry = create_transparency_entry(
                sequence=sequence,
                release_id=release_id,
                release_provenance_sha256=_canonical_sha256(
                    provenance
                ),
                slsa_statement_sha256=(
                    release_metadata.get(
                        "slsa_statement_sha256"
                    )
                ),
                previous_hash=previous_hash,
                created_at=now,
            )
            _execute(
                db,
                self.backend,
                """
                INSERT INTO transparency_log(
                    sequence, release_id, entry_json,
                    entry_hash, previous_hash, created_at
                )
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    sequence,
                    release_id,
                    json.dumps(
                        transparency_entry,
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    transparency_entry["entry_hash"],
                    previous_hash,
                    now,
                ),
            )
            self.backend.append_event(
                db,
                "release-promoted",
                {
                    "release_id":release_id,
                    "workflow_id":workflow_id,
                    "artifact_id":artifact_id,
                    "artifact_sha256":artifact_sha256,
                    "source_revision":source_revision,
                    "workflow_generation":workflow_generation,
                },
                repository=workflow_row["repository"],
            )
            self.backend.append_event(
                db,
                "release-provenance-signed",
                {
                    "release_id":release_id,
                    "validator_id":verified_attestation[
                        "validator_id"
                    ],
                    "provenance_signature":provenance["signature"],
                    "signature_schema":provenance["schema_version"],
                },
                repository=workflow_row["repository"],
            )
            row = _execute(
                db,
                self.backend,
                "SELECT * FROM releases WHERE id=?",
                (release_id,),
            ).fetchone()

        return self._row(row)

    def transparency_log(self) -> list[dict]:
        with self.backend.connect() as db:
            rows = _execute(
                db,
                self.backend,
                """
                SELECT entry_json
                FROM transparency_log
                ORDER BY sequence ASC
                """,
            ).fetchall()
        return [
            json.loads(row["entry_json"])
            for row in rows
        ]

    def verify_transparency(self) -> dict:
        return verify_transparency_chain(
            self.transparency_log()
        )

    def verify(self, release_id: str) -> dict:
        release = self.get(release_id)
        metadata = dict(release.get("metadata") or {})
        attestation = dict(
            metadata.get("validation_attestation") or {}
        )
        provenance = dict(metadata.get("provenance") or {})
        attestation_schema = str(
            attestation.get("schema_version") or ""
        )
        dual_signed = attestation_schema == DUAL_SCHEMA
        asymmetric = (
            dual_signed
            or attestation_schema.endswith(
                "/validation-attestation/v2"
            )
        )

        try:
            if dual_signed:
                if not self.trusted_validation_secrets:
                    raise RuntimeError(
                        "trusted validation HMAC keys not configured"
                    )
                if not self.trusted_validation_public_keys:
                    raise RuntimeError(
                        "trusted validation public keys not configured"
                    )
                if not self.provenance_public_key:
                    raise RuntimeError(
                        "release provenance public key not configured"
                    )
                verified_bundle = verify_dual_attestation(
                    attestation,
                    trusted_secrets=self.trusted_validation_secrets,
                    trusted_public_keys=(
                        self.trusted_validation_public_keys
                    ),
                    workflow_id=release["workflow_id"],
                    artifact_id=release["artifact_id"],
                    artifact_sha256=metadata["artifact_sha256"],
                    source_revision=release["source_revision"],
                    workflow_generation=release[
                        "workflow_generation"
                    ],
                    validation=release["validation"],
                    max_age_seconds=-1,
                )
                verified = verified_bundle["ed25519"]
                provenance_valid = verify_release_provenance_v2(
                    provenance,
                    public_key_pem=self.provenance_public_key,
                )
            elif asymmetric:
                if not self.trusted_validation_public_keys:
                    raise RuntimeError(
                        "trusted validation public keys not configured"
                    )
                if not self.provenance_public_key:
                    raise RuntimeError(
                        "release provenance public key not configured"
                    )
                verified = verify_validation_attestation_v2(
                    attestation,
                    trusted_public_keys=(
                        self.trusted_validation_public_keys
                    ),
                    workflow_id=release["workflow_id"],
                    artifact_id=release["artifact_id"],
                    artifact_sha256=metadata["artifact_sha256"],
                    source_revision=release["source_revision"],
                    workflow_generation=release[
                        "workflow_generation"
                    ],
                    validation=release["validation"],
                    max_age_seconds=-1,
                )
                provenance_valid = verify_release_provenance_v2(
                    provenance,
                    public_key_pem=self.provenance_public_key,
                )
            else:
                if not self.trusted_validation_secrets:
                    raise RuntimeError(
                        "trusted validation attestation keys "
                        "not configured"
                    )
                if not self.provenance_secret:
                    raise RuntimeError(
                        "release provenance signing secret "
                        "not configured"
                    )
                verified = verify_validation_attestation(
                    attestation,
                    trusted_secrets=self.trusted_validation_secrets,
                    workflow_id=release["workflow_id"],
                    artifact_id=release["artifact_id"],
                    artifact_sha256=metadata["artifact_sha256"],
                    source_revision=release["source_revision"],
                    workflow_generation=release[
                        "workflow_generation"
                    ],
                    validation=release["validation"],
                    max_age_seconds=-1,
                )
                provenance_valid = verify_release_provenance(
                    provenance,
                    secret=self.provenance_secret,
                )
        except (
            AttestationError,
            AsymmetricAttestationError,
            DualSignError,
            RuntimeError,
        ) as exc:
            return {
                "release_id":release_id,
                "valid":False,
                "reason":str(exc),
            }

        if asymmetric:
            signed_statement = dict(
                metadata.get("slsa_provenance") or {}
            )
            if self.require_trusted_builder:
                if self.builder_trust_policy is None:
                    return {
                        "release_id":release_id,
                        "valid":False,
                        "reason":"trusted builder policy not configured",
                    }
                slsa_valid = verify_trusted_slsa_statement(
                    signed_statement,
                    builder_policy=self.builder_trust_policy,
                    expected_repository=release["repository"],
                    expected_sha256=metadata["artifact_sha256"],
                )
            else:
                slsa_valid = verify_signed_slsa_statement(
                    signed_statement,
                    public_key_pem=self.provenance_public_key,
                    expected_sha256=metadata["artifact_sha256"],
                )
            if not slsa_valid:
                return {
                    "release_id":release_id,
                    "valid":False,
                    "reason":"invalid or untrusted SLSA provenance statement",
                }
            expected_statement_digest = statement_digest(
                dict(signed_statement.get("statement") or {})
            )
            if metadata.get("slsa_statement_sha256") != (
                expected_statement_digest
            ):
                return {
                    "release_id":release_id,
                    "valid":False,
                    "reason":"SLSA statement digest mismatch",
                }

        if not provenance_valid:
            return {
                "release_id":release_id,
                "valid":False,
                "reason":"invalid release provenance signature",
            }

        expected = {
            "release_id":release["id"],
            "workflow_id":release["workflow_id"],
            "artifact_id":release["artifact_id"],
            "repository":release["repository"],
            "artifact_sha256":metadata["artifact_sha256"],
            "source_revision":release["source_revision"],
            "workflow_generation":release["workflow_generation"],
            "validator_id":verified["validator_id"],
            "approval_key":metadata["approval"]["approval_key"],
            "approved_by":metadata["approval"]["approved_by"],
            "approval_role":metadata["approval"]["role"],
            "created_at":release["created_at"],
        }
        if asymmetric:
            expected.update({
                "validation_attestation_key_id":
                    verified["signature"]["key_id"],
                "validation_attestation_signature":
                    verified["signature"]["signature"],
            })
        else:
            expected["validation_attestation_signature"] = (
                verified["signature"]
            )

        for key, value in expected.items():
            if provenance.get(key) != value:
                return {
                    "release_id":release_id,
                    "valid":False,
                    "reason":
                        f"release provenance binding mismatch: {key}",
                }

        chain = self.verify_transparency()
        if not chain.get("valid"):
            return {
                "release_id":release_id,
                "valid":False,
                "reason":chain.get(
                    "reason",
                    "invalid transparency log",
                ),
            }
        entries = self.transparency_log()
        transparency_entry = next(
            (
                item for item in entries
                if item.get("release_id") == release_id
            ),
            None,
        )
        if transparency_entry is None:
            return {
                "release_id":release_id,
                "valid":False,
                "reason":"release missing from transparency log",
            }
        if transparency_entry.get(
            "release_provenance_sha256"
        ) != _canonical_sha256(provenance):
            return {
                "release_id":release_id,
                "valid":False,
                "reason":"transparency provenance digest mismatch",
            }

        signature = provenance["signature"]
        return {
            "release_id":release_id,
            "valid":True,
            "signature_scheme":(
                "hmac-sha256+ed25519"
                if dual_signed
                else (
                    "ed25519"
                    if asymmetric
                    else "hmac-sha256"
                )
            ),
            "validator_id":verified["validator_id"],
            "source_revision":release["source_revision"],
            "workflow_generation":release["workflow_generation"],
            "artifact_sha256":metadata["artifact_sha256"],
            "provenance_signature":signature,
            "transparency_sequence":
                transparency_entry["sequence"],
            "transparency_entry_hash":
                transparency_entry["entry_hash"],
            "transparency_root_hash":chain["root_hash"],
        }

    def rollback(
        self,
        release_id: str,
        *,
        reason: str,
        metadata: dict | None = None,
    ) -> dict:
        original = self.get(release_id)
        if original["status"] != "promoted":
            raise RuntimeError(
                "only promoted releases can be rolled back"
            )
        reason = str(reason or "").strip()
        if not reason:
            raise ValueError("rollback reason is required")

        rollback_id = uuid.uuid4().hex
        now = _now()
        with self.backend.transaction() as db:
            existing = _execute(
                db,
                self.backend,
                """
                SELECT id FROM releases
                WHERE rollback_of=? AND status='rollback'
                """,
                (release_id,),
            ).fetchone()
            if existing is not None:
                raise RuntimeError(
                    "release already rolled back by "
                    f"{existing['id']}"
                )

            _execute(
                db,
                self.backend,
                """
                INSERT INTO releases(
                    id, workflow_id, artifact_id, repository,
                    source_revision, workflow_generation,
                    validation_json, metadata_json, status,
                    rollback_of, created_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, 'rollback', ?, ?)
                """,
                (
                    rollback_id,
                    original["workflow_id"],
                    original["artifact_id"],
                    original["repository"],
                    original["source_revision"],
                    original["workflow_generation"],
                    json.dumps(
                        {
                            "status":"rollback",
                            "reason":reason,
                        },
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        dict(metadata or {}),
                        ensure_ascii=False,
                    ),
                    release_id,
                    now,
                ),
            )
            self.backend.append_event(
                db,
                "release-rollback-recorded",
                {
                    "rollback_id":rollback_id,
                    "release_id":release_id,
                    "reason":reason,
                },
                repository=original["repository"],
            )
            row = _execute(
                db,
                self.backend,
                "SELECT * FROM releases WHERE id=?",
                (rollback_id,),
            ).fetchone()

        return self._row(row)
