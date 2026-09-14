# Production-OS

Portfolio control plane for autonomous software production.

Production-OS now manages portfolio state, reuse, compatibility, and validation readiness before handing work to `ai-dev-server`.

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
- reusable boundary detection
- automatic adaptation plans
- **target-side dependency compatibility checks**
- **automatic validation-plan generation**
- live `dbrckk/star-list` ranking
- portfolio-wide **Next Best Action**
- direct `ai-dev-server` handoff

## Target dependency compatibility

For every adaptation plan, Production-OS now compares required dependencies against target evidence.

Each dependency is classified as:

```text
available
missing-or-unverified
```

The result is added to the adaptation plan as:

```text
dependency_compatibility
missing_dependencies
compatible_for_adaptation
```

A plan is considered directly adaptable only when its risk remains acceptable and the unresolved dependency set stays limited.

## Automatic validation plan

Every adaptation plan now carries an ordered validation checklist.

Depending on the capability and target, this can include:

```text
1. resolve dependencies
2. compile/build
3. port/recreate linked unit tests
4. Android APK/AAB build
5. emulator/device smoke test
6. capability-specific validation
7. CI green
8. regression suite
```

Android Play Billing additionally requires explicit purchase, acknowledgement, restore and entitlement verification.

## ai-dev-server handoff V8

```bash
production-os scan --owner dbrckk --handoff
```

The V8 contract contains:

- reuse candidates
- reusable components
- recommended low-risk components
- adaptation plans
- dependency compatibility
- missing dependencies
- validation plans
- executable adaptation plans
- external star-list references

Promotion constraints now include:

```text
resolve_missing_dependencies_before_promotion = true
complete_validation_plan_before_promotion = true
```

## Decision pipeline

```text
Next Best Action
      ↓
internal capability search
      ↓
component extraction
      ↓
adaptation risk
      ↓
reusable boundary
      ↓
dependency compatibility
      ↓
validation plan
      ↓
executable adaptation plan
      ↓
ai-dev-server
      ↓
implementation
      ↓
tests / device / CI / regression
```

## Portfolio JSON V9

The portfolio output exposes the same compatibility and validation information used by the V8 handoff.

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
- [x] target dependency compatibility
- [x] automatic validation plans
- [ ] call/import graph refinement
- [ ] stronger dependency/version compatibility
- [ ] validation-result ingestion

### P2
- [ ] autonomous scheduling
- [ ] portfolio resource allocation
- [ ] long-term trend history
- [ ] automatic execution feedback loop
- [ ] mobile dashboard

## Design principles

- Evidence over assumptions
- Deterministic decisions before LLM judgment
- Fail closed on missing evidence
- Reuse before rebuild
- Prefer low-risk tested components
- Adapt rather than blindly copy
- Validate before promotion
- Human approval for destructive or externally privileged actions
