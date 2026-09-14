# Production-OS

Portfolio control plane for autonomous software production.

Production-OS sits above individual repositories and answers four questions:

1. **What is the real state of every project?**
2. **What should be worked on next?**
3. **Which proven implementation can be reused instead of rebuilt?**
4. **Has portfolio quality improved or regressed since the last scan?**

## Current capabilities

- GitHub portfolio discovery
- deterministic maturity scoring
- project classification
- GitHub Actions runtime-state ingestion
- bounded recursive source-tree sampling
- deep source fingerprinting
- capability fingerprinting
- source-symbol/component extraction
- component provenance
- component→dependency→capability graph
- **test-to-component linking**
- **adaptation risk scoring**
- component-level cross-repository reuse ranking
- persistent snapshots and regression detection
- live `dbrckk/star-list` ingestion and ranking
- portfolio-wide **Next Best Action**
- direct `ai-dev-server` handoff

## Adaptation risk

Every reusable component candidate is now scored from 0 to 100.

Signals include:

- source/target profile mismatch
- language mismatch
- dependency count
- linked tests
- direct capability match
- UI coupling
- whether the candidate is itself test code

Risk levels:

```text
0-25   low
26-50  medium
51-75  high
76-100 very-high
```

Low-risk and medium-risk non-test components are preferred in the handoff.

## Test-to-component linking

Production-OS links likely tests to components using:

- component name appearing in test symbol
- component name appearing in test path
- shared capability hints
- shared dependencies

Example:

```text
BillingManager
   ↓ tested_by
BillingManagerTest
```

Those tests are attached to the adaptation candidate so `ai-dev-server` can reuse or recreate the verification coverage.

## Component reuse ranking

Candidate ranking now considers:

```text
adaptation risk
      +
component confidence
      +
linked test coverage
      +
project family compatibility
      ↓
recommended component
```

A repository-level reuse score is also reduced when the only available component candidates have high adaptation risk.

## ai-dev-server handoff V6

```bash
production-os scan --owner dbrckk --handoff
```

The V6 contract adds:

- `adaptation_risk`
- `adaptation_risk_level`
- `adaptation_reasons`
- `linked_tests`
- `recommended_components`

The policy becomes:

```text
repair blockers first
        ↓
find internal component
        ↓
score adaptation risk
        ↓
prefer tested low-risk component
        ↓
otherwise reuse architecture/pattern
        ↓
otherwise consult star-list
        ↓
adapt + test + verify
```

## Portfolio JSON V7

The JSON portfolio now exposes the enriched component reuse data and the same adaptation metadata used by the handoff.

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
- [x] deep source fingerprinting
- [x] recursive source-tree sampling
- [x] live star-list ingestion
- [x] source-symbol/component extraction
- [x] reusable component provenance
- [x] first dependency graph
- [x] component-aware reuse handoff
- [x] test-to-component linking
- [x] adaptation risk scoring
- [ ] call/import graph refinement
- [ ] reusable boundary detection
- [ ] automatic adaptation plans

### P2
- [ ] autonomous scheduling
- [ ] portfolio resource allocation
- [ ] long-term trend history
- [ ] automatic component extraction plans
- [ ] mobile dashboard

## Design principles

- Evidence over assumptions
- Deterministic decisions before LLM judgment
- Fail closed on missing evidence
- Reuse before rebuild
- Prefer low-risk tested components
- Adapt rather than blindly copy
- Test before promotion
- Human approval for destructive or externally privileged actions
