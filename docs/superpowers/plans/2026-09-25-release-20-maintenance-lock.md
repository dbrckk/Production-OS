# Production-OS Release 20 — Exclusive Database Maintenance Lock

## Goal

Prevent concurrent use of a SQLite Production-OS database by the control plane and future destructive maintenance operations.

## Scope

- SQLite only.
- Control-plane process acquires an exclusive server lock for its entire lifetime.
- A second control-plane process must fail fast while the kernel lock is held.
- Kernel lock ownership is tied to the open file descriptor and is released automatically when the process exits or crashes.
- The lock file may persist as harmless metadata; file existence alone never means the database is locked.
- PostgreSQL behavior is unchanged.

## Safety

- No time-based stale eviction for live server locks.
- POSIX `flock(LOCK_EX | LOCK_NB)` is the source of truth.
- A persistent metadata file records the current PID only for diagnostics.
- No lock-file unlink race is possible because release unlocks/closes the file descriptor instead of deleting the file.
- Lock path is derived server-side from the SQLite database path.
- No lock path/token is exposed through HTTP.

## Qualification

- second acquisition blocked while the first file descriptor owns the kernel lock
- release allows immediate reacquisition
- stale/malformed metadata file does not block acquisition when no kernel lock exists
- PostgreSQL returns a no-op lock context
- serve_control_plane acquires/releases lock around server lifetime
- full CI + Python 3.11/3.12 green before merge


## Implemented in current branch

- SQLite-only process-lifetime maintenance lock
- POSIX kernel flock as authoritative ownership
- persistent safe metadata with PID/purpose for diagnostics
- fail-fast second acquisition
- automatic kernel release on process exit/crash
- PostgreSQL no-op behavior
- serve_control_plane acquires the lock before opening the control plane and releases it after server_close
- direct ControlPlane unit tests remain unaffected
- lock semantics and server lifecycle regression coverage

## Remaining before Release 20 completion

- final CI qualification
- README documentation
- final diff review
- mark PR ready and merge after green head
