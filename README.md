# Production-OS

Portfolio control plane for autonomous software production.

Production-OS sits above individual repositories and answers four questions:

1. **What is the real state of every project?**
2. **What should be worked on next?**
3. **Which proven implementation can be reused instead of rebuilt?**
4. **Has portfolio quality improved or regressed since the last scan?**

It is designed to coordinate repositories such as `ai-dev-server`, Android products, research systems and shared knowledge bases.

## Current capabilities

- GitHub portfolio discovery
- repository evidence collection
- deterministic maturity scoring
- automatic project classification
- GitHub Actions runtime-state ingestion
- portfolio-wide **Next Best Action** ranking
- capability fingerprinting with confidence + evidence
- **deep source fingerprinting** from manifests, workflows and infrastructure files
- cross-repository reuse matching
- knowledge graph of repositories, profiles and capabilities
- persistent portfolio snapshots
- score regression detection
- first external-reference bridge for `star-list`-style recommendations
- JSON output suitable for agents and CI
- explicit handoff payload for `ai-dev-server`

## Deep source fingerprinting

Production-OS now reads selected high-signal files when present:

- `pyproject.toml`
- `requirements.txt`
- `package.json`
- `build.gradle(.kts)`
- `settings.gradle.kts`
- `pom.xml`
- `Cargo.toml`
- `go.mod`
- Docker/Compose files
- GitHub Actions workflows

This produces source-level signals such as:

- Android Play Billing dependency
- Google Mobile Ads
- UMP consent
- FastAPI
- Celery
- Redis
- Optuna
- vectorbt
- yfinance
- pytest
- Docker Compose
- GitHub Actions

These signals are exported separately from README-derived capabilities so downstream agents can distinguish declared features from implementation evidence.

## External reference bridge

The handoff contract can now attach external reference candidates for missing capabilities.

Examples:

```text
backtesting
  -> QuantConnect/Lean
  -> nautechsystems/nautilus_trader
  -> polakowo/vectorbt

dependency-automation
  -> dependabot/dependabot-core
  -> renovatebot/renovate
```

The bridge is intentionally conservative: it only maps known capabilities to known reference repositories. A later step will read the actual `star-list` catalog and filter by its scoring/ranking metadata.

## ai-dev-server handoff V3

```bash
production-os scan --owner dbrckk --handoff
```

The v3 handoff contains:

- target repository
- prioritized task
- rationale
- acceptance criteria
- triggering evidence
- priority
- evidence-backed reuse candidates
- external reference candidates
- safety/verification constraints

Important constraints include:

```text
reuse_before_rebuild = true
prefer_evidence_backed_references = true
verify_before_completion = true
```

## Roadmap

### P0
- [x] Portfolio discovery
- [x] Evidence model
- [x] Maturity score
- [x] Next Best Action ranking
- [x] ai-dev-server handoff
- [x] CI test gate
- [x] persistent snapshots
- [x] regression detection
- [x] project classification

### P1
- [x] GitHub Actions status ingestion
- [x] capability fingerprints
- [x] first knowledge graph
- [x] capability-based cross-repository reuse
- [x] profile-aware release scoring
- [x] first deep source fingerprinting
- [x] first external-reference bridge
- [ ] live `star-list` catalog ingestion
- [ ] reusable component provenance
- [ ] dependency graph
- [ ] nested source-tree sampling

### P2
- [ ] autonomous scheduling
- [ ] portfolio budget/resource allocation
- [ ] component extraction recommendations
- [ ] trend/regression history across many snapshots
- [ ] mobile dashboard

## Design principles

- Evidence over assumptions
- Deterministic decisions before LLM judgment
- Fail closed on missing evidence
- Reuse before rebuild
- Test before promotion
- Human approval for destructive or externally privileged actions
