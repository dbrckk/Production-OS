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
- cross-repository reuse matching
- knowledge graph of repositories, profiles and capabilities
- persistent portfolio snapshots
- score regression detection
- JSON output suitable for agents and CI
- explicit handoff payload for `ai-dev-server`

## Architecture

```text
GitHub repositories
        |
        v
 Portfolio Scanner
        |
        v
 Evidence Model
        |
        +------> Project Classifier
        |
        +------> Capability Fingerprints
        |                 |
        |                 v
        |          Knowledge Graph
        |
        +------> Maturity / CI / Release Scoring
        |
        +------> Cross-Repo Reuse Matcher
        |
        +------> Snapshot / Regression Engine
        |
        +------> Action Generator
                       |
                       v
              Next Best Action
                       |
                       v
                ai-dev-server
```

## Quick start

Requires Python 3.11+.

```bash
git clone https://github.com/dbrckk/Production-OS
cd Production-OS
python -m pip install -e ".[dev]"

production-os scan --owner dbrckk
```

For higher GitHub API limits:

```bash
export GITHUB_TOKEN=...
production-os scan --owner dbrckk --json
```

Focus on the active portfolio:

```bash
production-os scan \
  --owner dbrckk \
  --include ai-dev-server deadline-zero Who-are-you Ai-trading xbow-perso Production-OS
```

## Capability fingerprints

Production-OS now extracts evidence-backed capabilities rather than only coarse repository metadata.

Examples currently recognized include:

- `android-play-billing`
- `android-admob`
- `android-consent`
- `android-play-release`
- `android-device-qa`
- `android-artifact-build`
- `github-actions-ci`
- `release-automation`
- `automated-tests`
- `multi-agent-orchestration`
- `autonomous-execution`
- `checkpoint-recovery`
- `audit-trail`
- `queued-workers`
- `docker-compose-deployment`
- `walk-forward-validation`
- `independent-risk-engine`
- `paper-broker`
- `backtesting`
- `experiment-registry`

Each fingerprint includes a confidence score and the evidence that triggered it.

## Knowledge graph

The JSON scan output contains a graph with:

```text
repository --classified_as--> profile
repository ----provides-----> capability
```

This is the foundation for later dependency, similarity, provenance and reuse relationships.

## Cross-repository reuse

Reuse matching is now capability-based. Production-OS only proposes a source when:

1. source and target belong to compatible project families;
2. the source capability has sufficient confidence;
3. the capability is marked portable;
4. the capability is absent from the target.

A task handoff to `ai-dev-server` now carries matching reuse candidates directly.

## CI priority

When the latest default-branch GitHub Actions run fails, is cancelled, times out or requires action:

- the CI score is reduced;
- a repair action is generated;
- restoring CI to green receives maximum operational priority.

Verification gates are never intentionally weakened to improve the score.

## Snapshots and regressions

Persist the current state:

```bash
production-os scan --owner dbrckk --snapshot artifacts/portfolio.json
```

Compare a later scan:

```bash
production-os scan \
  --owner dbrckk \
  --compare artifacts/portfolio.json \
  --snapshot artifacts/portfolio-next.json
```

A maturity regression is reported when a repository score drops by at least five points.

## ai-dev-server handoff

```bash
production-os scan --owner dbrckk --handoff
```

The v2 handoff contains:

- target repository
- prioritized task
- rationale
- acceptance criteria
- triggering evidence
- priority
- evidence-backed reuse candidates
- safety/verification constraints

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
- [ ] deeper source-code fingerprinting
- [ ] star-list retrieval bridge
- [ ] reusable component provenance
- [ ] dependency graph

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
