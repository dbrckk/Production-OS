# Release 56 Stable UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a visually polished, mobile-first Production OS dashboard on a fully qualified and unambiguous main branch.

**Architecture:** Keep the current server-rendered `DASHBOARD_HTML` and API contracts. Consolidate visual changes inside the existing dashboard UI, add contract tests for visual/responsive/accessibility invariants, and make repository/CI cleanup part of the release gate rather than introducing new runtime architecture.

**Tech Stack:** Python 3.11/3.12, stdlib HTTP control plane, embedded HTML/CSS/JavaScript dashboard, pytest, GitHub Actions, Docker.

**Spec:** `docs/superpowers/specs/2026-09-26-release-56-stable-ui.md`

## Global Constraints

- No new product feature, API endpoint, mutation, framework or external UI dependency.
- Preserve all six dashboard destinations and existing URL/deep-link behavior.
- Preserve Productions and worker-operation contracts from Releases 47–55.
- Primary responsive target is 360px–430px Android phones.
- No horizontal document overflow at 360px.
- Status must not rely only on color; visible keyboard focus and reduced-motion support are required.
- Release PR stays draft until every qualification gate is green on the final head.

## Review Focus

- 360px viewport: navigation, long repository names and action rows wrap without document overflow — pinned by responsive UI contract tests in Task 2.
- Keyboard-only navigation: every interactive control has a visible `:focus-visible` state — pinned by accessibility contract tests in Task 2.
- Reduced-motion preference: decorative transitions/animation are disabled — pinned by accessibility contract tests in Task 2.
- Missing/long optional metadata: cards retain hierarchy and do not clip content — pinned by existing dashboard rendering tests plus long-content assertions in Task 3.
- Existing operator controls: visual refactor does not rename/remove production or worker mutations — pinned by regression assertions in Task 3.

---

### Task 1: Lock the release surface and repository state

**Files:**
- Existing PR metadata
- Spec: `docs/superpowers/specs/2026-09-26-release-56-stable-ui.md`

**Interfaces:**
- Consumes: current `main` after Release 55.
- Produces: `feat/release-56-stable-ui` as the only active feature release candidate.

- [ ] **Step 1:** Enumerate open PRs and compare each stale head with `main`.
- [ ] **Step 2:** Close only PRs demonstrably superseded/diverged; never merge stale historical work for cleanup.
- [ ] **Step 3:** Confirm Release 56 branch starts from current `main` and record the spec/plan.

### Task 2: Define visual, responsive and accessibility contracts

**Files:**
- Modify: `tests/test_dashboard_ui.py`
- Modify or create focused dashboard UI test file following existing test organization.

**Interfaces:**
- Consumes: `DASHBOARD_HTML`.
- Produces: regression assertions for stable CSS hooks and preserved navigation/actions.

- [ ] **Step 1:** Add failing tests asserting CSS design tokens for layered surfaces, radii, shadows and control sizing.
- [ ] **Step 2:** Add failing tests asserting `:focus-visible` and `@media (prefers-reduced-motion: reduce)` coverage.
- [ ] **Step 3:** Add failing tests asserting the <=560px layout prevents horizontal document overflow and allows navigation/action wrapping.
- [ ] **Step 4:** Add assertions that all six existing dashboard views and production/worker control labels/hooks remain present.
- [ ] **Step 5:** Run focused tests and confirm RED for the new visual contracts.

### Task 3: Implement the stable visual system

**Files:**
- Modify: `src/production_os/dashboard_ui.py`
- Test: dashboard UI contract tests from Task 2.

**Interfaces:**
- Consumes: existing HTML IDs, JS handlers and server payloads unchanged.
- Produces: refined CSS/layout with no API or mutation changes.

- [ ] **Step 1:** Replace ad-hoc visual constants with expanded existing `:root` tokens for surfaces, borders, shadows, radii, control height and spacing.
- [ ] **Step 2:** Refine page shell, topbar, status indicators and navigation hierarchy while preserving IDs/handlers.
- [ ] **Step 3:** Harmonize cards, section headers, badges, empty/error/loading states and metadata typography.
- [ ] **Step 4:** Harmonize input/select/textarea and primary/secondary/destructive buttons with consistent touch size, disabled and focus states.
- [ ] **Step 5:** Refine Productions and worker cards so state remains text-labelled and visually scannable without changing classification or actions.
- [ ] **Step 6:** Add <=560px rules for wrapping, compact spacing and safe sticky offsets; ensure long content uses `overflow-wrap` rather than clipping.
- [ ] **Step 7:** Add reduced-motion override and visible keyboard focus treatment.
- [ ] **Step 8:** Run focused dashboard tests and confirm GREEN.

### Task 4: Regression qualification

**Files:**
- Modify only if a real regression is discovered; no scope expansion.

**Interfaces:**
- Consumes: final Release 56 implementation.
- Produces: a release candidate proven against existing runtime contracts.

- [ ] **Step 1:** Run focused dashboard/UI tests.
- [ ] **Step 2:** Run full unit suite.
- [ ] **Step 3:** Run Production E2E.
- [ ] **Step 4:** Run Python 3.11 and 3.12 CI compatibility jobs.
- [ ] **Step 5:** Run distribution build, wheel install, Docker and CLI smoke gates.
- [ ] **Step 6:** Fix only evidenced regressions and repeat affected + full gates.

### Task 5: Final review and stable merge

**Files:**
- PR diff/review metadata
- `main`

**Interfaces:**
- Consumes: final green Release 56 head.
- Produces: stable Release 56 baseline on `main`.

- [ ] **Step 1:** Compare branch to current `main`; update if main moved and rerun qualification.
- [ ] **Step 2:** Inspect final diff and confirm no unresolved review thread.
- [ ] **Step 3:** Confirm no obsolete open PR remains.
- [ ] **Step 4:** Mark Release 56 ready only after fresh green CI.
- [ ] **Step 5:** Squash merge with expected head SHA.
- [ ] **Step 6:** Verify merge commit is present on `main` and record it as the stable baseline.