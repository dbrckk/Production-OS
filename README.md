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
- **source-symbol/component extraction**
- **component provenance**
- **component→dependency→capability graph**
- component-level cross-repository reuse matching
- persistent snapshots and regression detection
- live `dbrckk/star-list` ingestion and ranking
- portfolio-wide **Next Best Action**
- direct `ai-dev-server` handoff

## Component provenance

Production-OS now extracts selected source symbols from sampled files.

Supported first-pass extraction:

```text
Python
├── classes
├── public functions
└── imports

Kotlin / Java
├── classes
├── interfaces
├── objects
├── enum classes
└── imports
```

Each component carries:

```text
name
kind
path
language
confidence
dependencies
capability_hints
test_like
```

Example:

```text
component: BillingManager
path: app/src/.../BillingManager.kt
language: kotlin
dependencies:
  - BillingClient
capability_hints:
  - android-play-billing
```

## Knowledge graph V2

The graph now models:

```text
repository --contains------> component
component  --depends_on----> dependency
component  --implements----> capability
repository --provides------> capability
repository --classified_as-> profile
```

This makes provenance explicit: Production-OS can distinguish a capability declared at repository level from a concrete component that appears to implement it.

## Component-level reuse

Reuse recommendations now include candidate source components.

Example:

```text
Target:
deadline-zero

Missing capability:
android-play-billing

Source:
Who-are-you

Candidate components:
- BillingManager
  path: ...
  dependencies:
    - BillingClient

- PremiumRepository
  path: ...
```

The system still treats these as **adaptation candidates**, not blindly copyable code. Compatibility and tests remain mandatory.

## ai-dev-server handoff V5

```bash
production-os scan --owner dbrckk --handoff
```

The V5 handoff contains:

- prioritized task
- target repository
- trigger evidence
- acceptance criteria
- repo-level reuse candidates
- **reusable component candidates**
- component paths
- component dependencies
- live star-list references
- verification constraints

The policy is now:

```text
repair blockers first
        ↓
reuse internal component if suitable
        ↓
otherwise reuse internal architecture/pattern
        ↓
otherwise consult star-list
        ↓
adapt
        ↓
test
        ↓
verify
```

## Portfolio JSON V6

```bash
production-os scan --owner dbrckk --json
```

includes:

- repo assessments
- sampled source documents
- source signals
- components
- capability fingerprints
- ranked actions
- component-aware reuse opportunities
- knowledge graph V2
- regressions
- snapshots
- star-list status

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
- [ ] test-to-component linking
- [ ] call/import graph refinement
- [ ] adaptation risk scoring
- [ ] reusable boundary detection

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
- Adapt rather than blindly copy
- Test before promotion
- Human approval for destructive or externally privileged actions
