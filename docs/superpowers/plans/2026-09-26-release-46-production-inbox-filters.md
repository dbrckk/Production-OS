# Release 46 — Prioritized production inbox filters

## Goal

Make the persistent multi-production inbox useful as an operator work queue on mobile without introducing new mutation semantics.

## Server contract

GET /v1/dashboard/productions accepts:

- limit
- filter = all | active | review | problems | completed

The service:

1. reconstructs eligible persistent Managed Projects and runtime state;
2. computes global phase counts before filtering;
3. classifies each item into an operator category;
4. orders categories by problems → review → active → completed;
5. orders items within a category by recent activity first;
6. applies the selected filter;
7. applies the response limit last.

Unknown filters fail closed with ValueError / HTTP 400 through the existing dashboard error path.

## Mobile UI

The Productions view exposes:

- Toutes
- Actives
- À revoir
- Problèmes
- Terminées

The selected category is sent to the server. Summary totals remain global.

Existing production actions remain unchanged:

- cancel
- retest / verify
- mark DONE

No new mutation endpoint is introduced.

## Regression scope

- server-side category filtering
- totals independent from selected filter
- invalid-filter rejection
- operator-priority ordering
- recent-first ordering within equal priority
- post-sort response limiting
- mobile filter controls and request parameter
- existing production mutation contracts remain present

## Architectural constraint

Release 46 must be integrated directly into dashboard_service.py, control_plane.py and dashboard_ui.py. No wrapper modules, thread-local request propagation or parse_qs monkey-patching are allowed.

## Completion gate

- Python 3.11 green
- Python 3.12 green
- non-E2E suite green
- Production E2E green
- distribution build green
- wheel install smoke green
- Docker smoke green
- CLI smoke green
- final PR diff contains no legacy wrapper modules
