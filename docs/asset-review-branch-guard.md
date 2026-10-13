# GitHub asset delivery: review-branch guard

## Confirmed code path (2026-10-12)

The public single-asset and batch entrypoints reject direct GitHub delivery
to main/master. The shared private `_deliver_produced_assets` helper did not
enforce that requirement itself. A direct caller could reach version-receipt
reads and `GitHubClient.commit_files` with `target_ref="main"`. This is a
source-confirmed guard omission, not proof of any past unauthorized push.

## Corrected behavior

The shared helper now rejects GitHub repository delivery to main/master
(including refs/heads forms) before any GitHub read/write. An explicit
non-default review branch still supports atomic asset/receipt commits and
expected-head protection. Worktree deliveries remain unaffected.

## Functional evidence

`integration/real_producer_bundle_smoke.py` now checks this path using an
offline recording GitHub client: all forbidden refs must fail without reading
or writing; the existing review-branch version 7-to-8 delivery must succeed.
CI must finish successfully at the exact commit SHA before qualification.

This is not a hosted worker-to-PR-to-game test, a commercial license
verification, or permission to deploy/merge.
