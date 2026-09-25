# Production-OS Release 20 — Exclusive Database Maintenance Lock

## Goal

Prevent concurrent use of a SQLite Production-OS database by the control plane and future destructive maintenance operations.

## Scope

- SQLite only.
- Control-plane process acquires an exclusive server lock for its entire lifetime.
- A second control-plane process must fail fast while the lock owner PID is alive.
- Truly orphaned locks may be reclaimed when the recorded PID no longer exists.
- Lock release removes the file only if the releasing process still owns the recorded token.
- PostgreSQL behavior is unchanged.

## Safety

- No time-based stale eviction for live server locks.
- PID liveness is checked before reclaiming.
- Atomic O_EXCL lock creation.
- Random owner token prevents one process from deleting a replacement lock.
- Lock path is derived server-side from the SQLite database path.
- No lock path/token is exposed through HTTP.

## Qualification

- second acquisition blocked while owner PID alive
- orphaned dead PID reclaimed
- malformed orphan lock reclaimed
- owner-token mismatch prevents accidental deletion
- PostgreSQL returns a no-op lock context
- serve_control_plane acquires/releases lock around server lifetime
- full CI + Python 3.11/3.12 green before merge
