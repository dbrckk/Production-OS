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
