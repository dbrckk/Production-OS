# Render Free deployment for Production-OS (existing Neon database)

The operator designated the second Render account **studycall12@gmail.com**
(workspace `My Workspace`) as the **permanent Production-OS host** on
2026-10-31. The target Free service already exists:
`production-os-control-plane` (`srv-dbj1hiuc6qcc73b7afvg`),
https://production-os-control-plane.onrender.com. Its repository is
`dbrckk/Production-OS`, branch `main`, region Frankfurt, using
`Dockerfile.free-hosting`. A secure Neon `DATABASE_URL` was set from the
existing `production-os` project, database `production_os`; no database
was recreated.

**Cutover is NOT complete or operationally qualified.** The initial Docker
image built successfully on 2026-10-31, but the first deployment failed
closed at startup because `PRODUCTION_OS_WORKER_TOKEN` was not yet present.
`PRODUCTION_OS_OPERATOR_TOKEN` must also be provisioned for authenticated
operation. `GITHUB_TOKEN` is optional: without it the existing scheduled
Actions worker provides a best-effort scheduled polling fallback rather
than immediate dispatch; GitHub does not guarantee a five-minute cadence. New-service auto-deploy is
temporarily **off** to avoid wasting Free quota on repeated GitHub pushes
before authentication and readiness are verified. This document records
the target destination, not a successful switchover.

The version-controlled `render.yaml` is a *future Blueprint template* and
does not automatically update or configure the new manually created Render
service. Never create a duplicate controller with the Blueprint. The old
`production-os1` on the original account was resumed by Render on
2026-11-01 after an earlier Free-quota suspension; it is not the future
destination and must not be allowed to run concurrently with the new
controller on the same persistent database.

If explicitly deployed, `render.yaml` creates exactly
**one Render Free web service**. It does not create a database, a paid service,
a persistent disk, a cron job or an extra worker. GitHub Actions remains the
execution tier. Prior free-host alternatives are archived as a fallback in
`docs/free-hosting-migration.md`; **do not deploy them**.

## Verified existing architecture

- Source: `dbrckk/Production-OS`, `main` (Render builds
  `Dockerfile.free-hosting`, running `scripts/render-start.py`).
- Worker: `dbrckk/ai-dev-server`, GitHub Actions
  `production-os-actions-worker.yml` (cron `*/5 * * * *`; GitHub-hosted
  scheduled runs can be delayed or skipped, so this is not a five-minute SLA).
- Persistent database: existing Neon project **production-os**, database
  **production_os**, branch **production**, region **Frankfurt**.
  Preserve the original database; it has application tables and historical
  workflows/jobs. A fresh empty PostgreSQL database **is not a migration**.
- API: port **8787**. Render's frequent health checks use the lightweight
  **GET /healthz** endpoint (process liveness; no DB connection).
  GitHub Actions workers and operational verification must still use
  **GET /readyz** (real PostgreSQL `SELECT 1`), followed by authenticated
  API checks. A healthy process does not mean an available database.
  This separation reduces unnecessary Neon compute wake-ups and avoids
  restarting the API for transient database failures.
  Docs: https://render.com/docs/health-checks and
  https://neon.com/docs/introduction/scale-to-zero
  Protected routes include **GET /v1/workflows**.
- Render startup **rejects SQLite paths, hostless PostgreSQL URLs, missing
  database names, malformed ports, and URI schemes other than
  `postgresql://` and `postgres://`** before creating authentication
  files. A hostless connection may otherwise fall back to a local socket or
  environment defaults instead of the existing Neon database; the free
  container's disk is ephemeral.
  The worker and operator bearer tokens must also be different: reusing one
  secret undermines role separation and stops boot immediately.
- The Render startup reads `DATABASE_URL` from the environment using
  `--database-env DATABASE_URL` rather than copying the PostgreSQL password
  into the process argument list. Keep the variable as a secret in Render;
  environment access still requires host-level access controls.
- Original Render `production-os1` was suspended after
  `Free Tier Usage Exceeded` on 2026-10-26; its older live deploy is not
  proof of current reachability. The new designated account is `studycall12`.
  Do not enable two live controllers against the same DB.

## 2026-11-03 startup hardening (pending review)

The Render-specific launcher now reports **all** missing required variable
names together (never secret values) so the next deployment does not need
iterative failed startups. The PostgreSQL URL and the distinct worker and
operator tokens remain mandatory. `GITHUB_TOKEN` is optional for an initially
usable control plane: without it, the pre-existing GitHub Actions worker
can poll on its nominal five-minute cron, but GitHub Actions does not
guarantee a five-minute cadence and **immediate dispatch is disabled**. A process returning healthy is not evidence of dispatch
authorization or a completed worker job. Add a dispatch-capable token to
enable immediate wake after the scheduled fallback is qualified. A manually created service
does not inherit Blueprint `envVars`: the launcher supplies the audited
default `PRODUCTION_OS_ACTIONS_REPOSITORY=dbrckk/ai-dev-server`,
`PRODUCTION_OS_ACTIONS_WORKFLOW=production-os-actions-worker.yml`, and
`PRODUCTION_OS_ACTIONS_REF=main` when unset. Explicit nonempty overrides
are preserved. These safeguards **do not provision credentials** or establish
dispatch permissions. Keep auto-deploy off until the secrets have been
coordinated, then qualify readiness and a real worker claim.

## 2026-11-04 read-only infrastructure checkpoint

The connected Neon project `production-os` (primary branch `production`,
database `production_os`, PostgreSQL 16.15) answered a direct SQL query.
At observation time it contained 81 jobs (29 completed, 51 failed, 1 queued),
57 workflows (29 succeeded, 27 failed, 1 running) and two worker records.
The last recorded `github-actions-worker` heartbeat was
2026-10-26 15:59 UTC. These are preserved database records, **not proof of
currently executing workers**. Do not blindly clear or replay their leases.

Initial unauthenticated GET probes of both `/healthz` and `/readyz`
returned HTTP 503 for **both** hosts. Crucially, **repeated probes after the
Free-instance wake-up returned HTTP 200** on legacy `production-os1`, with
`status=healthy`, `status=ready`, and `database=reachable`; unauthenticated
`/v1/workflows` returned the expected HTTP 401. The designated new
`production-os-control-plane` still returned HTTP 503. The legacy controller
is therefore demonstrably able to resume and connect to Neon, even though it
may sleep between requests. Render reports it `not_suspended` with
`autoDeploy=yes`. **Isolate the legacy service in Render before the new
controller starts; an initial HTTP 503 is not isolation proof.** No Render
deployment or database writes occurred during this diagnostic.

## Explicit single-writer activation gate (pending PR)

The Render-specific startup now rejects all Render service IDs other than the
designated `srv-dbj1hiuc6qcc73b7afvg` (while preserving local, non-Render
test runs). If Render's standard `RENDER=true` marker is present but
`RENDER_SERVICE_ID` is absent, startup also **fails closed** rather than
bypassing the identity check. On the designated service it **refuses to start** until
`PRODUCTION_OS_PRIMARY_WRITER_ENABLED=true` is explicitly configured.
This value is **not a proof of isolation**: it must be set only after the old
`production-os1` Render service has been independently confirmed suspended,
with no possibility of an automatic redeploy. Merely returning HTTP 503
(including cold start) is never sufficient. The versioned Blueprint defaults
the activation latch to `false`; the existing manually created service
requires its own environment setting.

Do not use the latch as a switch between two live writers. There is no
automatic distributed fencing with the currently deployed legacy controller.
All historical Neon rows, job leases and GitHub Actions secrets remain
untouched during preparation.

## Read-only, credential-safe cutover verifier

A standalone verifier now exists at `scripts/verify-render-cutover.py`.
Run it from a trusted terminal with worker/operator secrets **already
present as environment variables**; never pass credentials in CLI arguments,
issue comments or URL strings:

```bash
python scripts/verify-render-cutover.py
```

It uses bounded HTTPS requests (no redirects, no credential forwarding) to
verify the new `/healthz`, `/readyz` with database access, anonymous
`/v1/workflows` rejection (401), authenticated worker
`POST /v1/jobs/availability` (read-only queue inspection), and authenticated
operator `GET /v1/stats`. It checks the legacy `/readyz` repeatedly to
catch Render Free cold-starts. It never registers a worker, claims work,
dispatches an Action or writes to Neon; log output contains no secret values.

`python scripts/verify-render-cutover.py --public-only` supports
unauthenticated diagnostics, but deliberately returns exit status **2** even
when HTTP probes pass, because auth is unverified. The full verifier returns
status **0** only when its HTTP and role probes pass, and status **1** when any
check blocks. **Neither result proves durable suspension of the old Render
service or successful execution of a real worker task**: independently
confirm the old service is suspended and require a real Actions canary
before considering cutover completed.

## Complete the already-created new-account cutover

1. **Prepare**, but do not yet add to Render, matching
   `PRODUCTION_OS_WORKER_TOKEN` and a distinct
   `PRODUCTION_OS_OPERATOR_TOKEN`. GitHub Actions Secrets in
   `dbrckk/ai-dev-server` cannot be read back by the connector, so recover
   the existing worker token from a trusted vault or rotate it securely.
   Never paste values into commits, issue comments or chat. Prepare an
   optional dispatch-capable `GITHUB_TOKEN`; without it scheduled
   GitHub Actions polling is best-effort. Neon `DATABASE_URL` already exists.
   **Do not set either Render token yet.** The currently installed image
   predates the new activation latch, and an environment update might
   activate it while the legacy controller still owns the database.
2. On the **old** Render account, disable `production-os1` auto-deploy
   and suspend its service. Independently verify Render reports
   `suspended` (not merely an HTTP 503 or an idle Free instance); keep
   historical jobs and leases unchanged. Older duplicates remain disabled.
   The current Render connector cannot suspend services or toggle
   auto-deploy, so an authorized Render administrator must perform this
   specific dashboard operation.
3. Only after the legacy suspension, merge the reviewed, green PR to
   `main` (the new service has `autoDeploy=no`). On the **new** Render
   service, coordinate `PRODUCTION_OS_WORKER_TOKEN` with GitHub Actions
   and add the distinct `PRODUCTION_OS_OPERATOR_TOKEN` and optional
   `GITHUB_TOKEN`. Keep `PRODUCTION_OS_PRIMARY_WRITER_ENABLED` unset or
   `false` during configuration. Reverify legacy suspension, set the latch
   to `true`, and trigger **one** deployment of the qualified `main`
   revision. Require `/healthz` HTTP 200, `/readyz` HTTP 200 with DB
   reachable, and unauthenticated `/v1/workflows` HTTP 401. Verify the
   deployed SHA and authenticated worker/operator responses before cutover
   acceptance.
4. The four worker/operator workflow URLs were corrected and merged on
   2026-10-31 in
   [ai-dev-server PR #412](https://github.com/dbrckk/ai-dev-server/pull/412)
   to use **the new HTTPS origin directly**, rather than a fallback controlled
   by the potentially stale `PRODUCTION_OS_URL` repository variable.
   The origin pinning is complete, but a successful worker run with its
   executor skipped is not proof of controller readiness. Separately update
   the repository variable `PRODUCTION_OS_URL` to
   `https://production-os-control-plane.onrender.com` for administrative
   consistency and any consumers outside these four workflows; the
   connector cannot administer that setting.
5. Run one bounded authenticated canary and require a real worker claim,
   durable completed state, model-produced exact-SHA draft PR and
   independently passing target CI. A green *scheduled preflight* that
   skipped the executor is not proof of autonomy.
6. After successful qualification, enable new-service automatic deploys
   on reviewed `main` revisions if free-tier usage permits it; monitor
   monthly pooled Render usage (the second workspace also hosts other
   Free services). Never enable paid upgrades automatically.

**2026-10-31 connector limit:** The GitHub connector does not expose Actions
secret-value reads or secret/variable writes. Render exposes new-service
environment-variable writes but not existing secret-value reads. Updating
`DATABASE_URL` on the old `production-os1` was attempted to fail-closed
that controller permanently, but Render rejected it with
`cannot deploy suspended service`. The old controller remains billing
suspended, but this is **not** proof it will stay unavailable after the
old account's quota reset. Securely transfer the original tokens and keep
the old controller disabled via its dashboard. Browser automation was
not used because its linked metered wallet had insufficient credit.

## Future Blueprint recreation (requires separate authorization)

**Do not run this Blueprint to complete the current migration.** The
new-account service already exists, and re-running the Blueprint could
create another controller. The steps below apply only to a separately
approved future service replacement.

1. Open https://dashboard.render.com/blueprints in the approved Render
   account, choose **New Blueprint** and connect the existing GitHub repo
   `dbrckk/Production-OS` on branch **main**.
2. Keep the default Blueprint path **render.yaml**. Inspect the planned
   resources before approval: **one web service, plan Free, Frankfurt**,
   with the name `production-os-control-plane`; **no Render database**.
   Never approve an automatically selected paid tier.
3. In the Blueprint's **secret environment variable** prompts, supply the
   three mandatory values plus optional `GITHUB_TOKEN` for immediate dispatch.
   Render's `sync: false` keeps values out of Git:
   - `DATABASE_URL`: the **existing** Neon PostgreSQL connection string
     for `production_os`, SSL enabled. Obtain via Neon Console, or safely
     from an authorized secret manager. **Never copy into Git or chat.**
   - `PRODUCTION_OS_WORKER_TOKEN`: must equal the worker secret currently
     configured in **ai-dev-server -> Settings -> Secrets and variables ->
     Actions -> Secrets**.
   - `PRODUCTION_OS_OPERATOR_TOKEN`: must equal the operator/canary
     Actions secret in **ai-dev-server**. Must be distinct from the worker
     token.
   - `GITHUB_TOKEN` (optional for scheduled fallback): a separate,
     least-privilege GitHub token permitted to dispatch the
     `production-os-actions-worker.yml` workflow in `dbrckk/ai-dev-server`.
     Do not use the Neon password as a token.
4. The Blueprint sets the worker ID, repository, workflow, branch and port
   to existing audited defaults. Allow the first deployment to finish.
   Retrieve its **actual Render-assigned HTTPS URL**; do not assume a
   particular service hostname.
5. Verify **GET /healthz** returns HTTP 200 with `status: healthy` without
   querying PostgreSQL. Separately verify **GET /readyz** returns HTTP 200
   with `status: ready` and `database: reachable`, and **GET /v1/workflows**
   without Authorization returns HTTP 401. Health-only 200 on `/healthz`
   is not evidence of operational readiness.
6. Only after those checks, review **ai-dev-server -> Settings -> Secrets
   and variables -> Actions -> Variables -> PRODUCTION_OS_URL** for
   consistency with the deployed URL. The four workflows covered by
   ai-dev-server PR #412 pin the new URL and no longer use the old
   fallback expression; other clients may still use the repository
   variable. Do not start production work before the new controller is
   ready and the old one is prevented from accepting writes.
7. Confirm the old Render service cannot accept writes before allowing new
   launches. Do not clear leases, delete data, or replay jobs to force a
   successful check.
8. Trigger exactly one bounded existing canary; demand a genuine worker
   claim, model execution, durable final state, **automatically** created
   exact-SHA draft PR and independently successful CI before declaring the
   autonomous workflow verified. A PR manually constructed by an operator
   does not count. Keep the marker canary draft until these prerequisites
   are satisfied.

## Rotating secrets safely

GitHub Actions secret **values cannot be read back** from the GitHub UI.
If the existing operator/worker tokens are unavailable, generate **new**
independent random tokens and rotate both sides as one coordinated change.
Avoid switching the GitHub worker secret to a new value before Render is
ready to accept it. A missing/wrong token must result in authentication
failure, never an anonymous API.

The Render connector for `studycall12` is connected and the service was
created successfully. GitHub-to-Render authorization and GitHub Actions
secret values are **separate**: connecting GitHub to Render does not copy
worker/operator tokens or the GitHub dispatch PAT. Do not claim readiness
from a successful image build alone; verify actual service behavior first.

## Free-tier limits and operational expectations

Render Free instances can spin down after inactivity, making the next
request slower. The existing GitHub Actions worker is scheduled every 5
minutes; verify it still performs successful, authorized API calls and
observe quota use before promising sustained 24/7 autonomy. Each Render
account's free quota is provider-enforced; this migration does **not**
guarantee the old or new account will avoid suspension, nor does it increase
AI model/GitHub Actions quotas. Keep paid auto-upgrades disabled.

## Rollback and audit

- Do not redirect unrelated consumers of `PRODUCTION_OS_URL` before new
  readiness and authorization checks pass. The four worker workflows from
  PR #412 explicitly use the new host. Keep the previous value for audit,
  not as a guaranteed working rollback destination.
- If the new host fails, stop new task launches and prevent concurrent
  writers; do not invent successful canary receipts.
- CI checks blueprint resource count, Free plan, absence of managed database
  and explicit `sync: false` secret prompts; it also boots the real free
  Docker image against disposable PostgreSQL credentials.
