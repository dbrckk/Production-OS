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
