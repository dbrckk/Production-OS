# Bounded autonomous source qualification

## Next applicable objective: chronological reviewer decisions

The approved `production_os_latest_reviewer_state` task changes only the
`states` assignment in `src/production_os/github_work_state.py::_review_state`.
Current code retains a reviewer's old `CHANGES_REQUESTED` after their later
`APPROVED`. The permitted assignment keeps each identified reviewer's latest
meaningful decision in supplied chronological order, ignores comments/pending
reviews, and preserves other reviewers' outstanding refusals. Missing reviewer
identities remain separate. No CI, promotion policy or API code may change.

Both trusted handoffs compare the proposed assignment's AST against the
reviewed one-line policy. The model supplies the proposal; there is no local
patch fallback. The new read-only review-state qualification workflow pins
the reviewed commit before checkout and checks eleven chronological review
scenarios, existing GitHub reconciliation tests, compilation and builds.
The acceptance script fails on current production source. Its passing local
fixture is acceptance evidence only, not an actual model execution.

Infrastructure registration does not apply the source fix. A fresh hosted
canary must publish the model edit, open a real draft PR and independently
pass this workflow on the same SHA. Keep the resulting source PR unmerged.

The completed pilot objective was Git branch validity in
`src/production_os/worktree_contract.py::_slug`. Identifiers containing
`..`, or a workflow slug ending in `.lock`, previously produced references
that Git refused. The approved worker proposal was the existing normalization
assignment followed by `.replace(".", "-")`. Digest inputs, limits,
attempt isolation and every other source byte must remain unchanged.

The model-produced fix was merged through PR #297. The permission recovery
subsequently proved automatic PR creation (#302) and independent exact-source
qualification (run39956492079:54 tests,eight actual Git worktrees and builds).
PR #302 was closed as a duplicate. The original canary failed; this recovery
does not establish an uninterrupted fresh autonomous delivery.

Before dispatching qualification or opening a PR, the handoff now compares
the candidate source blob with the source blob at a pinned current main
commit. Equal blobs mean the source is already applied: it reports that
outcome and exits without creating a PR or dispatching CI. This matters after
a squash merge because GitHub's three-dot comparison can still show the old
patch against the merge base. Invalid blob evidence fails closed. This
already-applied outcome does not manufacture new review or CI evidence.

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

## Trusted PR event bridge (including legacy Studio branches)

A Studio candidate can predate changes to the qualification workflow. GitHub
may then evaluate `pull_request` triggers from a historical source branch,
so editing that PR does not guarantee the new workflow will launch.

`.github/workflows/trusted-studio-pr-qualification.yml` uses
`pull_request_target` from the trusted default branch. It does **not**
check out, install or execute candidate code, and never creates or merges a
PR. Its only write permission is `actions: write`, used to dispatch the
existing **read-only** `production-os-source-qualification.yml` with both
the vetted Studio branch and immutable `expected_sha`. This works even
when a legacy source branch predates the new default-branch workflow.

Before dispatch, the trusted script verifies the exact open PR number,
main-branch target, same-repository source branch, unchanged source commit,
single modified source file and exact authorized one-assignment patch.
HTTP errors fail closed without logging API credentials. The dispatched
qualification workflow remains `workflow_dispatch`-only to avoid
duplicate GitHub runner usage and preserves its own immutable SHA checks,
actual eight Git worktrees, existing runner tests, and build gate.

The event bridge is activated on `opened`, `reopened`, `synchronize`,
`edited` and `ready_for_review` for PRs against `main`. An operator can
edit the description of existing [draft PR #297](https://github.com/dbrckk/Production-OS/pull/297)
without changing its original model-authored commit, which requests a new
qualification from the default-branch bridge. Success still does not prove
fully autonomous PR creation, commercial model capacity or deployment.

## Exact-commit full CI for bot-created source PRs — 2026-10-24

A trusted handoff can open a draft PR using `GITHUB_TOKEN`, but GitHub
may not run the ordinary `pull_request` workflow automatically for a PR
created by that token. The [canary 2026-10-24 PR #305](https://github.com/dbrckk/Production-OS/pull/305)
had successful independent bounded source qualification at
`f2477fc6e795b5182772cd1ca5e97d8cfe4fac98`, while its PR CI
reported `action_required` rather than a successful set of CI jobs.
Those are different gates; qualification alone must never be reported as
passing the full application CI.

After verifying the approved one-line change and immutable source branch,
the default-branch handoff now dispatches the **canonical**
`.github/workflows/ci.yml` itself, with workflow `ref: main` and inputs
`expected_sha` and `source_branch`. Running the workflow definition from
trusted `main` works even for old model-authored branches that predate
new CI input declarations. All three jobs check out the candidate
**by SHA**, with credentials not persisted, then fail closed unless the
event came from `main`, the candidate SHA is well formed, the source
branch belongs to the reserved Studio namespace, and
`git rev-parse HEAD` matches the expected SHA. The reviewed branch tip
is checked again before dispatch.

Only successful canonical CI on the exact candidate SHA qualifies
**application tests**; a successful API dispatch is not a successful CI
run. The source PR stays a draft, is never auto-merged, and no Render
deployment is implied. For legacy Studio PRs, the existing trusted `pull_request_target`
bridge can also dispatch the canonical full CI after independently validating
the PR's exact head and authorized patch. A metadata-only edit can invoke
that bridge without changing model-authored source. Its CI dispatch uses
`ref: main` and both immutable source inputs, just like the original
review handoff. The two trusted dispatchers provide recovery if the PR
was created before this workflow existed. A separate successful run
and exact checked-out SHA must be confirmed; neither dispatcher marks
a candidate verified merely by submitting an API request.

### Candidate-specific CI concurrency

The default-branch trusted workflow and a normal manual CI run can have the
same `github.sha` even though the first checks out a different approved
source commit. The canonical CI concurrency group therefore selects
`pull_request.number` for regular PRs, then `inputs.expected_sha` for
immutable Studio source dispatches, and finally `github.sha` for ordinary
push or manual builds. This prevents an unrelated `main` verification from
cancelling a vetted source proof while retaining same-commit supersession.
