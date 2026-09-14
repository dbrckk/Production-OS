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
- deterministic maturity scoring
- project classification
- GitHub Actions runtime-state ingestion
- capability fingerprinting with confidence + evidence
- bounded recursive source-tree sampling
- deep source fingerprinting from manifests, workflows, infrastructure and sampled source files
- cross-repository reuse matching
- knowledge graph
- persistent snapshots and regression detection
- **live `dbrckk/star-list` catalog ingestion**
- star-list ranking by capability match, repository score and tier metadata
- portfolio-wide **Next Best Action**
- direct `ai-dev-server` handoff

## Recursive source sampling

Production-OS uses GitHub's recursive tree endpoint to inspect repository structure without walking every directory with individual API calls.

Sampling is deliberately bounded:

```text
max depth          3
max sampled files  40
max chars/file     12,000
```

Priority directories include:

```text
src
app
core
android
backend
studio
tests
lib
server
services
packages
```

Generated/build/vendor directories and binary artifacts are excluded.

The sampled source is used only as evidence; repository content is treated as untrusted input.

## Live star-list integration

By default:

```bash
production-os scan --owner dbrckk
```

also reads:

```text
dbrckk/star-list
└── catalog.json
```

The catalog already exposes:

- repository score
- tier
- category
- domain
- capabilities
- alternatives
- complements
- best-for guidance
- avoid-when guidance
- runtime/resource/integration metadata

Production-OS ranks relevant external references using:

```text
capability match
      +
star-list score
      +
tier/domain metadata
      ↓
ranked external references
```

The integration can be disabled:

```bash
production-os scan --owner dbrckk --no-star-list
```

or redirected:

```bash
production-os scan \
  --owner dbrckk \
  --star-list-repo dbrckk/star-list \
  --star-list-path catalog.json
```

## Decision pipeline

```text
Target repository
      ↓
metadata + CI state
      ↓
recursive source sampling
      ↓
capabilities + source signals
      ↓
internal portfolio reuse search
      ↓
live star-list ranking
      ↓
Next Best Action
      ↓
ai-dev-server
      ↓
implementation + verification
```

Internal reuse remains preferred over external adoption.

## ai-dev-server handoff V4

```bash
production-os scan --owner dbrckk --handoff
```

The V4 task contract contains:

- target repository
- prioritized task
- rationale
- acceptance criteria
- triggering evidence
- priority
- internal reuse candidates
- live star-list external-reference candidates
- verification and safety constraints

The core policy is:

```text
repair blockers first
reuse internal implementation before rebuilding
use evidence-backed external references when needed
verify before completion
```

## Portfolio JSON V5

```bash
production-os scan --owner dbrckk --json
```

includes:

- repository assessments
- sampled source evidence
- capability fingerprints
- source signals
- ranked actions
- cross-repo reuse opportunities
- knowledge graph
- regressions
- snapshot
- star-list catalog status and repository count

## Roadmap

### P0
- [x] Portfolio discovery
- [x] evidence model
- [x] maturity score
- [x] Next Best Action
- [x] ai-dev-server handoff
- [x] CI gate
- [x] snapshots
- [x] regressions
- [x] project classification

### P1
- [x] GitHub Actions state
- [x] capability fingerprints
- [x] knowledge graph
- [x] cross-repository reuse
- [x] profile-aware scoring
- [x] deep source fingerprinting
- [x] recursive source-tree sampling
- [x] live star-list catalog ingestion
- [ ] reusable component provenance
- [ ] dependency graph
- [ ] source-symbol/component extraction
- [ ] risk-aware automatic adaptation plans

### P2
- [ ] autonomous scheduling
- [ ] portfolio resource allocation
- [ ] trend history
- [ ] component extraction recommendations
- [ ] mobile dashboard

## Design principles

- Evidence over assumptions
- Deterministic decisions before LLM judgment
- Fail closed on missing evidence
- Reuse before rebuild
- Test before promotion
- Human approval for destructive or externally privileged actions
