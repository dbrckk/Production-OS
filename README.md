# Production-OS

Portfolio control plane for autonomous software production.

Production-OS sits above individual repositories and answers three questions:

1. **What is the real state of every project?**
2. **What should be worked on next?**
3. **Which proven implementation can be reused instead of rebuilt?**

It is designed to coordinate repositories such as `ai-dev-server`, product apps, research systems and shared knowledge bases.

## V0 capabilities

- GitHub portfolio discovery
- repository evidence collection
- deterministic maturity scoring
- release-readiness signals
- blocker/opportunity detection
- portfolio-wide **Next Best Action** ranking
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
        +------> Maturity Scoring
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

python -m production_os.cli scan --owner dbrckk
```

For higher GitHub API limits:

```bash
export GITHUB_TOKEN=...
python -m production_os.cli scan --owner dbrckk --json
```

To focus the scan:

```bash
python -m production_os.cli scan \
  --owner dbrckk \
  --include ai-dev-server deadline-zero Who-are-you Ai-trading xbow-perso
```

## Scoring

The V0 score is evidence-based and intentionally conservative. It currently considers:

- repository documentation
- automated tests
- CI/workflows
- release automation
- dependency/build manifests
- security policy / dependency automation
- license
- recent repository activity
- explicit roadmap/TODO signals

Unknown evidence does **not** receive points.

The score is not intended to claim product quality. It is a portfolio prioritization signal.

## Next Best Action

Each detected gap becomes a candidate action with:

- impact
- urgency
- risk reduction
- release proximity
- estimated effort

Production-OS ranks actions using a deterministic value/effort score. The highest-ranked action is emitted as the portfolio's next recommended task.

## ai-dev-server handoff

Use:

```bash
python -m production_os.cli scan --owner dbrckk --handoff
```

The command emits a machine-readable task contract containing:

- target repository
- task
- rationale
- acceptance criteria
- evidence that triggered the recommendation
- priority score

The contract is designed to be consumed by `ai-dev-server` rather than requiring another LLM to reinterpret free-form prose.

## Roadmap

### P0
- [x] Portfolio discovery
- [x] Evidence model
- [x] Maturity score
- [x] Next Best Action ranking
- [x] ai-dev-server handoff payload
- [ ] CI test gate
- [ ] persistent snapshots and score history

### P1
- [ ] cross-repository reuse detection
- [ ] release-readiness profiles by project type
- [ ] knowledge graph
- [ ] GitHub Actions status ingestion
- [ ] star-list retrieval bridge

### P2
- [ ] autonomous scheduling
- [ ] component extraction recommendations
- [ ] regression detection
- [ ] mobile dashboard

## Design principles

- Evidence over assumptions
- Deterministic decisions before LLM judgment
- Fail closed on missing evidence
- Reuse before rebuild
- Test before promotion
- Human approval for destructive or externally privileged actions
