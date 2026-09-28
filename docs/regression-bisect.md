# Regression bisect runtime

Production OS can locate the first bad commit between a known-good and known-bad
revision without rewriting history.

## CLI

```bash
production-os regression-bisect \
  --repository-root /srv/worktrees/job-123 \
  --good-sha <40-char-good-sha> \
  --bad-sha <40-char-bad-sha> \
  --test-command "python -m pytest tests/test_regression.py" \
  --timeout-seconds 900
```

The command returns a versioned JSON result containing the culprit SHA, tested
range, duration and a bounded output excerpt.

## Safety contract

The bisect runtime:

- requires full 40-character commit SHAs;
- requires the repository path to be exactly the Git top-level directory;
- refuses to run with uncommitted changes;
- verifies that both revisions resolve to commits;
- requires the known-good revision to be an ancestor of the known-bad revision;
- passes the test command as argv and never invokes a shell;
- enforces a bounded runtime;
- always runs `git bisect reset` after success or failure;
- never force-pushes, resets branches, deletes commits, or rewrites history.

It is intended to run inside an isolated Production OS worktree. The test
command must return Git bisect-compatible exit codes: 0 for good, 1-127 for bad,
and 125 to skip a commit.
