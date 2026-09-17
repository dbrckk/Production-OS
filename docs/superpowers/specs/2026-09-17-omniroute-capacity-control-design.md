# OmniRoute-backed portfolio capacity control

Date: 2026-09-17
Status: design for review
Scope: `dbrckk/Production-OS` + `dbrckk/ai-dev-server`

## Objective

Turn Production-OS into the human-facing control plane for multiple autonomous GitHub projects while AI Dev Server remains the execution engine. Each selected repository receives a final goal, an execution state, a token/capacity budget, and a human review gate. The system should use free inference capacity first, especially OmniRoute's aggregated free tiers, and use Codex authenticated through the user's ChatGPT plan as a secondary included-capacity path when available. Paid API use is disabled by default.

## Existing architecture to preserve

Production-OS already owns portfolio discovery, prioritization, scheduling, resource allocation, execution feedback, and the HTML control surface. AI Dev Server already owns autonomous goals, project runtime state, fleet scheduling, agent routing, tests/build/review, and durable telemetry. The integration extends these boundaries rather than duplicating them.

## Approaches considered

### A. Production-OS control plane -> AI Dev Server -> capacity router (selected)

Production-OS stores user intent and displays state. AI Dev Server chooses and executes an agent/provider according to a capacity policy. OmniRoute is treated as an inference gateway/provider pool inside AI Dev Server.

Advantages: preserves existing boundaries; one execution engine; one place for provider failover and quotas; easiest to test independently.

### B. Production-OS calls OmniRoute/Codex directly

Rejected because it would duplicate provider routing, process supervision, verification and runtime state already implemented in AI Dev Server.

### C. Separate token-router microservice

Rejected for V1 because it adds deployment, persistence and failure modes without a capability that AI Dev Server cannot own directly. The provider interface must remain separable so it can become a service later if required.

## Capacity sources and routing order

Default route order:

1. `omniroute-free`
2. `codex-chatgpt`
3. other free providers already registered in AI Dev Server
4. paid providers only when an explicit project/user policy enables them

`omniroute-free` must not hardcode a 1.5B value. OmniRoute currently documents about 1.53B recurring free tokens/month, but the catalog changes. AI Dev Server should read the local OmniRoute free-tier summary when reachable and cache the latest successful snapshot with timestamp and source metadata.

`codex-chatgpt` means Codex authenticated with the user's ChatGPT account. It consumes the allowance included with that ChatGPT plan. It is not the same as `OPENAI_API_KEY`, and API-key billing must remain a separate provider mode.

If both OmniRoute and ChatGPT/Codex are unavailable, the router may use another configured free provider. It must not silently cross into paid inference.

## OmniRoute integration

OmniRoute runs as a local or network-reachable gateway. Its OpenAI-compatible endpoint is expected at a configurable base URL, defaulting to `http://localhost:20128` only when the process is local.

Required adapter responsibilities:

- health/probe without consuming meaningful inference;
- OpenAI-compatible request execution using model/combo `auto` by default;
- capture provider/model chosen when OmniRoute exposes it;
- normalized token usage per request/run;
- read free-tier budget/usage summary from OmniRoute when available;
- bounded retry for transient gateway/provider failures;
- surface exhausted/unavailable pools to the existing capacity scheduler;
- never store provider secrets in project workspaces or Production-OS state.

A fresh OmniRoute install can answer through keyless free providers, but larger free capacity may require provider-specific account/API configuration. Those credentials remain in OmniRoute or trusted secret storage, never in project briefs.

## Managed Project model

Production-OS adds a persistent `ManagedProject` record with at least:

- repository full name;
- repository default branch;
- project ID;
- final goal text;
- goal revision;
- user-selected priority;
- execution policy (`free_only` by default);
- preferred agent (`auto` by default);
- project token budget or `null` for global-policy-only;
- lifecycle state;
- latest AI Dev Server run ID;
- latest verified revision/SHA;
- accumulated normalized token usage;
- latest blocker/review summary;
- timestamps.

The project record contains no GitHub, provider or model credential values.

## Lifecycle

Canonical states:

- `READY`: configured and waiting for capacity;
- `RUNNING`: AI Dev Server owns an active lease/run;
- `BLOCKED`: external prerequisite or deterministic blocker prevents progress;
- `FAILED`: execution stopped after bounded recovery/retry policy;
- `REVIEW_REQUIRED`: automated goal verification passed and a human should test the result;
- `DONE`: explicitly marked finished by the user.

`REVIEW_REQUIRED` is not `DONE`. Agents cannot mark a project `DONE`. From `REVIEW_REQUIRED`, the user can either:

- add instructions, producing a new goal revision and returning the project to `READY`/`RUNNING`; or
- mark it `DONE`.

A completed project can later receive a new goal revision and become active again.

## Goal handoff

Production-OS sends a versioned execution contract to AI Dev Server containing repository, target revision, goal revision, final goal, priority, execution policy, budget envelope and required verification profile.

AI Dev Server executes against an isolated workspace/worktree and returns a versioned status contract containing run ID, project state, current phase, selected agent/provider, Git revision, verification results, blockers and usage telemetry.

Contracts must be JSON-serializable and backward-compatible for at least one previous schema version during migration.

## Usage and token accounting

Two different numbers must never be conflated:

1. **Measured project usage**: normalized input/output/cache/reasoning/total token counts emitted by a provider or agent when available.
2. **Available capacity**: provider-specific free allowance or quota estimate.

Per-run usage events include:

- project ID and run ID;
- provider (`omniroute`, `codex-chatgpt`, etc.);
- model when known;
- input tokens;
- cached input tokens when known;
- output tokens;
- reasoning tokens when known;
- total tokens;
- estimated monetary cost, forced to zero only when the source is known to be included/free;
- whether the counts are `reported`, `derived`, or `unknown`;
- timestamp.

Unknown counts remain unknown rather than being fabricated.

### OmniRoute global capacity

Production-OS displays the current OmniRoute recurring-free capacity snapshot and used/remaining values when the gateway reports them. Because free-tier grants can change, the UI shows the snapshot timestamp and never treats ~1.53B as a guaranteed contractual quota.

### ChatGPT/Codex capacity

Codex/ChatGPT usage is displayed separately from OmniRoute. The system records measured Codex activity where available and may expose Codex status/limit information that the client provides, but it must not invent a token-equivalent monthly ceiling for a ChatGPT subscription.

### Portfolio bar

The main UI contains:

- OmniRoute free-pool used/remaining bar;
- ChatGPT/Codex included-capacity status separately;
- total measured project tokens for the selected period;
- per-project usage bars against user-defined project budgets when budgets exist.

The global visual must make clear whether a value is measured usage, a provider allowance, or a user-defined budget.

## Scheduler behavior

Production-OS continues to decide which projects are eligible and their portfolio priority. AI Dev Server continues to allocate execution capacity.

Before starting a run, AI Dev Server requests a provider route from the capacity router. The route decision considers:

- project execution policy;
- provider health;
- remaining known free capacity;
- current rate/concurrency limits;
- model/agent capability requirements;
- verification reserve;
- recent success/failure/cost telemetry.

Provider exhaustion should cause rerouting or pause, not project failure, unless every allowed route is exhausted or unavailable.

## UI design

The existing Production-OS control surface is extended rather than replaced in V1.

### Portfolio header

Shows GitHub connection status, active/review/blocked/done project counts, OmniRoute free-pool capacity and measured total usage.

### Repository selection

The user can select multiple accessible GitHub repositories and create Managed Projects. Existing managed entries are not duplicated.

### Project card

Each card shows:

- repository name;
- final goal summary;
- state icon and state label;
- current phase;
- agent + capacity source;
- branch/SHA;
- test/build/lint/verification status when available;
- project token usage and optional budget bar;
- actions appropriate to state.

### Review actions

`REVIEW_REQUIRED` exposes `New instruction` and `Mark finished`. New instructions create a new immutable goal revision; they do not overwrite history.

The layout remains usable on Android/mobile widths.

## Security

- No provider/API/GitHub secret values in Managed Project JSON, briefs, telemetry or generated dashboards.
- Agent workspaces continue to receive no repository publishing credentials.
- OmniRoute credentials stay in OmniRoute/trusted secrets.
- Codex ChatGPT authentication stays in the Codex client auth store supported by that client.
- Paid provider routes require explicit enablement; absence of a free route never implies permission to spend money.
- Logs redact values associated with key/token/secret/password environment variables.
- Repository writes continue through trusted Git/GitHub paths after verification.

## Failure handling

- OmniRoute unreachable: mark route unhealthy, try allowed fallback.
- OmniRoute free pools exhausted: use another allowed free route, including Codex/ChatGPT if available.
- Codex ChatGPT allowance exhausted: mark capacity unavailable until reset/reauth; do not convert automatically to API billing.
- Provider rate limit: bounded backoff, then reroute.
- All free routes unavailable: project becomes `BLOCKED` with a capacity reason, preserving checkpoint state.
- Verification failure: remain active/retry according to existing bounded policies; never enter `REVIEW_REQUIRED`.
- Telemetry unavailable: execution may continue if policy allows, but usage is recorded as unknown and the UI indicates incomplete accounting.

## Persistence

V1 should use the persistence mechanism already native to each repository rather than adding a database solely for this feature. Production-OS owns managed-project configuration/history; AI Dev Server owns runtime/checkpoint/telemetry. Their shared contracts are files or HTTP payloads with explicit schema versions.

## Testing strategy

### Production-OS

- ManagedProject serialization and goal revision history;
- state-transition tests, especially preventing agent-driven `DONE`;
- multi-repository import without duplicates;
- capacity/usage aggregation with unknown values;
- dashboard rendering at desktop and narrow/mobile widths;
- contract compatibility tests.

### AI Dev Server

- OmniRoute adapter probe/request/timeout/rate-limit behavior using a local fake HTTP server, not paid external inference;
- free-only routing never selects paid providers;
- Codex ChatGPT fallback selection;
- exhaustion/reroute behavior;
- token telemetry normalization;
- secret redaction;
- project remains resumable after capacity blockage;
- integration with existing fleet/capacity scheduler.

### Cross-repository

A contract fixture shared by tests in both repos verifies that Production-OS handoff payloads are accepted by AI Dev Server and that returned project status/usage payloads render correctly in Production-OS.

## Rollout sequence

1. Define and test versioned project/capacity/usage contracts.
2. Add AI Dev Server OmniRoute capacity adapter and routing policy.
3. Add normalized usage telemetry and Codex/ChatGPT fallback state.
4. Add Production-OS ManagedProject persistence and lifecycle.
5. Connect handoff/status ingestion.
6. Extend the Production-OS control surface for multi-repo goals, state icons and token/capacity views.
7. Run unit/integration suites and existing readiness/CI gates in both repos.
8. Enable one real repository as a canary before allowing several concurrent projects.

## Acceptance criteria

The feature is ready for initial use when all of the following are true:

- multiple GitHub repositories can be selected and assigned independent final goals;
- each project can execute through AI Dev Server without writing directly to `main` from the agent workspace;
- OmniRoute is the first free capacity route when healthy;
- Codex authenticated by ChatGPT can be used as an included-capacity fallback without requiring an OpenAI API key;
- paid API inference cannot occur unless explicitly enabled;
- project state, phase, verification and measured token usage are visible in Production-OS;
- the OmniRoute capacity view is sourced dynamically and timestamped;
- verified goal completion produces `REVIEW_REQUIRED`, not `DONE`;
- only an explicit user action marks a project `DONE`;
- failed/exhausted providers reroute or block cleanly without losing project state;
- existing tests plus new integration tests pass in both repositories.
