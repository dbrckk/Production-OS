# Bounded autonomous source qualification

The reviewed pilot objective is Git branch validity in
`src/production_os/worktree_contract.py::_slug`. Identifiers containing
`..`, or a workflow slug ending in `.lock`, currently produce references
that Git refuses. The worker may propose only the existing normalization
assignment followed by `.replace(".", "-")`. Digest inputs, limits,
attempt isolation and every other source byte must remain unchanged.

The default-branch review handoff verifies the exact branch tip and a
single-file, single-assignment diff before opening a draft PR and requesting
independent qualification CI. It does not check out candidate code with write
credentials. Qualification CI has read-only permissions, no model or operator
secrets, and checks actual Git worktree creation for eight identifier cases,
existing worktree/runner tests, compilation and distribution building.

Success requires the model-authored change, confirmed draft PR, and successful
qualification at the exact source commit. The normal PR CI is an additional
review gate. Neither the handoff nor the worker merges or deploys the source
change. A provider diagnostic alone does not establish autonomous delivery or
sustained free inference capacity.

## Exact-commit workflow dispatch and execution fence

The trusted handoff dispatches `production-os-source-qualification.yml`
with the reviewed `studio/mp-*` branch **and** a required `expected_sha`
input. The qualification workflow rejects unexpected repositories, branch
names, malformed SHAs and any difference between the dispatch-time GitHub
commit and that reviewed SHA **before** checking out or running candidate
code. `actions/checkout` uses the immutable SHA, not the movable branch
tip; the job additionally checks `git rev-parse HEAD` before compilation,
test execution or building a distribution.

This closes a race in which an accepted handoff dispatched a branch-only
qualification and a subsequent branch movement could cause that run to
validate the wrong revision. A failed guard must not be treated as a
qualified source change. Record the exact candidate SHA, associated draft
PR head and successful job conclusion together; a passing check for a
different SHA is not evidence of delivery.

This CI gate is not itself an inference call, a model-authored source
change, a verified end-to-end autonomous PR, a merge, or a deployment.
Provider capacity and production-device qualification remain separate.

## Canary 42 recovery and GitHub Actions permission boundary — 2026-10-23

The scheduled worker produced a genuine bounded one-line source commit
`39c7453d535873c2e0cce284301de78f723221b2` on
`studio/mp-7f6bd4bb55826074ad315ee8`. Independent GitHub comparison
confirmed a single changed file (`worktree_contract.py`, +1/-1). The
trusted handoff run [39910344503](https://github.com/dbrckk/Production-OS/actions/runs/39910344503)
stopped with HTTP 401/403, but its old shared error message did not identify
which GitHub API call failed. Do not assume PR creation is the source of
that status without a stage-specific log.

An operator-assisted recovery opened [draft PR #297](https://github.com/dbrckk/Production-OS/pull/297)
against the exact model-produced branch. Its creation is *not* autonomous.
The candidate Git blob `aa49158db360b3d922fbee59be8ed3de8d093340`
was independently rechecked locally using real Git: eight adversarial
worktree creations, eight valid refs and eight removals succeeded.
This local proof is distinct from the required independent GitHub
qualification workflow and ordinary PR CI.

For future approved handoffs, the trusted workflow first dispatches
read-only qualification with the validated immutable SHA, **before**
attempting draft PR creation. If PR creation is forbidden, the handoff
still fails explicitly, but a permitted Actions dispatch can finish
independently. Stage-specific failures now distinguish candidate ref
lookups, diff comparisons, existing PR lookups, qualification dispatch
and PR creation. No token contents or provider prompts are logged.

If the next failure explicitly says `draft PR creation` with HTTP 403,
review repository **Settings → Actions → General → Workflow permissions**:
the `GITHUB_TOKEN` needs `Pull requests: write`, and the repository
setting **Allow GitHub Actions to create and approve pull requests**
must permit creation. This is a repository-owner configuration; do not
change broad permissions or add credentials silently. Other operations
need their own stage diagnosis. No paid inference or quota increase
is part of this recovery.
