# Release 56 — Stable UI

## Goal

Produce a single fully merged, release-candidate-quality Production OS main branch and make the dashboard feel like a finished production product without changing its backend authority model or adding new product features.

## Product direction

Release 56 is a stabilization and presentation release, not a feature release. The dashboard keeps the existing server-rendered HTML/CSS/JavaScript architecture and all current API/mutation contracts. No framework migration and no new runtime dependency are allowed.

The visual direction is a premium dark operations dashboard: restrained, dense, legible, mobile-first, and clearly stateful rather than decorative.

## Stable repository state

- Start from current main after Release 55.
- Close obsolete open PRs that are superseded by later merged releases rather than attempting to merge divergent historical work.
- Release 56 must finish with no ambiguous feature PR left open.
- Do not merge any stale branch merely to achieve a zero-open-PR count.
- The Release 56 PR itself remains draft until all qualification gates pass.

## Visual system

Retain the current dark identity while strengthening hierarchy.

### Foundations

- Refine background/surface/border contrast so page, cards and elevated controls read as distinct layers.
- Use one restrained blue accent for primary navigation/action focus.
- Preserve green/yellow/red semantics for healthy/warning/error states.
- Standardize card radius, control radius, shadows, spacing and transition behavior through CSS variables.
- Preserve readable contrast and visible keyboard focus.
- Respect prefers-reduced-motion.

### Header and navigation

- Make the product identity and current control-plane state visually distinct.
- Reduce the visual weight of inactive navigation items.
- Make the selected section obvious without relying only on text color.
- Keep all six existing dashboard destinations and URL behavior.
- On narrow Android-sized screens, navigation must remain reachable without horizontal page overflow.

### Dashboard hierarchy

- Make top-level system health/status visually scannable before detailed cards.
- Improve section headers, badges and metadata hierarchy.
- Harmonize empty, loading, success and error states.
- Keep existing information and operator actions; this release may reorganize presentation but must not hide a required control.

### Forms and actions

- Unify input/select/textarea/button heights and focus treatment.
- Distinguish primary, secondary and destructive actions consistently.
- Preserve existing disabled states and mutation confirmation behavior.
- Touch targets should remain practical on mobile.

### Productions and worker operations

- Keep the searchable/shareable Productions workflow introduced by Releases 47–48.
- Keep worker active/paused/draining controls introduced by Release 55.
- Improve visual differentiation of active work, review-required work, attention/problems and completed work without changing server classification.

## Responsive behavior

Primary target widths: 360px–430px Android phones, then tablet/desktop.

- No horizontal document overflow at 360px.
- Main actions remain reachable without hover.
- Dense metadata wraps rather than clipping.
- Sticky elements must not obscure focused/deep-linked content.
- Desktop should use available width without turning every card into a full-width wall of text.

## Accessibility and resilience

- Keep semantic buttons/inputs and existing labels.
- Add visible :focus-visible treatment.
- Do not encode status solely by color.
- Respect prefers-reduced-motion.
- Dashboard must remain usable when optional data fields are absent or long repository/project names wrap.

## Non-goals

- No React/Vue/Svelte migration.
- No new API endpoint or mutation.
- No backend lifecycle redesign.
- No new external font, icon or UI dependency.
- No feature expansion beyond presentation/stability fixes required by qualification.

## Qualification gate

Release 56 can merge only when all of the following are fresh on its final head:

- focused dashboard UI contract tests green;
- full unit suite green;
- Python 3.11 green;
- Python 3.12 green;
- Production E2E green;
- distribution build green;
- wheel install smoke green;
- Docker smoke green;
- CLI smoke green;
- final PR diff reviewed with no unresolved review thread;
- branch aligned with current main;
- no obsolete open PR remains.

After merge, verify the merge commit is present on main and treat that commit as the stable Release 56 baseline.