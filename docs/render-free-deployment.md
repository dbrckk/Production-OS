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
`PRODUCTION_OS_OPERATOR_TOKEN` and `GITHUB_TOKEN` must also be provisioned
on the new service before it can be activated. New-service auto-deploy is
temporarily **off** to avoid wasting Free quota on repeated GitHub pushes
before authentication and readiness are verified. This document records
the target destination, not a successful switchover.

The version-controlled `render.yaml` is a *future Blueprint template* and
does not automatically update or configure the new manually created Render
service. Never create a duplicate controller with the Blueprint. The old
`production-os1` on the original account is billing-suspended; it is not
the future destination and must not be allowed to run concurrently with the
new controller on the same persistent database.

If explicitly deployed, `render.yaml` creates exactly
**one Render Free web service**. It does not create a database, a paid service,
a persistent disk, a cron job or an extra worker. GitHub Actions remains the
execution tier. Prior free-host alternatives are archived as a fallback in
`docs/free-hosting-migration.md`; **do not deploy them**.

## Verified existing architecture

- Source: `dbrckk/Production-OS`, `main` (Render builds
  `Dockerfile.free-hosting`, running `scripts/render-start.py`).
- Worker: `dbrckk/ai-dev-server`, GitHub Actions
  `production-os-actions-worker.yml` (schedule every 5 minutes).
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

## Complete the already-created new-account cutover

1. In the **new** Render service's Environment settings, configure the
   existing `PRODUCTION_OS_WORKER_TOKEN`, `PRODUCTION_OS_OPERATOR_TOKEN`
   and `GITHUB_TOKEN` securely; never paste secrets into commits or chat.
   Worker/operator values must match the relevant secrets in
   `dbrckk/ai-dev-server`. If the existing values cannot be recovered,
   rotate both sides together instead of inventing placeholders. The
   existing Neon `DATABASE_URL` is already configured.
2. With auto-deploy still off, deploy once from `main` and verify the
   *new* host's `/healthz`, `/readyz` and unauthenticated protected
   `/v1/workflows` return 200 healthy, 200 ready with database reachable,
   and 401, respectively. Check that the deployed commit is the intended
   reviewed `main` revision.
3. Before switching incoming work, ensure the original
   `production-os1` service is permanently suspended or otherwise
   unable to run against the shared Neon database; do not delete data or
   reset leases. Older duplicate controllers remain disabled.
4. Change the **ai-dev-server** GitHub Actions repository variable
   `PRODUCTION_OS_URL` to
   `https://production-os-control-plane.onrender.com`. Its existing
   workflow fallback still points to the old host, so this explicit
   variable is **required** until that fallback is independently updated.
5. Run one bounded authenticated canary and require a real worker claim,
   durable completed state, model-produced exact-SHA draft PR and
   independently passing target CI. A green *scheduled preflight* that
   skipped the executor is not proof of autonomy.
6. After successful qualification, enable new-service automatic deploys
   on reviewed `main` revisions if free-tier usage permits it; monitor
   monthly pooled Render usage (the second workspace also hosts other
   Free services). Never enable paid upgrades automatically.

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
   four mandatory values. Render's `sync: false` keeps values out of Git:
   - `DATABASE_URL`: the **existing** Neon PostgreSQL connection string
     for `production_os`, SSL enabled. Obtain via Neon Console, or safely
     from an authorized secret manager. **Never copy into Git or chat.**
   - `PRODUCTION_OS_WORKER_TOKEN`: must equal the worker secret currently
     configured in **ai-dev-server -> Settings -> Secrets and variables ->
     Actions -> Secrets**.
   - `PRODUCTION_OS_OPERATOR_TOKEN`: must equal the operator/canary
     Actions secret in **ai-dev-server**. Must be distinct from the worker
     token.
   - `GITHUB_TOKEN`: a separate, least-privilege GitHub token permitted to
     dispatch the `production-os-actions-worker.yml` workflow in
     `dbrckk/ai-dev-server`. Do not use the Neon password as a token.
4. The Blueprint sets the worker ID, repository, workflow, branch and port
   to existing audited defaults. Allow the first deployment to finish.
   Retrieve its **actual Render-assigned HTTPS URL**; do not assume a
   particular service hostname.
5. Verify **GET /healthz** returns HTTP 200 with `status: healthy` without
   querying PostgreSQL. Separately verify **GET /readyz** returns HTTP 200
   with `status: ready` and `database: reachable`, and **GET /v1/workflows**
   without Authorization returns HTTP 401. Health-only 200 on `/healthz`
   is not evidence of operational readiness.
6. Only after those checks, change **ai-dev-server -> Settings -> Secrets
   and variables -> Actions -> Variables -> PRODUCTION_OS_URL** to the
   actual, reachable new HTTPS base URL. The worker and canary workflows
   otherwise **fall back to the old suspended Render hostname**, so this
   variable is essential to the cutover.
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

- Do not change `PRODUCTION_OS_URL` until new readiness + authorization
  checks pass. Keep the previous value for audit, not as a guaranteed
  working rollback destination.
- If the new host fails, stop new task launches and prevent concurrent
  writers; do not invent successful canary receipts.
- CI checks blueprint resource count, Free plan, absence of managed database
  and explicit `sync: false` secret prompts; it also boots the real free
  Docker image against disposable PostgreSQL credentials.
