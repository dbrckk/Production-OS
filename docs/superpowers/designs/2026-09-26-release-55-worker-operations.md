# Release 55 — Worker operations design

Production OS already has the server-side pieces for operator worker control: durable desired state, audited pause/resume/drain actions, heartbeat acknowledgements, claim admission, worker liveness and active-task reporting. The missing link is the persistent remote runner itself.

Release 55 therefore uses one control loop rather than adding an orchestration subsystem. Each runner consumes the desired worker state returned by heartbeat. It keeps that state locally only as a cache of server authority, echoes it as `control_state` on the next heartbeat so DashboardControl can persist acknowledgement, and only enters the claim loop while the observed state is `active`.

`paused` and `draining` both stop new claims. Their operational distinction is intent: pause is reversible admission suspension; drain is the operator signal to empty the worker. Neither kills active executors. Existing active jobs continue heartbeat/cancellation/stale-generation handling and finish normally. Process shutdown remains a separate mechanism and retains Release 53 recovery semantics.

The control plane remains defense in depth: `/v1/jobs/claim` already rejects paused/draining workers even if a runner has stale local state. Heartbeat-derived liveness remains independent from desired state, so a paused worker can be online and a draining worker can later become dead if heartbeats stop.