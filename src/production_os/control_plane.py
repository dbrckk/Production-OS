from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .api_auth import Principal, TokenAuthorizer
from .storage import job_queue_for, open_backend, worker_registry_for
from .workflow_engine import WorkflowEngine, WorkflowTaskSpec
from .managed_projects import ManagedProjectService, global_token_capacity
from .execution_optimizer import ExecutionOptimizer
from .speculation import SpeculationManager
from .portfolio_optimizer import PortfolioOptimizer
from .github_client import GitHubAPIError, GitHubClient
from .release_ledger import ReleaseLedger
from .github_webhook import (
    WebhookDeliveryStore,
    WebhookError,
    parse_github_webhook,
    pull_request_event_target,
    verify_github_signature,
)


class ControlPlane:
    def __init__(
        self,
        database: str,
        *,
        authorizer: TokenAuthorizer | None = None,
        github_webhook_secret: str | None = None,
        trusted_validation_secrets: dict[str, str] | None = None,
        provenance_secret: str | None = None,
        trusted_validation_public_keys: dict[str, str] | None = None,
        provenance_private_key: str | None = None,
        provenance_public_key: str | None = None,
        provenance_signer=None,
        validation_signature_policy: str = "compatible",
        builder_id: str = "https://production-os.local/builder",
        builder_private_key: str | None = None,
        builder_signer=None,
        trusted_builders: dict | None = None,
        trusted_builder_keys: dict | None = None,
        require_trusted_builder: bool = False,
    ):
        self.backend = open_backend(database)
        self.queue = job_queue_for(self.backend)
        self.workers = worker_registry_for(self.backend)
        self.workflows = WorkflowEngine(self.backend, self.queue)
        self.managed_projects = ManagedProjectService(self.workflows)
        self.optimizer = ExecutionOptimizer(self.backend)
        self.speculation = SpeculationManager(self.backend, self.queue)
        self.portfolio = PortfolioOptimizer(self.workflows, self.optimizer)
        self.releases = ReleaseLedger(
            self.backend,
            self.workflows,
            trusted_validation_secrets=trusted_validation_secrets,
            provenance_secret=provenance_secret,
            trusted_validation_public_keys=(
                trusted_validation_public_keys
            ),
            provenance_private_key=provenance_private_key,
            provenance_public_key=provenance_public_key,
            provenance_signer=provenance_signer,
            validation_signature_policy=validation_signature_policy,
            builder_id=builder_id,
            builder_private_key=builder_private_key,
            builder_signer=builder_signer,
            trusted_builders=trusted_builders,
            trusted_builder_keys=trusted_builder_keys,
            require_trusted_builder=require_trusted_builder,
        )
        self.authorizer = authorizer or TokenAuthorizer([])
        self.github_webhook_secret = github_webhook_secret
        self.webhook_deliveries = WebhookDeliveryStore(self.backend)


def _json_bytes(payload: dict | list) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Production-OS</title>
<style>
:root{font-family:system-ui,-apple-system,sans-serif;color-scheme:light dark}
body{max-width:1180px;margin:0 auto;padding:18px;line-height:1.4}
header,.toolbar,.row,.project-head,.actions{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
header{justify-content:space-between;margin-bottom:16px}
h1,h2,h3,p{margin-top:0}
input,textarea,select,button{font:inherit;padding:9px;border-radius:8px;border:1px solid #888}
input,textarea,select{box-sizing:border-box}
button{cursor:pointer}
button:disabled{opacity:.55;cursor:not-allowed}
.panel,.card{border:1px solid #7776;border-radius:12px;padding:14px;margin:12px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}
.repo-list,.project-grid,.selected-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px}
.repo,.project,.setup{border:1px solid #7776;border-radius:10px;padding:12px}
.project-head{justify-content:space-between}
.badge{font-size:.82rem;border:1px solid #7778;border-radius:999px;padding:3px 8px}
.muted{opacity:.72;font-size:.9rem}
label{display:block;margin:7px 0 4px}
textarea{width:100%;min-height:76px;resize:vertical}
.setup input,.setup select{width:100%}
progress{width:100%;height:16px}
.notice{min-height:1.4em}
.token-input{min-width:220px;flex:1}
.owner-input{min-width:150px}
.metric strong{font-size:1.4rem;display:block}
.hidden{display:none}
@media(max-width:600px){
 body{padding:12px}
 .toolbar>*{width:100%}
 .toolbar button{width:auto}
 .project-grid,.repo-list,.selected-grid{grid-template-columns:1fr}
}
</style>
</head>
<body>
<header>
 <div><h1>Production-OS</h1><div class="muted">Managed autonomous projects</div></div>
 <span class="badge">GitHub + AI Dev Server</span>
</header>

<section class="panel">
 <div class="toolbar">
  <input id="token" class="token-input" type="password" autocomplete="off" placeholder="Production-OS Bearer token">
  <button type="button" onclick="refreshProjects()">Refresh</button>
 </div>
 <p id="notice" class="notice muted"></p>
</section>

<section class="panel">
 <h2>Portfolio</h2>
 <div id="stats" class="grid"></div>
 <div class="card">
  <div class="project-head"><strong>Global token budget</strong><span id="global-token-text">0 / 0</span></div>
  <div id="global-token-source" class="muted">Managed project budgets</div>
  <progress id="global-token-progress" value="0" max="1"></progress>
 </div>
</section>

<section class="panel">
 <h2>Add GitHub repositories</h2>
 <div class="toolbar">
  <input id="owner" class="owner-input" placeholder="GitHub owner">
  <button type="button" onclick="loadRepositories()">Load repositories</button>
 </div>
 <p class="muted">Select one or more repositories. Each selected project gets its own final goal, token budget and agent preference.</p>
 <div id="repo-list" class="repo-list"></div>
 <div id="selected-projects" class="selected-grid"></div>
 <div class="actions">
  <button id="create-selected" type="button" onclick="createSelectedProjects()" disabled>Start selected projects</button>
 </div>
</section>

<section class="panel">
 <h2>Managed projects</h2>
 <div id="managed-projects" class="project-grid"></div>
</section>

<section class="panel">
 <details>
  <summary>Runtime details</summary>
  <h3>Workers</h3><pre id="workers"></pre>
  <h3>Recent events</h3><pre id="events"></pre>
 </details>
</section>

<script>
const selectedRepos=new Map();
const stateIcons={
 RUNNING:'▶', REVIEW_REQUIRED:'✓', DONE:'●', BLOCKED:'!', FAILED:'×', PAUSED:'Ⅱ'
};

function authHeaders(extra){
 const token=document.getElementById('token').value.trim();
 return Object.assign(
  {'Authorization':'Bearer '+token,'Content-Type':'application/json'},
  extra||{}
 );
}

async function api(path,options){
 const opts=Object.assign({},options||{});
 opts.headers=authHeaders(opts.headers);
 const response=await fetch(path,opts);
 const text=await response.text();
 let payload={};
 if(text){try{payload=JSON.parse(text)}catch(_){payload={error:text}}}
 if(!response.ok) throw new Error(payload.error||('HTTP '+response.status));
 return payload;
}

function setNotice(message,isError){
 const node=document.getElementById('notice');
 node.textContent=message||'';
 node.style.fontWeight=isError?'600':'400';
}

function formatTokens(value){
 const number=Number(value||0);
 return new Intl.NumberFormat().format(number);
}

function element(tag,text,className){
 const node=document.createElement(tag);
 if(text!==undefined && text!==null) node.textContent=String(text);
 if(className) node.className=className;
 return node;
}

function renderStats(projects,capacity){
 const counts={RUNNING:0,REVIEW_REQUIRED:0,BLOCKED:0,FAILED:0,DONE:0,PAUSED:0};
 projects.forEach(function(project){
  counts[project.state]=(counts[project.state]||0)+1;
 });
 const globalCapacity=capacity||{};
 const used=Number(globalCapacity.used||0);
 const budget=Number(globalCapacity.monthly_budget||0);
 const stats=document.getElementById('stats');
 stats.replaceChildren();
 [
  ['Running',counts.RUNNING],
  ['Review',counts.REVIEW_REQUIRED],
  ['Blocked',counts.BLOCKED+counts.FAILED],
  ['Done',counts.DONE]
 ].forEach(function(pair){
  const card=element('div',null,'card metric');
  card.append(element('span',pair[0]),element('strong',pair[1]));
  stats.append(card);
 });
 const bar=document.getElementById('global-token-progress');
 bar.max=Math.max(1,budget);
 bar.value=Math.min(used,Math.max(1,budget));
 document.getElementById('global-token-text').textContent=
  formatTokens(used)+' / '+formatTokens(budget)+' tokens';
 document.getElementById('global-token-source').textContent=
  String(globalCapacity.label||'Managed project budgets');
}

function projectCard(project){
 const card=element('article',null,'project');
 const head=element('div',null,'project-head');
 const title=element('strong',project.repository);
 const badge=element(
  'span',
  (stateIcons[project.state]||'?')+' '+project.state,
  'badge'
 );
 head.append(title,badge);
 card.append(head);
 card.append(element('p',project.final_goal));
 card.append(element('div','Agent: '+project.agent_preference,'muted'));

 const used=Number((project.usage||{}).total_tokens||0);
 const budget=Number(project.token_budget||0);
 const usageText=element(
  'div',
  formatTokens(used)+' / '+formatTokens(budget)+' tokens',
  'muted'
 );
 const progress=document.createElement('progress');
 progress.max=Math.max(1,budget);
 progress.value=Math.min(used,Math.max(1,budget));
 card.append(usageText,progress);

 if(project.state==='REVIEW_REQUIRED'){
  const instruction=document.createElement('textarea');
  instruction.placeholder='Add a new instruction before final approval';
  instruction.setAttribute('aria-label','New instruction');
  card.append(instruction);

  const actions=element('div',null,'actions');
  const retest=element('button','Retest');
  retest.type='button';
  retest.addEventListener('click',async function(){
   retest.disabled=true;
   try{
    await api(
     '/v1/managed-projects/'+encodeURIComponent(project.workflow_id)+'/verify',
     {method:'POST',body:'{}'}
    );
    setNotice(project.repository+' verification queued.',false);
    await refreshProjects();
   }catch(error){
    setNotice(String(error),true);
    retest.disabled=false;
   }
  });

  const send=element('button','Send instruction');
  send.type='button';
  send.addEventListener('click',async function(){
   const value=instruction.value.trim();
   if(!value){setNotice('Enter an instruction first.',true);return}
   send.disabled=true;
   try{
    await api(
     '/v1/managed-projects/'+encodeURIComponent(project.workflow_id)+'/instructions',
     {method:'POST',body:JSON.stringify({instruction:value})}
    );
    setNotice(project.repository+' instruction queued.',false);
    await refreshProjects();
   }catch(error){
    setNotice(String(error),true);
    send.disabled=false;
   }
  });

  const complete=element('button','Mark done');
  complete.type='button';
  complete.addEventListener('click',async function(){
   complete.disabled=true;
   try{
    await api(
     '/v1/managed-projects/'+encodeURIComponent(project.workflow_id)+'/complete',
     {method:'POST',body:'{}'}
    );
    setNotice(project.repository+' marked done.',false);
    await refreshProjects();
   }catch(error){
    setNotice(String(error),true);
    complete.disabled=false;
   }
  });
  actions.append(retest,send,complete);
  card.append(actions);
 }
 return card;
}

async function refreshProjects(){
 try{
  const data=await api('/v1/managed-projects');
  const projects=data.projects||[];
  const container=document.getElementById('managed-projects');
  container.replaceChildren();
  if(!projects.length){
   container.append(element('p','No managed projects yet.','muted'));
  }else{
   projects.forEach(function(project){container.append(projectCard(project))});
  }
  renderStats(projects,data.capacity);
  const runtime=await Promise.all([
   api('/v1/workers'),
   api('/v1/events?limit=20')
  ]);
  document.getElementById('workers').textContent=JSON.stringify(runtime[0].workers||[],null,2);
  document.getElementById('events').textContent=JSON.stringify(runtime[1].events||[],null,2);
  setNotice('Dashboard refreshed.',false);
 }catch(error){
  setNotice(String(error),true);
 }
}

function renderSelected(){
 const root=document.getElementById('selected-projects');
 root.replaceChildren();
 selectedRepos.forEach(function(repo){
  const card=element('div',null,'setup');
  card.dataset.repository=repo.full_name;
  card.append(element('strong',repo.full_name));

  const goalLabel=element('label','Final goal');
  const goal=document.createElement('textarea');
  goal.dataset.role='goal';
  goal.placeholder='Describe the concrete final result for this repository';

  const budgetLabel=element('label','Token budget');
  const budget=document.createElement('input');
  budget.type='number';
  budget.min='1';
  budget.step='1';
  budget.value='250000';
  budget.dataset.role='budget';

  const agentLabel=element('label','Agent');
  const agent=document.createElement('select');
  agent.dataset.role='agent';
  [['auto','Automatic'],['codex','Codex']].forEach(function(pair){
   const option=document.createElement('option');
   option.value=pair[0]; option.textContent=pair[1]; agent.append(option);
  });

  card.append(goalLabel,goal,budgetLabel,budget,agentLabel,agent);
  root.append(card);
 });
 document.getElementById('create-selected').disabled=selectedRepos.size===0;
}

async function loadRepositories(){
 const owner=document.getElementById('owner').value.trim();
 if(!owner){setNotice('Enter a GitHub owner.',true);return}
 try{
  const data=await api('/v1/github/repositories?owner='+encodeURIComponent(owner));
  const root=document.getElementById('repo-list');
  root.replaceChildren();
  selectedRepos.clear();
  (data.repositories||[]).forEach(function(repo){
   const label=element('label',null,'repo');
   const checkbox=document.createElement('input');
   checkbox.type='checkbox';
   checkbox.addEventListener('change',function(){
    if(checkbox.checked) selectedRepos.set(repo.full_name,repo);
    else selectedRepos.delete(repo.full_name);
    renderSelected();
   });
   label.append(checkbox,document.createTextNode(' '+repo.full_name));
   if(repo.private) label.append(element('div','Private','muted'));
   root.append(label);
  });
  renderSelected();
  setNotice('Loaded '+String((data.repositories||[]).length)+' repositories.',false);
 }catch(error){
  setNotice(String(error),true);
 }
}

async function createSelectedProjects(){
 const cards=Array.from(document.querySelectorAll('#selected-projects .setup'));
 if(!cards.length) return;
 const button=document.getElementById('create-selected');
 button.disabled=true;
 try{
  for(const card of cards){
   const finalGoal=card.querySelector('[data-role="goal"]').value.trim();
   const tokenBudget=Number(card.querySelector('[data-role="budget"]').value);
   const agent=card.querySelector('[data-role="agent"]').value;
   if(!finalGoal) throw new Error('A final goal is required for '+card.dataset.repository);
   if(!Number.isInteger(tokenBudget)||tokenBudget<=0){
    throw new Error('A positive token budget is required for '+card.dataset.repository);
   }
   await api('/v1/managed-projects',{
    method:'POST',
    body:JSON.stringify({
     repository:card.dataset.repository,
     final_goal:finalGoal,
     token_budget:tokenBudget,
     agent_preference:agent
    })
   });
  }
  selectedRepos.clear();
  document.querySelectorAll('#repo-list input[type="checkbox"]').forEach(function(node){
   node.checked=false;
  });
  renderSelected();
  setNotice('Selected projects created.',false);
  await refreshProjects();
 }catch(error){
  setNotice(String(error),true);
 }finally{
  button.disabled=selectedRepos.size===0;
 }
}
</script>
</body>
</html>"""


class RequestBodyTooLarge(ValueError):
    pass


def make_handler(control: ControlPlane):
    class Handler(BaseHTTPRequestHandler):
        server_version = "ProductionOS"

        def version_string(self) -> str:
            return self.server_version

        def log_message(self, format: str, *args) -> None:
            return

        def _send_html(self, status: int, html: str) -> None:
            body = html.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                return

        def _send(
            self,
            status: int,
            payload: dict | list,
            *,
            headers: dict[str, str] | None = None,
        ) -> None:
            body = _json_bytes(payload)
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            if headers:
                for name, value in headers.items():
                    self.send_header(name, value)
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                return

        def _method_not_allowed(self) -> None:
            self._send(
                HTTPStatus.METHOD_NOT_ALLOWED,
                {"error": "method not allowed"},
                headers={"Allow": "GET, POST"},
            )

        def do_PUT(self) -> None:
            self._method_not_allowed()

        def do_PATCH(self) -> None:
            self._method_not_allowed()

        def do_DELETE(self) -> None:
            self._method_not_allowed()

        def _read_body(self) -> bytes:
            raw_length = self.headers.get("Content-Length", "0")
            try:
                length = int(raw_length)
            except ValueError as exc:
                raise ValueError("invalid Content-Length") from exc
            if length < 0:
                raise ValueError("invalid Content-Length")
            max_body = 1024 * 1024
            if length > max_body:
                self.rfile.read(min(length, max_body + 1))
                raise RequestBodyTooLarge("request body too large")
            if not length:
                return b""
            body = self.rfile.read(length)
            if len(body) != length:
                raise ValueError("truncated request body")
            return body

        def _read_json(self) -> dict:
            raw = self._read_body()
            if not raw:
                return {}
            try:
                payload = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError("invalid JSON body") from exc
            if not isinstance(payload, dict):
                raise ValueError("JSON object body required")
            return payload

        def _principal(self) -> Principal | None:
            header = self.headers.get("Authorization", "")
            prefix = "Bearer "
            token = header[len(prefix):] if header.startswith(prefix) else None
            return control.authorizer.authenticate(token)

        def _require(self, role: str) -> Principal | None:
            principal = self._principal()
            if principal is None:
                self._send(
                    HTTPStatus.UNAUTHORIZED,
                    {"error":"unauthorized"},
                )
                return None
            if not principal.allows(role):
                self._send(
                    HTTPStatus.FORBIDDEN,
                    {
                        "error":"forbidden",
                        "required_role":role,
                        "role":principal.role,
                    },
                )
                return None
            return principal

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/dashboard":
                self._send_html(HTTPStatus.OK, DASHBOARD_HTML)
                return

            if parsed.path in {"/", "/health", "/healthz"}:
                self._send(
                    HTTPStatus.OK,
                    {
                        "status":"healthy",
                        "schema_version":"production-os/control-plane/v1",
                    },
                )
                return

            principal = self._require("viewer")
            if principal is None:
                return

            if parsed.path == "/v1/github/repositories":
                query = parse_qs(parsed.query)
                owner = str(query.get("owner", [""])[0]).strip()
                if not owner:
                    self._send(
                        HTTPStatus.BAD_REQUEST,
                        {"error": "owner is required"},
                    )
                    return
                try:
                    repositories = GitHubClient().list_accessible_repositories(owner)
                except GitHubAPIError as exc:
                    self._send(
                        HTTPStatus.BAD_GATEWAY,
                        {"error": str(exc)},
                    )
                    return
                safe = []
                for repo in repositories:
                    if not isinstance(repo, dict):
                        continue
                    safe.append({
                        "name": str(repo.get("name") or ""),
                        "full_name": str(repo.get("full_name") or ""),
                        "private": bool(repo.get("private", False)),
                        "archived": bool(repo.get("archived", False)),
                        "fork": bool(repo.get("fork", False)),
                        "default_branch": str(
                            repo.get("default_branch") or "main"
                        ),
                        "pushed_at": repo.get("pushed_at"),
                    })
                self._send(
                    HTTPStatus.OK,
                    {"owner": owner, "repositories": safe},
                )
                return

            if parsed.path == "/v1/managed-projects":
                projects = control.managed_projects.list()
                control.workers.load()
                workers = [
                    worker.to_dict()
                    for worker in control.workers.workers.values()
                ]
                self._send(
                    HTTPStatus.OK,
                    {
                        "projects": projects,
                        "capacity": global_token_capacity(
                            projects,
                            workers,
                        ),
                    },
                )
                return

            if parsed.path == "/v1/stats":
                with control.backend.connect() as db:
                    rows = db.execute(
                        "SELECT status, COUNT(*) AS count FROM jobs GROUP BY status"
                    ).fetchall()
                    workers = db.execute(
                        "SELECT COUNT(*) AS count FROM workers WHERE status='online'"
                    ).fetchone()["count"]
                    workflow_rows = db.execute(
                        "SELECT status, COUNT(*) AS count FROM workflows GROUP BY status"
                    ).fetchall()
                self._send(
                    HTTPStatus.OK,
                    {
                        "jobs":{row["status"]:row["count"] for row in rows},
                        "workflows":{
                            row["status"]:row["count"]
                            for row in workflow_rows
                        },
                        "online_workers":workers,
                    },
                )
                return

            if parsed.path == "/v1/stragglers":
                control.workers.load()
                self._send(
                    HTTPStatus.OK,
                    {
                        "stragglers":control.optimizer.stragglers(
                            workers=list(
                                control.workers.workers.values()
                            )
                        )
                    },
                )
                return

            if parsed.path == "/v1/workflows":
                with control.backend.connect() as db:
                    rows = db.execute(
                        """
                        SELECT id, name, repository, status, created_at, updated_at
                        FROM workflows
                        ORDER BY created_at DESC
                        LIMIT 100
                        """
                    ).fetchall()
                self._send(
                    HTTPStatus.OK,
                    {
                        "workflows":[
                            {
                                "id":row["id"],
                                "name":row["name"],
                                "repository":row["repository"],
                                "status":row["status"],
                                "created_at":row["created_at"],
                                "updated_at":row["updated_at"],
                            }
                            for row in rows
                        ]
                    },
                )
                return

            if parsed.path == "/v1/events":
                query = parse_qs(parsed.query)
                try:
                    after = int(query.get("after", ["0"])[0])
                    limit = int(query.get("limit", ["100"])[0])
                except ValueError:
                    self._send(
                        HTTPStatus.BAD_REQUEST,
                        {"error":"invalid pagination"},
                    )
                    return
                self._send(
                    HTTPStatus.OK,
                    {
                        "events":control.backend.events_after(after, limit),
                    },
                )
                return

            if parsed.path.startswith("/v1/jobs/"):
                key = parsed.path.split("/", 3)[-1]
                try:
                    job = control.queue.get(key)
                except KeyError:
                    self._send(
                        HTTPStatus.NOT_FOUND,
                        {"error":"job not found"},
                    )
                    return
                self._send(HTTPStatus.OK, {"job":job})
                return

            if parsed.path.startswith("/v1/workflows/"):
                parts = [part for part in parsed.path.split("/") if part]
                if len(parts) >= 3:
                    workflow_id = parts[2]
                    try:
                        if len(parts) == 4 and parts[3] == "critical-path":
                            payload = control.workflows.critical_path(workflow_id)
                            self._send(HTTPStatus.OK, payload)
                            return
                        if len(parts) == 4 and parts[3] == "eta":
                            workflow = control.workflows.get(workflow_id)
                            payload = control.optimizer.workflow_eta(workflow)
                            self._send(HTTPStatus.OK, payload)
                            return
                        if len(parts) == 4 and parts[3] == "releases":
                            self._send(
                                HTTPStatus.OK,
                                {
                                    "releases":
                                        control.releases.list_for_workflow(
                                            workflow_id
                                        )
                                },
                            )
                            return
                        if len(parts) == 3:
                            payload = control.workflows.get(workflow_id)
                            self._send(
                                HTTPStatus.OK,
                                {"workflow":payload},
                            )
                            return
                    except KeyError:
                        self._send(
                            HTTPStatus.NOT_FOUND,
                            {"error":"workflow not found"},
                        )
                        return

            if parsed.path == "/v1/incident-history/verify":
                self._send(
                    HTTPStatus.OK,
                    {
                        "schema_version":
                            "production-os/trust-incident-history-verification/v1",
                        **control.releases.verify_incident_history(),
                    },
                )
                return

            if parsed.path == "/v1/incident-history":
                query = parse_qs(parsed.query)
                incident_id = (
                    query.get("incident_id") or [None]
                )[0]
                self._send(
                    HTTPStatus.OK,
                    {
                        "schema_version":
                            "production-os/trust-incident-history/v1",
                        "incident_id": incident_id,
                        "entries": control.releases.incident_history(
                            incident_id=incident_id
                        ),
                    },
                )
                return

            if parsed.path == "/v1/incident-report":
                query = parse_qs(parsed.query)
                report = control.releases.incident_report(
                    validator_id=(query.get("validator_id") or [None])[0],
                    builder_id=(query.get("builder_id") or [None])[0],
                    key_id=(query.get("key_id") or [None])[0],
                )
                self._send(HTTPStatus.OK, report)
                return

            if parsed.path == "/v1/trust-status":
                query = parse_qs(parsed.query)
                result = control.releases.trust_status(
                    validator_id=(query.get("validator_id") or [None])[0],
                    builder_id=(query.get("builder_id") or [None])[0],
                    key_id=(query.get("key_id") or [None])[0],
                )
                self._send(
                    HTTPStatus.OK,
                    {
                        "schema_version":
                            "production-os/trust-status/v1",
                        **result,
                    },
                )
                return

            if parsed.path == "/v1/transparency":
                self._send(
                    HTTPStatus.OK,
                    {
                        "verification":
                            control.releases.verify_transparency(),
                        "entries":
                            control.releases.transparency_log(),
                    },
                )
                return

            if parsed.path.startswith("/v1/releases/"):
                parts = [
                    part
                    for part in parsed.path.split("/")
                    if part
                ]
                if (
                    len(parts) == 4
                    and parts[1] == "releases"
                    and parts[3] == "verify"
                ):
                    try:
                        verification = control.releases.verify(
                            parts[2]
                        )
                    except KeyError:
                        self._send(
                            HTTPStatus.NOT_FOUND,
                            {"error":"release not found"},
                        )
                        return
                    self._send(
                        HTTPStatus.OK,
                        {"verification":verification},
                    )
                    return
                if len(parts) == 3 and parts[1] == "releases":
                    try:
                        release = control.releases.get(parts[2])
                    except KeyError:
                        self._send(
                            HTTPStatus.NOT_FOUND,
                            {"error":"release not found"},
                        )
                        return
                    self._send(
                        HTTPStatus.OK,
                        {"release":release},
                    )
                    return

            if parsed.path == "/v1/workers":
                control.workers.load()
                self._send(
                    HTTPStatus.OK,
                    {
                        "workers":[
                            worker.to_dict()
                            for worker in control.workers.workers.values()
                        ]
                    },
                )
                return

            self._send(HTTPStatus.NOT_FOUND, {"error":"not found"})

        def do_POST(self) -> None:
            parsed = urlparse(self.path)

            if parsed.path == "/v1/github/webhook":
                if not control.github_webhook_secret:
                    self._send(
                        HTTPStatus.SERVICE_UNAVAILABLE,
                        {"error":"github webhook secret not configured"},
                    )
                    return
                try:
                    raw = self._read_body()
                except RequestBodyTooLarge as exc:
                    self._send(
                        HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                        {"error":str(exc)},
                    )
                    return
                except ValueError as exc:
                    self._send(
                        HTTPStatus.BAD_REQUEST,
                        {"error":str(exc)},
                    )
                    return

                if not verify_github_signature(
                    control.github_webhook_secret,
                    raw,
                    self.headers.get("X-Hub-Signature-256"),
                ):
                    self._send(
                        HTTPStatus.UNAUTHORIZED,
                        {"error":"invalid github webhook signature"},
                    )
                    return

                delivery_id = self.headers.get(
                    "X-GitHub-Delivery",
                    "",
                )
                event_name = self.headers.get(
                    "X-GitHub-Event",
                    "",
                )
                try:
                    payload = parse_github_webhook(raw)
                    target = pull_request_event_target(
                        event_name,
                        payload,
                    )
                except WebhookError as exc:
                    self._send(
                        HTTPStatus.BAD_REQUEST,
                        {"error":str(exc)},
                    )
                    return

                repository = target[0] if target else None
                try:
                    claimed = control.webhook_deliveries.claim(
                        delivery_id,
                        event_name,
                        repository,
                    )
                except WebhookError as exc:
                    self._send(
                        HTTPStatus.BAD_REQUEST,
                        {"error":str(exc)},
                    )
                    return

                if not claimed:
                    self._send(
                        HTTPStatus.OK,
                        {
                            "status":"duplicate",
                            "delivery_id":delivery_id,
                        },
                    )
                    return

                try:
                    if target is None:
                        self._send(
                            HTTPStatus.ACCEPTED,
                            {
                                "status":"ignored",
                                "delivery_id":delivery_id,
                                "event":event_name,
                            },
                        )
                        return

                    repository, pr_number, action, head_sha = target
                    generation, superseded = (
                        control.workflows.ensure_pr_generation(
                            repository,
                            pr_number,
                            head_sha,
                        )
                    )
                    if generation is None:
                        generation = (
                            control.workflows.create_from_pr_template(
                                repository,
                                pr_number,
                                head_sha,
                            )
                        )
                    workflows = [generation] if generation else []
                    refreshable = [
                        workflow
                        for workflow in workflows
                        if control.workflows.generation_refreshable(
                            workflow
                        )
                    ]
                    changed_paths = (
                        GitHubClient().list_pull_request_files(
                            repository,
                            pr_number,
                        )
                        if refreshable
                        else []
                    )
                    refreshed = []
                    dispatched = []
                    for workflow in workflows:
                        if workflow not in refreshable:
                            refreshed.append({
                                "workflow_id":workflow["id"],
                                "generation":workflow.get(
                                    "metadata", {}
                                ).get("github_pr_generation"),
                                "head_sha":head_sha,
                                "decisions":[],
                                "generation_noop":True,
                                "workflow":workflow,
                            })
                            continue

                        decisions = control.workflows.apply_change_impact(
                            workflow["id"],
                            changed_paths,
                        )
                        jobs = control.workflows.dispatch_ready(
                            workflow["id"],
                        )
                        refreshed.append({
                            "workflow_id":workflow["id"],
                            "generation":workflow.get(
                                "metadata", {}
                            ).get("github_pr_generation"),
                            "head_sha":head_sha,
                            "decisions":decisions,
                            "generation_noop":False,
                            "workflow":control.workflows.get(
                                workflow["id"]
                            ),
                        })
                        dispatched.extend(jobs)

                    self._send(
                        HTTPStatus.OK,
                        {
                            "status":"processed",
                            "delivery_id":delivery_id,
                            "event":event_name,
                            "action":action,
                            "repository":repository,
                            "pr_number":pr_number,
                            "head_sha":head_sha,
                            "changed_paths":changed_paths,
                            "refreshed":len(refreshed),
                            "workflows":refreshed,
                            "superseded_workflows":[
                                item["id"]
                                for item in superseded
                            ],
                            "dispatched_jobs":dispatched,
                        },
                    )
                    return
                except Exception:
                    control.webhook_deliveries.release(delivery_id)
                    raise

            try:
                body = self._read_json()
            except RequestBodyTooLarge as exc:
                self._send(
                    HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                    {"error":str(exc)},
                )
                return
            except ValueError as exc:
                self._send(
                    HTTPStatus.BAD_REQUEST,
                    {"error":str(exc)},
                )
                return

            try:
                if parsed.path == "/v1/managed-projects":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    project = control.managed_projects.create(
                        repository=str(body["repository"]),
                        final_goal=str(body["final_goal"]),
                        token_budget=body["token_budget"],
                        agent_preference=str(
                            body.get("agent_preference") or "auto"
                        ),
                    )
                    self._send(
                        HTTPStatus.CREATED,
                        {"project": project},
                    )
                    return

                if (
                    parsed.path.startswith("/v1/managed-projects/")
                    and parsed.path.endswith("/instructions")
                ):
                    principal = self._require("operator")
                    if principal is None:
                        return
                    parts = [
                        part for part in parsed.path.split("/") if part
                    ]
                    if len(parts) != 4:
                        self._send(
                            HTTPStatus.NOT_FOUND,
                            {"error": "not found"},
                        )
                        return
                    project = control.managed_projects.add_instruction(
                        parts[2],
                        str(body.get("instruction") or ""),
                    )
                    self._send(
                        HTTPStatus.OK,
                        {"project": project},
                    )
                    return

                if (
                    parsed.path.startswith("/v1/managed-projects/")
                    and parsed.path.endswith("/verify")
                ):
                    principal = self._require("operator")
                    if principal is None:
                        return
                    parts = [
                        part for part in parsed.path.split("/") if part
                    ]
                    if len(parts) != 4:
                        self._send(
                            HTTPStatus.NOT_FOUND,
                            {"error": "not found"},
                        )
                        return
                    project = control.managed_projects.request_verification(
                        parts[2]
                    )
                    self._send(
                        HTTPStatus.OK,
                        {"project": project},
                    )
                    return

                if (
                    parsed.path.startswith("/v1/managed-projects/")
                    and parsed.path.endswith("/complete")
                ):
                    principal = self._require("operator")
                    if principal is None:
                        return
                    parts = [
                        part for part in parsed.path.split("/") if part
                    ]
                    if len(parts) != 4:
                        self._send(
                            HTTPStatus.NOT_FOUND,
                            {"error": "not found"},
                        )
                        return
                    project = control.managed_projects.mark_done(
                        parts[2],
                        approved_by=principal.name,
                    )
                    self._send(
                        HTTPStatus.OK,
                        {"project": project},
                    )
                    return

                if parsed.path == "/v1/stragglers/speculate":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    control.workers.load()
                    stragglers = control.optimizer.stragglers(
                        threshold_factor=float(
                            body.get("threshold_factor", 1.75)
                        ),
                        min_runtime_seconds=float(
                            body.get("min_runtime_seconds", 60.0)
                        ),
                        min_samples=int(
                            body.get("min_samples", 2)
                        ),
                        workers=list(
                            control.workers.workers.values()
                        ),
                    )
                    spawned = []
                    skipped = []
                    for item in stragglers:
                        alternate = item.get("alternate_worker")
                        if not alternate:
                            skipped.append({
                                "job_key":item["job_key"],
                                "reason":"no alternate worker",
                            })
                            continue
                        try:
                            job = control.speculation.spawn(
                                item["job_key"],
                                target_worker=str(
                                    alternate["worker_id"]
                                ),
                            )
                        except RuntimeError as exc:
                            skipped.append({
                                "job_key":item["job_key"],
                                "reason":str(exc),
                            })
                            continue
                        spawned.append(job)

                    self._send(
                        HTTPStatus.OK,
                        {
                            "spawned":spawned,
                            "skipped":skipped,
                        },
                    )
                    return

                if parsed.path == "/v1/github/pr-refresh":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    repository = str(body["repository"])
                    pr_number = int(body["pr_number"])
                    workflows = control.workflows.find_by_github_pr(
                        repository,
                        pr_number,
                    )
                    if not workflows:
                        self._send(
                            HTTPStatus.OK,
                            {
                                "repository":repository,
                                "pr_number":pr_number,
                                "changed_paths":[],
                                "workflows":[],
                                "refreshed":0,
                            },
                        )
                        return

                    changed_paths = GitHubClient().list_pull_request_files(
                        repository,
                        pr_number,
                    )
                    refreshed = []
                    for workflow in workflows:
                        decisions = control.workflows.apply_change_impact(
                            workflow["id"],
                            changed_paths,
                        )
                        refreshed.append({
                            "workflow_id":workflow["id"],
                            "decisions":decisions,
                            "workflow":control.workflows.get(
                                workflow["id"]
                            ),
                        })
                    self._send(
                        HTTPStatus.OK,
                        {
                            "repository":repository,
                            "pr_number":pr_number,
                            "changed_paths":changed_paths,
                            "workflows":refreshed,
                            "refreshed":len(refreshed),
                        },
                    )
                    return

                if parsed.path == "/v1/workflows":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    tasks = [
                        WorkflowTaskSpec.from_dict(item)
                        for item in body.get("tasks", [])
                    ]
                    workflow = control.workflows.create(
                        name=str(body["name"]),
                        repository=str(body["repository"]),
                        tasks=tasks,
                        metadata=dict(body.get("metadata") or {}),
                        workflow_id=(
                            str(body["workflow_id"])
                            if body.get("workflow_id")
                            else None
                        ),
                    )
                    self._send(
                        HTTPStatus.CREATED,
                        {"workflow":workflow},
                    )
                    return

                if parsed.path.startswith("/v1/workflows/"):
                    parts = [part for part in parsed.path.split("/") if part]
                    if len(parts) >= 4:
                        principal = self._require("operator")
                        if principal is None:
                            return
                        workflow_id = parts[2]
                        action = parts[3]
                        if action == "dispatch":
                            jobs = control.workflows.dispatch_ready(
                                workflow_id,
                                limit=int(body.get("limit", 10)),
                            )
                            self._send(HTTPStatus.OK, {"jobs":jobs})
                            return
                        if action == "impact":
                            decisions = control.workflows.apply_change_impact(
                                workflow_id,
                                [
                                    str(path)
                                    for path in body.get(
                                        "changed_paths",
                                        [],
                                    )
                                ],
                            )
                            self._send(
                                HTTPStatus.OK,
                                {
                                    "decisions":decisions,
                                    "workflow":control.workflows.get(
                                        workflow_id
                                    ),
                                },
                            )
                            return
                        if action == "impact-pr":
                            repository = str(body["repository"])
                            pr_number = int(body["pr_number"])
                            changed_paths = GitHubClient().list_pull_request_files(
                                repository,
                                pr_number,
                            )
                            decisions = control.workflows.apply_change_impact(
                                workflow_id,
                                changed_paths,
                            )
                            self._send(
                                HTTPStatus.OK,
                                {
                                    "repository":repository,
                                    "pr_number":pr_number,
                                    "changed_paths":changed_paths,
                                    "decisions":decisions,
                                    "workflow":control.workflows.get(
                                        workflow_id
                                    ),
                                },
                            )
                            return
                        if action == "cancel":
                            workflow = control.workflows.cancel(workflow_id)
                            self._send(
                                HTTPStatus.OK,
                                {"workflow":workflow},
                            )
                            return
                        if action == "promote":
                            release = control.releases.promote(
                                workflow_id=workflow_id,
                                artifact_id=str(body["artifact_id"]),
                                validation=dict(
                                    body.get("validation") or {}
                                ),
                                attestation=dict(
                                    body.get("attestation") or {}
                                ),
                                approval={
                                    "approved":True,
                                    "approved_by":principal.name,
                                    "role":principal.role,
                                    **(
                                        {
                                            "reason":str(
                                                body["approval_reason"]
                                            )
                                        }
                                        if body.get("approval_reason")
                                        else {}
                                    ),
                                },
                                metadata=dict(
                                    body.get("metadata") or {}
                                ),
                            )
                            self._send(
                                HTTPStatus.CREATED,
                                {"release":release},
                            )
                            return
                        if action == "releases":
                            self._send(
                                HTTPStatus.OK,
                                {
                                    "releases":
                                        control.releases.list_for_workflow(
                                            workflow_id
                                        )
                                },
                            )
                            return
                        if action == "artifacts":
                            artifact = control.workflows.add_artifact(
                                workflow_id,
                                task_id=(
                                    str(body["task_id"])
                                    if body.get("task_id")
                                    else None
                                ),
                                name=str(body["name"]),
                                uri=str(body["uri"]),
                                sha256=(
                                    str(body["sha256"])
                                    if body.get("sha256")
                                    else None
                                ),
                                metadata=dict(body.get("metadata") or {}),
                            )
                            self._send(
                                HTTPStatus.CREATED,
                                {"artifact":artifact},
                            )
                            return

                if parsed.path == "/v1/workers/register":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    worker = control.workers.register(
                        str(body["worker_id"]),
                        [str(x) for x in body.get("capabilities", [])],
                        int(body.get("max_concurrency", 1)),
                    )
                    self._send(HTTPStatus.OK, {"worker":worker.to_dict()})
                    return

                if parsed.path == "/v1/workers/heartbeat":
                    principal = self._require("worker")
                    if principal is None:
                        return
                    worker = control.workers.heartbeat(
                        str(body["worker_id"]),
                        active_tasks=(
                            int(body["active_tasks"])
                            if "active_tasks" in body
                            else None
                        ),
                        capacity=(
                            dict(body["capacity"])
                            if "capacity" in body
                            and isinstance(body["capacity"], dict)
                            else None
                        ),
                    )
                    active_job_keys = body.get(
                        "active_job_keys",
                        [],
                    )
                    if not isinstance(active_job_keys, list):
                        raise ValueError(
                            "active_job_keys must be a list"
                        )
                    stale_job_keys = []
                    for key in active_job_keys:
                        try:
                            job = control.queue.get(str(key))
                        except KeyError:
                            stale_job_keys.append(str(key))
                            continue
                        if not control.workflows.job_generation_current(
                            job
                        ):
                            stale_job_keys.append(str(key))
                    self._send(
                        HTTPStatus.OK,
                        {
                            "worker":worker.to_dict(),
                            "stale_job_keys":stale_job_keys,
                        },
                    )
                    return

                if parsed.path == "/v1/incident-snapshot":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    allowed = {"validator_id", "builder_id", "key_id"}
                    unknown = sorted(set(body) - allowed)
                    if unknown:
                        self._send(
                            HTTPStatus.BAD_REQUEST,
                            {
                                "error": "unknown incident snapshot fields",
                                "fields": unknown,
                            },
                        )
                        return
                    filters = {}
                    for name in allowed:
                        value = body.get(name)
                        if value is None:
                            filters[name] = None
                            continue
                        if not isinstance(value, str) or not value.strip():
                            self._send(
                                HTTPStatus.BAD_REQUEST,
                                {
                                    "error":
                                        f"{name} must be a non-empty string",
                                },
                            )
                            return
                        if len(value) > 512:
                            self._send(
                                HTTPStatus.BAD_REQUEST,
                                {"error": f"{name} is too long"},
                            )
                            return
                        filters[name] = value.strip()
                    result = control.releases.record_incident_report(
                        validator_id=filters["validator_id"],
                        builder_id=filters["builder_id"],
                        key_id=filters["key_id"],
                    )
                    self._send(
                        HTTPStatus.CREATED if result["recorded"]
                        else HTTPStatus.OK,
                        {
                            "schema_version":
                                "production-os/trust-incident-snapshot/v1",
                            **result,
                        },
                    )
                    return

                if parsed.path.startswith("/v1/releases/"):
                    parts = [
                        part
                        for part in parsed.path.split("/")
                        if part
                    ]
                    if (
                        len(parts) == 4
                        and parts[1] == "releases"
                        and parts[3] == "rollback"
                    ):
                        principal = self._require("operator")
                        if principal is None:
                            return
                        release = control.releases.rollback(
                            parts[2],
                            reason=str(body.get("reason") or ""),
                            metadata=dict(
                                body.get("metadata") or {}
                            ),
                        )
                        self._send(
                            HTTPStatus.CREATED,
                            {"release":release},
                        )
                        return

                if parsed.path == "/v1/jobs/enqueue":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    job = control.queue.enqueue(body)
                    self._send(HTTPStatus.CREATED, {"job":job})
                    return

                if parsed.path == "/v1/jobs/claim":
                    principal = self._require("worker")
                    if principal is None:
                        return

                    worker_id = str(body["worker_id"])
                    capabilities = [
                        str(x) for x in body.get("capabilities", [])
                    ]

                    compatible = []
                    for queued in control.queue.peek_candidates(
                        worker_id=worker_id,
                        limit=100,
                    ):
                        if not control.workflows.job_generation_current(
                            queued
                        ):
                            continue
                        required = set(
                            queued["payload"].get(
                                "required_capabilities",
                                [],
                            )
                        )
                        if required.issubset(set(capabilities)):
                            compatible.append(queued)

                    if not compatible:
                        self._send(HTTPStatus.NO_CONTENT, {})
                        return

                    ranked = control.portfolio.rank(compatible)
                    candidate = ranked[0]["job"]

                    assigned = candidate.get("assigned_worker")
                    control.workers.load()
                    available_workers = list(
                        control.workers.workers.values()
                    )
                    if assigned:
                        available_workers = [
                            worker
                            for worker in available_workers
                            if worker.worker_id == assigned
                        ]

                    placement = control.optimizer.choose_worker(
                        repository=candidate["repository"],
                        task=candidate["task"],
                        workers=available_workers,
                        required_capabilities=list(
                            candidate["payload"].get(
                                "required_capabilities",
                                [],
                            )
                        ),
                        fallback_minutes=float(
                            candidate["payload"]
                            .get("handoff", {})
                            .get("estimated_minutes", 1.0)
                        ),
                    )
                    if (
                        placement is not None
                        and placement.worker_id != worker_id
                    ):
                        self._send(HTTPStatus.NO_CONTENT, {})
                        return

                    job = control.queue.claim_key(
                        candidate["key"],
                        worker_id,
                        ack_timeout_seconds=int(
                            body.get("ack_timeout_seconds", 120)
                        ),
                    )
                    if job is None:
                        self._send(HTTPStatus.NO_CONTENT, {})
                        return

                    self._send(
                        HTTPStatus.OK,
                        {
                            "job":job,
                            "optimization":{
                                "portfolio_score":ranked[0]["score"],
                                "critical":ranked[0]["critical"],
                                "descendants":ranked[0]["descendants"],
                                "predicted_minutes":ranked[0][
                                    "predicted_minutes"
                                ],
                            },
                        },
                    )
                    return

                if parsed.path == "/v1/jobs/ack":
                    principal = self._require("worker")
                    if principal is None:
                        return
                    key = str(body["key"])
                    before = control.queue.get(key)
                    if not control.workflows.job_generation_current(
                        before
                    ):
                        self._send(
                            HTTPStatus.CONFLICT,
                            {
                                "error":"stale workflow generation",
                                "key":key,
                            },
                        )
                        return
                    job = control.queue.ack(
                        key,
                        str(body["worker_id"]),
                    )
                    self._send(HTTPStatus.OK, {"job":job})
                    return

                if parsed.path == "/v1/jobs/stale-checkpoint":
                    principal = self._require("worker")
                    if principal is None:
                        return
                    key = str(body["key"])
                    worker_id = str(body["worker_id"])
                    checkpoint_ref = str(
                        body.get("checkpoint_ref") or ""
                    ).strip()
                    if not checkpoint_ref:
                        raise ValueError("checkpoint_ref is required")

                    job = control.queue.get(key)
                    if job.get("claimed_by") != worker_id:
                        raise RuntimeError("job claim owner mismatch")
                    if control.workflows.job_generation_current(job):
                        raise RuntimeError(
                            "job is not from a stale workflow generation"
                        )

                    payload = dict(job.get("payload") or {})
                    with control.backend.transaction() as db:
                        control.backend.append_event(
                            db,
                            "stale-job-checkpointed",
                            {
                                "job_key":key,
                                "worker_id":worker_id,
                                "checkpoint_ref":checkpoint_ref,
                                "workflow_id":payload.get(
                                    "workflow_id"
                                ),
                                "workflow_generation":payload.get(
                                    "workflow_generation"
                                ),
                                "source_revision":payload.get(
                                    "source_revision"
                                ),
                            },
                            repository=job.get("repository"),
                            task_key_value=key,
                        )

                    self._send(
                        HTTPStatus.OK,
                        {
                            "status":"checkpointed",
                            "key":key,
                            "checkpoint_ref":checkpoint_ref,
                        },
                    )
                    return

                if parsed.path == "/v1/jobs/complete":
                    principal = self._require("worker")
                    if principal is None:
                        return
                    key = str(body["key"])
                    worker_id = str(body["worker_id"])
                    before = control.queue.get(key)
                    if not control.workflows.job_generation_current(
                        before
                    ):
                        self._send(
                            HTTPStatus.CONFLICT,
                            {
                                "error":"stale workflow generation",
                                "key":key,
                            },
                        )
                        return

                    duration_seconds = body.get("duration_seconds")
                    if duration_seconds is not None:
                        control.optimizer.record_execution(
                            repository=before["repository"],
                            task=before["task"],
                            worker_id=worker_id,
                            duration_seconds=float(duration_seconds),
                            succeeded=True,
                            capabilities=[
                                str(x)
                                for x in body.get("capabilities", [])
                            ],
                        )

                    group_id = control.speculation.group_for_job(key)
                    if (
                        group_id is not None
                        and not control.speculation.try_win(
                            group_id,
                            key,
                        )
                    ):
                        job = control.speculation.cancel_job(key)
                        self._send(
                            HTTPStatus.OK,
                            {
                                "job":job,
                                "workflow":None,
                                "speculation":{
                                    "group_id":group_id,
                                    "winner":False,
                                },
                            },
                        )
                        return

                    job = control.queue.complete(key, worker_id)
                    cancelled = []
                    if group_id is not None:
                        cancelled = control.speculation.cancel_losers(
                            group_id,
                            key,
                        )

                    workflow_id = before["payload"].get("workflow_id")
                    workflow_task_id = before["payload"].get(
                        "workflow_task_id"
                    )
                    workflow = None
                    if workflow_id and workflow_task_id:
                        workflow = control.workflows.record_result(
                            str(workflow_id),
                            str(workflow_task_id),
                            succeeded=True,
                            result=dict(body.get("result") or {}),
                        )

                    self._send(
                        HTTPStatus.OK,
                        {
                            "job":job,
                            "workflow":workflow,
                            "speculation":{
                                "group_id":group_id,
                                "winner":True,
                                "cancelled_losers":cancelled,
                            } if group_id else None,
                        },
                    )
                    return

                if parsed.path == "/v1/jobs/fail":
                    principal = self._require("worker")
                    if principal is None:
                        return
                    key = str(body["key"])
                    worker_id = str(body["worker_id"])
                    reason = str(body.get("reason", "worker failure"))
                    before = control.queue.get(key)
                    if not control.workflows.job_generation_current(
                        before
                    ):
                        self._send(
                            HTTPStatus.CONFLICT,
                            {
                                "error":"stale workflow generation",
                                "key":key,
                            },
                        )
                        return

                    duration_seconds = body.get("duration_seconds")
                    if duration_seconds is not None:
                        control.optimizer.record_execution(
                            repository=before["repository"],
                            task=before["task"],
                            worker_id=worker_id,
                            duration_seconds=float(duration_seconds),
                            succeeded=False,
                            capabilities=[
                                str(x)
                                for x in body.get("capabilities", [])
                            ],
                        )

                    job = control.queue.fail(
                        key,
                        worker_id,
                        reason,
                    )
                    group_id = control.speculation.group_for_job(key)
                    if (
                        group_id is not None
                        and not control.speculation.failure_is_terminal(
                            group_id,
                            key,
                        )
                    ):
                        self._send(
                            HTTPStatus.OK,
                            {
                                "job":job,
                                "workflow":None,
                                "speculation":{
                                    "group_id":group_id,
                                    "terminal_failure":False,
                                },
                            },
                        )
                        return

                    workflow_id = before["payload"].get("workflow_id")
                    workflow_task_id = before["payload"].get(
                        "workflow_task_id"
                    )
                    workflow = None
                    if workflow_id and workflow_task_id:
                        workflow = control.workflows.record_result(
                            str(workflow_id),
                            str(workflow_task_id),
                            succeeded=False,
                            result={
                                "reason":reason,
                                **dict(body.get("result") or {}),
                            },
                        )

                    self._send(
                        HTTPStatus.OK,
                        {
                            "job":job,
                            "workflow":workflow,
                            "speculation":{
                                "group_id":group_id,
                                "terminal_failure":True,
                            } if group_id else None,
                        },
                    )
                    return

                if parsed.path == "/v1/jobs/recover":
                    principal = self._require("operator")
                    if principal is None:
                        return
                    actions = control.queue.recover_expired(
                        max_attempts=int(body.get("max_attempts", 3))
                    )
                    self._send(
                        HTTPStatus.OK,
                        {"actions":actions},
                    )
                    return

                self._send(HTTPStatus.NOT_FOUND, {"error":"not found"})
            except KeyError as exc:
                self._send(
                    HTTPStatus.BAD_REQUEST,
                    {"error":f"missing field: {exc.args[0]}"},
                )
            except (ValueError, RuntimeError) as exc:
                self._send(
                    HTTPStatus.CONFLICT,
                    {"error":str(exc)},
                )

    return Handler


def serve_control_plane(
    database: str,
    auth_config: str,
    *,
    host: str = "127.0.0.1",
    port: int = 8787,
    github_webhook_secret: str | None = None,
    trusted_validation_secrets: dict[str, str] | None = None,
    provenance_secret: str | None = None,
    trusted_validation_public_keys: dict[str, str] | None = None,
    provenance_private_key: str | None = None,
    provenance_public_key: str | None = None,
    provenance_signer=None,
    validation_signature_policy: str = "compatible",
    builder_id: str = "https://production-os.local/builder",
    builder_private_key: str | None = None,
    builder_signer=None,
    trusted_builders: dict | None = None,
    trusted_builder_keys: dict | None = None,
    require_trusted_builder: bool = False,
) -> None:
    control = ControlPlane(
        database,
        authorizer=TokenAuthorizer.load(auth_config),
        github_webhook_secret=github_webhook_secret,
        trusted_validation_secrets=trusted_validation_secrets,
        provenance_secret=provenance_secret,
        trusted_validation_public_keys=trusted_validation_public_keys,
        provenance_private_key=provenance_private_key,
        provenance_public_key=provenance_public_key,
    )
    server = ThreadingHTTPServer(
        (host, port),
        make_handler(control),
    )
    server.serve_forever()
