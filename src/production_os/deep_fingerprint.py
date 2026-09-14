from __future__ import annotations

from dataclasses import dataclass

from .models import RepoEvidence


@dataclass(frozen=True, slots=True)
class SourceSignal:
    kind: str
    value: str
    confidence: float
    evidence: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "value": self.value,
            "confidence": self.confidence,
            "evidence": list(self.evidence),
        }


def analyze_source_evidence(e: RepoEvidence) -> list[SourceSignal]:
    signals: list[SourceSignal] = []
    combined = "\n".join(e.source_documents.values()).lower()

    def add(kind: str, value: str, confidence: float, evidence: list[str]) -> None:
        signals.append(
            SourceSignal(kind, value, round(confidence, 2), tuple(evidence))
        )

    patterns = [
        ("android-library", "play-billing", ("com.android.billingclient", "billingclient"), 0.99),
        ("android-library", "google-mobile-ads", ("com.google.android.gms:play-services-ads", "google mobile ads"), 0.99),
        ("android-library", "ump-consent", ("user-messaging-platform", "consentinformation"), 0.99),
        ("python-library", "fastapi", ("fastapi",), 0.98),
        ("python-library", "celery", ("celery",), 0.98),
        ("python-library", "redis", ("redis",), 0.95),
        ("python-library", "optuna", ("optuna",), 0.98),
        ("python-library", "vectorbt", ("vectorbt",), 0.98),
        ("python-library", "yfinance", ("yfinance",), 0.98),
        ("python-library", "pytest", ("pytest",), 0.99),
        ("infra", "docker-compose", ("docker compose", "docker-compose"), 0.96),
        ("ci", "github-actions", ("uses: actions/",), 0.98),
    ]

    for kind, value, needles, confidence in patterns:
        if any(needle in combined for needle in needles):
            add(
                kind,
                value,
                confidence,
                [
                    f"source contains {needle}"
                    for needle in needles
                    if needle in combined
                ],
            )

    return sorted(
        signals,
        key=lambda item: (-item.confidence, item.kind, item.value),
    )
