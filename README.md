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
- test-to-component linking
- adaptation risk scoring
- **reusable boundary detection**
- **automatic adaptation plans**
- component-level cross-repository reuse ranking
- persistent snapshots and regression detection
- live `dbrckk/star-list` ingestion and ranking
- portfolio-wide **Next Best Action**
- direct `ai-dev-server` handoff

## Reusable boundary detection

Production-OS now separates component reuse into four explicit buckets:

```text
COPY / ADAPT
RECREATE LOCALLY
REUSE TESTS
DO NOT COPY
```

A component is excluded from direct reuse when it is too risky, test-only, or strongly UI-coupled.

Example:

```text
COPY / ADAPT
- BillingManager

RECREATE LOCALLY
- BillingClient binding
- target entitlement store

REUSE TESTS
- BillingManagerTest

DO NOT COPY
- PremiumScreen
- app-specific UI
```

## Automatic adaptation plans

Every reuse opportunity can now generate an adaptation plan containing:

- source repository
- target repository
- capability
- strategy
- components to adapt
- dependencies to recreate/bind locally
- tests to reuse
- components not to copy
- target-specific changes
- overall adaptation risk

Strategies:

```text
component-adaptation
architecture-pattern-only
```

When no safe component boundary exists, Production-OS automatically falls back to architecture-pattern reuse rather than recommending a risky copy.

## ai-dev-server handoff V7

```bash
production-os scan --owner dbrckk --handoff
```

The V7 contract adds:

- `adaptation_plans`
- explicit `copy_or_adapt`
- explicit `recreate`
- explicit `reuse_tests`
- explicit `do_not_copy`
- explicit `target_changes`
- overall plan risk

The execution policy is now:

```text
repair blockers
        ↓
find internal capability
        ↓
find concrete components
        ↓
score adaptation risk
        ↓
detect reusable boundary
        ↓
generate adaptation plan
        ↓
reuse tests
        ↓
consult star-list only if needed
        ↓
implement
        ↓
verify
```

## Portfolio JSON V8

The portfolio output now carries adaptation plans inside reuse opportunities, making the same plan available to dashboards, agents and later scheduling logic.

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
- [x] reusable boundary detection
- [x] automatic adaptation plans
- [ ] call/import graph refinement
- [ ] target-side dependency compatibility checks
- [ ] automatic validation-plan generation

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
