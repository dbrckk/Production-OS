from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .api_auth import Principal, TokenAuthorizer
from .storage import job_queue_for, open_backend, worker_registry_for
from .workflow_engine import WorkflowEngine, WorkflowTaskSpec
from .execution_optimizer import ExecutionOptimizer
from .speculation import SpeculationManager
from .portfolio_optimizer import PortfolioOptimizer
from .github_client import GitHubClient
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
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0b1020">
<title>Production-OS</title>
<style>
:root{
 --bg:#080d18;--panel:#101827;--panel2:#151f31;--line:#25324a;--text:#f4f7fb;
 --muted:#94a3b8;--accent:#6ea8fe;--accent2:#8b5cf6;--ok:#34d399;--warn:#fbbf24;
 --bad:#fb7185;--shadow:0 20px 50px rgba(0,0,0,.28);--radius:18px
}
*{box-sizing:border-box}
html{background:var(--bg)}
body{
 margin:0;min-height:100vh;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
 color:var(--text);background:
 radial-gradient(circle at 10% -10%,rgba(110,168,254,.18),transparent 34rem),
 radial-gradient(circle at 100% 0,rgba(139,92,246,.15),transparent 28rem),var(--bg)
}
.shell{max-width:900px;margin:0 auto;padding:18px 14px 48px}
.topbar{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:16px}
.brand{display:flex;align-items:center;gap:12px;min-width:0}
.logo{
 width:42px;height:42px;border-radius:13px;display:grid;place-items:center;font-weight:900;
 background:linear-gradient(135deg,var(--accent),var(--accent2));box-shadow:0 12px 30px rgba(110,168,254,.24)
}
.brand h1{font-size:1.28rem;margin:0;letter-spacing:-.02em}
.brand p{margin:2px 0 0;color:var(--muted);font-size:.82rem}
.icon-btn,.secondary-btn,.primary-btn{
 border:1px solid var(--line);color:var(--text);background:var(--panel2);cursor:pointer;
 border-radius:13px;font:inherit;font-weight:700;transition:.15s ease
}
.icon-btn{width:44px;height:44px;padding:0;font-size:1.15rem}
.icon-btn:active,.secondary-btn:active,.primary-btn:active{transform:scale(.98)}
.status-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:14px}
.status-card{background:rgba(16,24,39,.88);border:1px solid var(--line);border-radius:15px;padding:11px 12px;min-width:0}
.status-label{font-size:.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:.07em}
.status-value{font-size:.88rem;font-weight:800;margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px;background:var(--muted)}
.dot.ok{background:var(--ok);box-shadow:0 0 0 4px rgba(52,211,153,.10)}
.dot.warn{background:var(--warn);box-shadow:0 0 0 4px rgba(251,191,36,.10)}
.dot.bad{background:var(--bad);box-shadow:0 0 0 4px rgba(251,113,133,.10)}
.card{background:rgba(16,24,39,.94);border:1px solid var(--line);border-radius:var(--radius);padding:17px;margin-bottom:14px;box-shadow:var(--shadow)}
.card h2{font-size:1rem;margin:0 0 14px}
label{display:block;font-size:.82rem;font-weight:800;color:#cbd5e1;margin-bottom:6px}
select,textarea,input{
 width:100%;border:1px solid var(--line);background:#0c1422;color:var(--text);
 border-radius:13px;font:inherit;padding:12px 13px;outline:none
}
select:focus,textarea:focus,input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(110,168,254,.12)}
select{margin-bottom:14px}
textarea{resize:vertical;min-height:150px;line-height:1.45}
.launch-row{display:grid;grid-template-columns:1fr auto;gap:9px;margin-top:13px}
.primary-btn{
 border:none;padding:13px 17px;background:linear-gradient(135deg,#4f8dfd,#7c5ce7);
 box-shadow:0 12px 28px rgba(79,141,253,.22);min-height:48px
}
.primary-btn[disabled]{opacity:.55;cursor:wait}
.secondary-btn{padding:11px 14px}
.status-message{margin:11px 0 0;min-height:20px;font-size:.88rem;font-weight:700;color:#cbd5e1}
.worker-detail{margin:7px 0 0;color:var(--muted);font-size:.8rem}
.runtime-warning{display:none;margin-top:10px;padding:10px 12px;border-radius:12px;background:rgba(251,191,36,.10);border:1px solid rgba(251,191,36,.25);color:#fde68a;font-size:.82rem}
.runtime-warning.show{display:block}
.section-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:9px}
.section-head h2{margin:0}
.badge{display:inline-flex;align-items:center;border-radius:999px;padding:5px 9px;font-size:.75rem;font-weight:800;background:#1e293b;color:#cbd5e1}
.run-list{display:grid;gap:8px}
.run{
 display:grid;grid-template-columns:1fr auto;gap:8px;align-items:center;padding:11px 12px;
 border:1px solid var(--line);border-radius:13px;background:#0c1422
}
.run-title{font-size:.85rem;font-weight:800;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.run-meta{font-size:.74rem;color:var(--muted);margin-top:3px}
.run-state{font-size:.72rem;font-weight:900;border-radius:999px;padding:5px 8px}
.state-succeeded{background:rgba(52,211,153,.12);color:#6ee7b7}
.state-running,.state-ready,.state-pending{background:rgba(110,168,254,.12);color:#93c5fd}
.state-failed,.state-cancelled{background:rgba(251,113,133,.12);color:#fda4af}
.state-other{background:#1e293b;color:#cbd5e1}
.empty{color:var(--muted);font-size:.84rem;padding:7px 2px}
.quality-badge{display:inline-block;padding:5px 10px;border-radius:999px;font-weight:800;font-size:.78rem}
.quality-ok{background:rgba(52,211,153,.12);color:#6ee7b7}
.quality-regenerated{background:rgba(251,191,36,.12);color:#fde68a}
.quality-low{background:rgba(251,113,133,.12);color:#fda4af}
.quality-unknown{background:#1e293b;color:#cbd5e1}
.small{font-size:.8rem;color:var(--muted)}
.asset-row{display:flex;gap:10px;align-items:center;padding:9px 0;border-top:1px solid var(--line)}
.asset-thumb{width:50px;height:50px;object-fit:contain;border-radius:10px;background:#07101c}
.asset-meta{min-width:0;overflow-wrap:anywhere}
.asset-meta a{color:#bfdbfe;text-decoration:none}
.history-row{padding:7px 0;border-top:1px solid var(--line);font-size:.8rem;color:var(--muted)}
#settings{display:none;position:fixed;z-index:1000;inset:0;padding:18px;background:rgba(3,7,18,.72);backdrop-filter:blur(8px);overflow:auto}
#settings.open{display:block}
.settings-panel{max-width:520px;margin:8vh auto 0;background:#101827;border:1px solid var(--line);border-radius:20px;padding:18px;box-shadow:0 30px 80px rgba(0,0,0,.45)}
.settings-panel h2{margin:0 0 7px}
.settings-actions{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}
.settings-actions .secondary-btn:last-child{grid-column:1/-1}
.pair-feedback{min-height:18px;margin-top:9px;font-size:.8rem;font-weight:700}
.footer-note{text-align:center;color:#64748b;font-size:.72rem;margin-top:18px}
@media(max-width:560px){
 .shell{padding:14px 12px 38px}
 .status-grid{grid-template-columns:1fr}
 .status-card{display:flex;justify-content:space-between;align-items:center;gap:10px}
 .status-value{margin-top:0;text-align:right}
 .card{padding:15px}
 .launch-row{grid-template-columns:1fr auto}
 textarea{min-height:180px}
 .settings-panel{margin-top:3vh}
}
</style>
</head>
<body>
<div class="shell">
 <div class="topbar">
  <div class="brand">
   <div class="logo">P</div>
   <div><h1>Production-OS</h1><p>Centre de production autonome</p></div>
  </div>
  <button id="settings-button" class="icon-btn" type="button" onclick="toggleSettings()" aria-label="Settings">⚙</button>
 </div>

 <div class="status-grid">
  <div class="status-card"><div class="status-label">Serveur</div><div id="server-state" class="status-value"><span class="dot warn"></span>Vérification</div></div>
  <div class="status-card"><div class="status-label">Appairage</div><div id="pair-state" class="status-value"><span class="dot warn"></span>Non appairé</div></div>
  <div class="status-card"><div class="status-label">Worker</div><div id="worker-state" class="status-value"><span class="dot warn"></span>Vérification</div></div>
 </div>

 <div class="card">
  <h2>Nouvelle production</h2>
  <label for="repository">Repository</label>
  <select id="repository"><option value="dbrckk/Jumpy">dbrckk/Jumpy</option></select>
  <label for="instruction">Instruction</label>
  <textarea id="instruction" rows="7" placeholder="Décris le résultat final attendu. Production-OS s'occupe de l'exécution."></textarea>
  <div class="launch-row">
   <button id="launch-button" class="primary-btn" onclick="launchWorkflow()">Lancer la production</button>
   <button class="secondary-btn" type="button" onclick="refreshDashboard()" aria-label="Actualiser">↻</button>
  </div>
  <p id="launch-status" class="status-message"></p>
  <p id="worker-status" class="worker-detail">Capacités worker : vérification...</p>
  <div id="runtime-warning" class="runtime-warning">Worker hors ligne : la production peut être créée, mais elle restera en attente jusqu'à la reconnexion du moteur d'exécution.</div>
 </div>

 <div class="card">
  <div class="section-head"><h2>Productions récentes</h2><span id="runs-count" class="badge">0</span></div>
  <div id="recent-runs" class="run-list"><div class="empty">Aucune production chargée.</div></div>
 </div>

 <div class="card">
  <div class="section-head"><h2>Qualité visuelle</h2><span id="visual-quality" class="quality-badge quality-unknown">Inconnu</span></div>
  <p id="visual-quality-detail" class="small">Aucun résultat visuel chargé.</p>
  <div id="visual-assets-list" class="small"></div>
  <h3 style="font-size:.85rem;margin:15px 0 6px">Historique</h3>
  <div id="visual-quality-history" class="small"></div>
 </div>

 <p class="footer-note">Production-OS · tableau de contrôle mobile</p>
</div>

<div id="settings">
 <div class="settings-panel">
  <div class="section-head"><h2>Appairage</h2><button class="icon-btn" type="button" onclick="setSettingsOpen(false)" aria-label="Fermer">×</button></div>
  <p class="small">À faire une seule fois sur cet appareil. Le token reste dans le stockage local de ce navigateur.</p>
  <input id="pair-token" type="password" placeholder="Operator token" autocomplete="off">
  <div id="pair-feedback" class="pair-feedback"></div>
  <div class="settings-actions">
   <button class="primary-btn" type="button" onclick="savePairing()">Enregistrer</button>
   <button class="secondary-btn" type="button" onclick="clearPairing()">Oublier</button>
   <button class="secondary-btn" type="button" onclick="setSettingsOpen(false)">Fermer</button>
  </div>
 </div>
</div>

<script>
const TOKEN_KEY='production_os_operator_token';
let workerOnline=false;
let refreshBusy=false;

function token(){return localStorage.getItem(TOKEN_KEY)||''}
function esc(value){return String(value).replace(/[&<>"']/g,function(ch){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]})}
function dot(state){return '<span class="dot '+state+'"></span>'}
function setState(id,state,text){document.getElementById(id).innerHTML=dot(state)+esc(text)}
function setSettingsOpen(open){
 const el=document.getElementById('settings');
 el.classList.toggle('open',Boolean(open));
 if(open){setTimeout(function(){document.getElementById('pair-token').focus()},0)}
}
function toggleSettings(){const el=document.getElementById('settings');setSettingsOpen(!el.classList.contains('open'))}

async function api(path,options){
 options=options||{};
 const secret=token();
 if(!secret) throw new Error('Cet appareil doit être appairé une seule fois via ⚙.');
 const headers=Object.assign(
  {Authorization:'Bearer '+secret},
  options.body?{'Content-Type':'application/json'}:{},
  options.headers||{}
 );
 const r=await fetch(path,Object.assign({},options,{headers:headers}));
 if(!r.ok){
  let detail='';
  try{
   const payload=await r.json();
   detail=String(payload.error||'');
  }catch(_e){
   try{detail=(await r.text()).slice(0,180)}catch(_ignore){}
  }
  if(r.status===401) throw new Error('Token opérateur refusé par le serveur.');
  if(r.status===403) throw new Error('Ce token n’a pas le rôle requis.');
  throw new Error(detail||('Erreur serveur '+r.status));
 }
 if(r.status===204) return {};
 return await r.json();
}

async function checkServer(){
 try{
  const r=await fetch('/health',{cache:'no-store'});
  if(!r.ok) throw new Error('health');
  setState('server-state','ok','En ligne');
  return true;
 }catch(_e){
  setState('server-state','bad','Indisponible');
  return false;
 }
}

async function savePairing(){
 const input=document.getElementById('pair-token');
 const value=input.value.trim();
 const feedback=document.getElementById('pair-feedback');
 const status=document.getElementById('launch-status');
 if(!value){feedback.textContent='Entre le token opérateur.';return}
 const previous=token();
 localStorage.setItem(TOKEN_KEY,value);
 feedback.textContent='Vérification de l’appairage...';
 status.textContent='Vérification de l’appairage...';
 try{
  await api('/v1/workers');
  input.value='';
  feedback.textContent='';
  setSettingsOpen(false);
  setState('pair-state','ok','Appairé');
  status.textContent='Appareil appairé.';
  await refreshDashboard();
 }catch(e){
  if(previous) localStorage.setItem(TOKEN_KEY,previous); else localStorage.removeItem(TOKEN_KEY);
  setState('pair-state','bad','Token refusé');
  feedback.textContent=String(e).replace(/^Error:\s*/,'');
  status.textContent='Token opérateur invalide. Vérifie le token puis réessaie.';
 }
}

function clearPairing(){
 localStorage.removeItem(TOKEN_KEY);
 setState('pair-state','warn','Non appairé');
 setState('worker-state','warn','Appairage requis');
 document.getElementById('launch-status').textContent='Appairage supprimé.';
 document.getElementById('worker-status').textContent='Worker : appairage requis via ⚙.';
 document.getElementById('pair-feedback').textContent='';
 workerOnline=false;
}

async function loadRepositories(){
 try{
  const r=await fetch('https://api.github.com/users/dbrckk/repos?per_page=100&sort=pushed');
  if(!r.ok) return;
  const repos=await r.json();
  const select=document.getElementById('repository');
  const selected=select.value;
  select.innerHTML='';
  repos.filter(function(x){return !x.archived}).sort(function(a,b){return a.name.localeCompare(b.name)}).forEach(function(x){
   const option=document.createElement('option');
   option.value=x.full_name;
   option.textContent=x.full_name;
   if(x.full_name===selected||(!selected&&x.full_name==='dbrckk/Jumpy')) option.selected=true;
   select.appendChild(option);
  });
 }catch(_e){}
}

async function loadWorkerStatus(){
 const el=document.getElementById('worker-status');
 const warning=document.getElementById('runtime-warning');
 if(!token()){
  setState('pair-state','warn','Non appairé');
  setState('worker-state','warn','Appairage requis');
  el.textContent='Worker : appairage requis via ⚙.';
  warning.classList.remove('show');
  workerOnline=false;
  return;
 }
 setState('pair-state','ok','Appairé');
 try{
  const data=await api('/v1/workers');
  const online=(data.workers||[]).filter(function(x){return x.status==='online'});
  const capabilities=new Set(online.flatMap(function(x){return x.capabilities||[]}));
  const visual=capabilities.has('visual-asset-production');
  const threeD=capabilities.has('visual-asset-3d-production');
  workerOnline=online.length>0;
  if(workerOnline){
   setState('worker-state','ok',online.length+' en ligne');
   warning.classList.remove('show');
  }else{
   setState('worker-state','warn','Hors ligne');
   warning.classList.add('show');
  }
  el.textContent='Worker : code '+(online.length?'✓':'—')
   +' · assets 2D/SVG '+(visual?'✓':'—')
   +' · 3D '+(threeD?'✓':'—');
 }catch(e){
  workerOnline=false;
  const message=String(e).replace(/^Error:\s*/,'');
  setState('worker-state','bad','Erreur');
  el.textContent='Capacités worker : indisponibles · '+message;
  warning.classList.add('show');
 }
}

function workflowState(status){
 const value=String(status||'unknown').toLowerCase();
 if(value==='succeeded') return ['Terminé','state-succeeded'];
 if(value==='failed') return ['Échec','state-failed'];
 if(value==='cancelled'||value==='canceled') return ['Annulé','state-cancelled'];
 if(value==='running') return ['En cours','state-running'];
 if(value==='ready'||value==='pending'||value==='queued') return ['En attente','state-pending'];
 return [value||'Inconnu','state-other'];
}

async function loadRecentRuns(){
 const listEl=document.getElementById('recent-runs');
 const countEl=document.getElementById('runs-count');
 if(!token()){
  listEl.innerHTML='<div class="empty">Appairage requis pour afficher les productions.</div>';
  countEl.textContent='0';
  return;
 }
 try{
  const list=await api('/v1/workflows');
  const selectedRepository=document.getElementById('repository').value.trim();
  const workflows=(list.workflows||[]).filter(function(item){return !selectedRepository||item.repository===selectedRepository}).slice(0,8);
  countEl.textContent=String(workflows.length);
  if(!workflows.length){
   listEl.innerHTML='<div class="empty">Aucune production pour ce repository.</div>';
   return;
  }
  listEl.innerHTML=workflows.map(function(item){
   const state=workflowState(item.status);
   const when=String(item.updated_at||item.created_at||'').replace('T',' ').replace('Z','').slice(0,19);
   return '<div class="run"><div><div class="run-title">'+esc(item.name||item.id)+'</div>'
    +'<div class="run-meta">'+esc(when)+' · '+esc(String(item.id||'').slice(0,12))+'</div></div>'
    +'<div class="run-state '+state[1]+'">'+state[0]+'</div></div>';
  }).join('');
 }catch(e){
  listEl.innerHTML='<div class="empty">Productions indisponibles · '+esc(String(e).replace(/^Error:\s*/,''))+'</div>';
 }
}

function githubAssetUrls(repository,path){
 const repo=String(repository||'').trim();
 const value=String(path||'').replace(/^\\/+/, '');
 if(!/^[A-Za-z0-9_.-]+\\/[A-Za-z0-9_.-]+$/.test(repo)||!value||value.includes('..')) return null;
 const encoded=value.split('/').map(encodeURIComponent).join('/');
 return {view:'https://github.com/'+repo+'/blob/main/'+encoded,raw:'https://raw.githubusercontent.com/'+repo+'/main/'+encoded};
}
function isPreviewableAsset(path){return /\.(png|webp|jpe?g|gif|svg)$/i.test(String(path||''))}
function qualityView(status){
 if(status==='ok') return ['OK','quality-ok'];
 if(status==='regenerated') return ['Régénéré','quality-regenerated'];
 if(status==='low_quality') return ['Qualité faible','quality-low'];
 return ['Inconnu','quality-unknown'];
}
function extractVisualQuality(workflow){
 const tasks=(workflow&&workflow.tasks)||[];
 for(let i=tasks.length-1;i>=0;i--){
  const result=tasks[i]&&tasks[i].result;
  if(!result) continue;
  const direct=result.evidence&&result.evidence.visual_assets;
  const nested=result.result&&result.result.evidence&&result.result.evidence.visual_assets;
  const value=direct||nested;
  if(value) return value;
 }
 return null;
}
async function loadVisualQuality(){
 const badge=document.getElementById('visual-quality');
 const detail=document.getElementById('visual-quality-detail');
 if(!token()){
  const view=qualityView('unknown');badge.textContent=view[0];badge.className='quality-badge '+view[1];
  detail.textContent='Appaire cet appareil via ⚙ pour afficher la qualité des derniers assets.';return;
 }
 try{
  const list=await api('/v1/workflows');
  const selectedRepository=document.getElementById('repository').value.trim();
  const workflows=(list.workflows||[]).filter(function(item){return item.repository===selectedRepository});
  if(!workflows.length){
   const view=qualityView('unknown');badge.textContent=view[0];badge.className='quality-badge '+view[1];
   detail.textContent='Aucun workflow visuel pour ce repository.';return;
  }
  const recent=await Promise.all(workflows.slice(0,5).map(function(item){return api('/v1/workflows/'+encodeURIComponent(item.id))}));
  const latest=recent[0];
  const visual=extractVisualQuality(latest.workflow);
  if(!visual){
   const view=qualityView('unknown');badge.textContent=view[0];badge.className='quality-badge '+view[1];
   detail.textContent='Aucun contrôle visuel sur le dernier workflow.';return;
  }
  const view=qualityView(visual.quality_status);badge.textContent=view[0];badge.className='quality-badge '+view[1];
  const parts=[];
  if(Number.isFinite(Number(visual.checked))) parts.push('contrôlés '+Number(visual.checked));
  if(Number.isFinite(Number(visual.regenerated))) parts.push('régénérés '+Number(visual.regenerated));
  if(Number.isFinite(Number(visual.cache_hits))) parts.push('cache '+Number(visual.cache_hits));
  if(Number.isFinite(Number(visual.exact_duplicates))&&Number(visual.exact_duplicates)>0) parts.push('doublons exacts '+Number(visual.exact_duplicates));
  if(Number.isFinite(Number(visual.near_duplicates))&&Number(visual.near_duplicates)>0) parts.push('quasi-doublons '+Number(visual.near_duplicates));
  if(visual.minimum_score!==null&&visual.minimum_score!==undefined) parts.push('score min '+Number(visual.minimum_score).toFixed(2));
  detail.textContent=parts.length?parts.join(' · '):'Contrôle visuel disponible.';
  const assetList=document.getElementById('visual-assets-list');
  const rows=Array.isArray(visual.items)?visual.items:[];
  assetList.innerHTML=rows.slice(0,12).map(function(item){
   const score=item.score===null||item.score===undefined?'—':Number(item.score).toFixed(2);
   const attempts=Number(item.attempts||0);
   const semantic=item.semantic_score===null||item.semantic_score===undefined?'':' · art '+Number(item.semantic_score).toFixed(2);
   const cache=item.cache_hit?' · cache':'';
   const regenerated=item.regenerated?' · régénéré':'';
   const libraryVersion=item.library_version===null||item.library_version===undefined?'':' · lib v'+Number(item.library_version);
   const libraryQuality=item.library_quality===null||item.library_quality===undefined?'':' · qualité lib '+Number(item.library_quality).toFixed(2);
   const preferred=item.library_preferred===true?' · préférée':'';
   const duplicate=item.library_duplicate_of?' · doublon':'';
   const target=String(item.target_path||item.id||'asset');
   const sha=String(item.sha256||'').slice(0,10);
   const urls=githubAssetUrls(selectedRepository,target);
   const thumb=urls&&isPreviewableAsset(target)?'<a href="'+esc(urls.view)+'" target="_blank" rel="noreferrer"><img class="asset-thumb" loading="lazy" src="'+esc(urls.raw)+'" alt=""></a>':'';
   const link=urls?'<a href="'+esc(urls.view)+'" target="_blank" rel="noreferrer">'+esc(target)+'</a>':'<b>'+esc(target)+'</b>';
   return '<div class="asset-row">'+thumb+'<div class="asset-meta">'+link
    +'<div>cohérence '+score+semantic+' · essais '+attempts+cache+regenerated+libraryVersion+libraryQuality+preferred+duplicate+(sha?' · '+esc(sha):'')+'</div></div></div>';
  }).join('');
  const history=document.getElementById('visual-quality-history');
  history.innerHTML=recent.map(function(entry){
   const workflow=entry.workflow||{};const itemVisual=extractVisualQuality(workflow);
   const status=itemVisual?itemVisual.quality_status:'unknown';const itemView=qualityView(status);
   const when=String(workflow.updated_at||workflow.created_at||'').replace('T',' ').replace('Z','');
   const min=itemVisual&&itemVisual.minimum_score!==null&&itemVisual.minimum_score!==undefined?' · score '+Number(itemVisual.minimum_score).toFixed(2):'';
   return '<div class="history-row"><span class="quality-badge '+itemView[1]+'">'+itemView[0]+'</span> '+esc(when)+min+'</div>';
  }).join('');
 }catch(_e){
  const view=qualityView('unknown');badge.textContent=view[0];badge.className='quality-badge '+view[1];
  detail.textContent='Qualité visuelle indisponible.';
  document.getElementById('visual-assets-list').innerHTML='';
  document.getElementById('visual-quality-history').innerHTML='';
 }
}

async function launchWorkflow(){
 const status=document.getElementById('launch-status');
 const button=document.getElementById('launch-button');
 if(!token()){
  status.textContent='Appairage requis avant le premier lancement.';
  setSettingsOpen(true);return;
 }
 const repository=document.getElementById('repository').value.trim();
 const task=document.getElementById('instruction').value.trim();
 if(!repository||!task){status.textContent='Sélectionne un repo et écris une instruction.';return}
 button.disabled=true;button.textContent='Lancement…';status.textContent='Création du workflow…';
 try{
  const created=await api('/v1/workflows',{
   method:'POST',
   body:JSON.stringify({
    name:'Dashboard: '+repository,
    repository:repository,
    tasks:[{
     task_id:'implementation',
     title:task.slice(0,120),
     priority:100,
     max_attempts:2,
     estimated_minutes:30,
     payload:{handoff:{
      repository:repository,
      task:task,
      final_goal:task,
      agent_preference:'codex',
      token_budget:30000
     }}
    }]
   })
  });
  const id=created.workflow.id;
  const dispatched=await api('/v1/workflows/'+encodeURIComponent(id)+'/dispatch',{
   method:'POST',body:JSON.stringify({limit:1})
  });
  if((dispatched.jobs||[]).length){
   status.textContent='Production lancée · '+String(id).slice(0,12);
  }else{
   status.textContent='Production créée · en attente du worker · '+String(id).slice(0,12);
  }
  await loadRecentRuns();
 }catch(e){
  status.textContent=String(e).replace(/^Error:\s*/,'');
 }finally{
  button.disabled=false;button.textContent='Lancer la production';
 }
}

async function refreshDashboard(){
 if(refreshBusy) return;
 refreshBusy=true;
 try{
  await checkServer();
  await Promise.all([loadWorkerStatus(),loadRecentRuns(),loadVisualQuality()]);
 }finally{refreshBusy=false}
}

loadRepositories().then(function(){return refreshDashboard()});
document.getElementById('repository').addEventListener('change',function(){loadVisualQuality();loadRecentRuns()});
setInterval(loadVisualQuality,10000);
setInterval(function(){loadWorkerStatus();loadRecentRuns()},10000);
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
                control.workers.detect_dead()
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
