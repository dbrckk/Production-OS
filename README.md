# Production-OS

Portfolio control plane for autonomous software production.

Production-OS sits above individual repositories and answers four questions:

1. **What is the real state of every project?**
2. **What should be worked on next?**
3. **Which proven implementation can be reused instead of rebuilt?**
4. **Has portfolio quality improved or regressed since the last scan?**

It is designed to coordinate repositories such as `ai-dev-server`, product apps, research systems and shared knowledge bases.

## Current capabilities

- GitHub portfolio discovery
- repository evidence collection
- deterministic maturity scoring
- automatic project classification
- release-readiness signals
- blocker/opportunity detection
- portfolio-wide **Next Best Action** ranking
- cross-repository reuse opportunities
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
        +------> Maturity / Release Scoring
        |
        +------> Cross-Repo Reuse Detector
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

## Snapshots and regressions

Persist the current state:

```bash
production-os scan --owner dbrckk --snapshot artifacts/portfolio.json
```

Compare a later scan against it:

```bash
production-os scan \
  --owner dbrckk \
  --compare artifacts/portfolio.json \
  --snapshot artifacts/portfolio-next.json
```

A regression is reported when a repository maturity score drops by at least five points.

## Project profiles

The classifier currently recognizes:

- `android-app`
- `android-game`
- `automation-platform`
- `quant-research`
- `python-service`
- `node-project`
- `knowledge-base`
- `generic`

Classification is evidence-based and reports a confidence score and triggering signals.

## Cross-repository reuse

Production-OS searches related repositories for already-proven capabilities such as:

- CI workflows
- release workflows
- test baselines
- security policy
- dependency automation

A reuse opportunity is emitted only when the source exposes evidence for the capability and the target does not.

## Scoring

The score is intentionally conservative. It considers:

- documentation
- automated tests
- CI/workflows
- release automation
- dependency/build manifests
- security policy
- dependency automation
- license
- recent activity

Unknown evidence does **not** receive points.

The score measures operational maturity for prioritization. It does not claim user-facing product quality.

## Next Best Action

Each detected gap becomes a candidate action with:

- impact
- urgency
- risk reduction
- release proximity
- estimated effort

Production-OS ranks actions deterministically using value divided by effort.

## ai-dev-server handoff

```bash
production-os scan --owner dbrckk --handoff
```

The command emits a machine-readable task contract containing:

- target repository
- task
- rationale
- acceptance criteria
- triggering evidence
- priority
- safety/verification constraints

This contract is designed for direct consumption by `ai-dev-server`.

## Roadmap

### P0
- [x] Portfolio discovery
- [x] Evidence model
- [x] Maturity score
- [x] Next Best Action ranking
- [x] ai-dev-server handoff payload
- [x] CI test gate
- [x] persistent snapshots
- [x] regression detection
- [x] project classification

### P1
- [x] first cross-repository reuse detector
- [x] first profile-aware release scoring
- [ ] GitHub Actions status ingestion
- [ ] deeper repository evidence graph
- [ ] knowledge graph
- [ ] star-list retrieval bridge
- [ ] reusable component fingerprinting

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
