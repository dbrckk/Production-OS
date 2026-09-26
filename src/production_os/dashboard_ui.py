from __future__ import annotations

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
.launch-card{border-color:rgba(110,168,254,.42);box-shadow:0 22px 60px rgba(79,141,253,.16)}
.launch-card h2{font-size:1.08rem}
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
.danger-btn{border:1px solid rgba(248,113,113,.5);background:rgba(127,29,29,.25);color:#fecaca;border-radius:12px;padding:10px 13px;font-weight:800;cursor:pointer}
.danger-btn:disabled{opacity:.55;cursor:not-allowed}
.status-message{margin:11px 0 0;min-height:20px;font-size:.88rem;font-weight:700;color:#cbd5e1}
.worker-detail{margin:7px 0 0;color:var(--muted);font-size:.8rem}
.runtime-warning{display:none;margin-top:10px;padding:10px 12px;border-radius:12px;background:rgba(251,191,36,.10);border:1px solid rgba(251,191,36,.25);color:#fde68a;font-size:.82rem}
.runtime-warning.show{display:block}
.launch-readiness{margin:8px 0 0;padding:9px 11px;border-radius:12px;background:#0c1422;border:1px solid var(--line);font-size:.8rem;color:var(--muted)}
.launch-readiness.ready{border-color:rgba(52,211,153,.35);color:#a7f3d0}
.launch-readiness.queued{border-color:rgba(251,191,36,.35);color:#fde68a}
.launch-tracker{margin-top:12px;padding:12px;border:1px solid var(--line);border-radius:14px;background:rgba(12,20,34,.82)}
.launch-tracker[hidden]{display:none}
.launch-tracker .outcome-summary{margin-top:7px}
.live-runtime{margin-top:9px;padding-top:9px;border-top:1px solid var(--line)}
.live-progress{height:8px;border-radius:999px;background:#1e293b;overflow:hidden;margin-top:8px}
.live-progress-fill{height:100%;background:linear-gradient(90deg,#4f8dfd,#34d399);border-radius:999px}
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
.advanced-options{margin:12px 0;padding:10px 12px;border:1px solid var(--line);border-radius:13px;background:#0c1422}
.advanced-options summary{cursor:pointer;font-size:.82rem;font-weight:800;color:#cbd5e1}
.advanced-options[open] summary{margin-bottom:10px}
.attention-summary{position:sticky;top:8px;z-index:2}
.attention-card .secondary-btn{margin-top:10px}
.attention-required{border-left:3px solid rgba(251,191,36,.8)}
.attention-done{opacity:.78}
.attention-actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.attention-focus{outline:2px solid rgba(110,168,254,.7);box-shadow:0 0 0 4px rgba(110,168,254,.12)}
.attention-inline-instruction{display:grid;gap:8px;width:100%;margin-top:8px}
.attention-inline-instruction textarea{min-height:62px}
.outcome-summary{margin-top:8px;padding-top:8px;border-top:1px solid var(--line)}
.outcome-evidence{margin-top:6px}
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

body{overflow-x:hidden}
.v3-nav{display:grid;grid-template-columns:repeat(6,1fr);gap:6px;position:sticky;top:0;z-index:20;padding:8px;background:rgba(8,13,24,.94);backdrop-filter:blur(12px)}
.v3-nav button{border:1px solid var(--line);background:var(--panel);color:var(--text);padding:10px 6px;border-radius:12px;font-weight:700}
.v3-workspace{margin:12px 0}.v3-view{display:none}.v3-view.active{display:block}.v3-tabs{display:flex;gap:6px;overflow-x:auto;padding:6px 0}.v3-tabs button{white-space:nowrap}
@media(max-width:640px){.shell{padding-left:10px;padding-right:10px}.v3-nav{font-size:12px}}
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

 <div id="one-tap-production" class="card launch-card">
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
  <div id="launch-readiness" class="launch-readiness">Disponibilité : vérification...</div>
  <p id="worker-status" class="worker-detail">Capacités worker : vérification...</p>
  <div id="runtime-warning" class="runtime-warning">Worker hors ligne : la production peut être créée, mais elle restera en attente jusqu'à la reconnexion du moteur d'exécution.</div>
  <div id="last-production-card" class="launch-tracker" hidden></div>
 </div>


<nav class="v3-nav" aria-label="Navigation principale">
<button data-view="attention" onclick="navigate({view:'attention',workerId:null,repository:null,tab:null})">À faire</button>
<button data-view="overview" onclick="navigate({view:'overview',workerId:null,repository:null,tab:null})">Vue générale</button>
<button data-view="projects" onclick="navigate({view:'projects',workerId:null,repository:null,tab:null})">Projets</button>
<button data-view="workers" onclick="navigate({view:'workers',workerId:null,repository:null,tab:null})">Workers</button>
<button data-view="autopilot" onclick="navigate({view:'autopilot',workerId:null,repository:null,tab:null})">Autopilot</button>
<button data-view="managed" onclick="navigate({view:'managed',workerId:null,repository:null,tab:null})">Managed</button>
<button data-view="activity" onclick="navigate({view:'activity',workerId:null,repository:null,tab:null})">Activité</button>
</nav>
<section class="v3-workspace" aria-live="polite">
<div id="view-attention" class="v3-view active"><div class="section-head"><h2>À faire maintenant</h2><span id="attention-count" class="badge">0</span></div><div id="attention-list"></div></div>
<div id="view-overview" class="v3-view"><div class="section-head"><h2>Vue générale</h2><div class="v3-tabs" aria-label="Période"><button type="button" onclick="setDashboardWindow('24h')">24h</button><button type="button" onclick="setDashboardWindow('7d')">7d</button><button type="button" onclick="setDashboardWindow('30d')">30d</button></div></div><div id="overview-metrics"></div></div>
<div id="view-projects" class="v3-view"><h2>Projets</h2><div id="projects-list"></div><div class="v3-tabs" aria-label="Détail projet"><button>Aperçu</button><button>Avancement</button><button>Commits</button><button>API</button><button>Workflows</button><button>Qualité</button><button>Historique</button></div><div id="project-detail"></div></div>
<div id="view-workers" class="v3-view"><h2>Workers</h2><div id="workers-list"></div><div class="v3-tabs" aria-label="Détail worker"><button>Aperçu</button><button>Tâches</button><button>Logs</button><button>API</button><button>Historique</button><button data-worker-tab="control">Control</button></div><div id="worker-detail"></div></div>
<div id="view-autopilot" class="v3-view"><div class="section-head"><h2>Autopilot</h2><span id="autopilot-count" class="badge">0</span></div><div id="autopilot-list"></div></div>
<div id="view-managed" class="v3-view"><div class="section-head"><h2>Projets managés</h2><span id="managed-count" class="badge">0</span></div><div class="card"><h3>Nouveau projet managé</h3><label for="managed-create-repository">Repository</label><select id="managed-create-repository"><option value="">Chargement...</option></select><label for="managed-create-goal">Objectif final</label><textarea id="managed-create-goal" rows="4" placeholder="Décris le résultat final à atteindre et valider."></textarea><details class="advanced-options"><summary>Options avancées</summary><label for="managed-create-budget">Budget tokens</label><input id="managed-create-budget" type="number" min="1" step="1000" value="30000"><label for="managed-create-agent">Agent préféré</label><select id="managed-create-agent"><option value="auto">Auto</option><option value="codex">Codex</option></select></details><button class="primary-btn" type="button" onclick="createManagedProject()">Créer et lancer</button><div id="managed-create-status" class="status-message"></div></div><div id="managed-list"></div></div>
<div id="view-activity" class="v3-view"><h2>Activité</h2><div id="activity-list"></div></div>
</section>
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
const LAST_PROJECT_KEY='production_os_last_project_id';
const PENDING_LAUNCH_KEY='production_os_pending_launch';
let workerOnline=false;
let refreshBusy=false;
let launchReadiness=null;

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
  await loadRepositories();
  await refreshDashboard();
 }catch(e){
  if(previous) localStorage.setItem(TOKEN_KEY,previous); else localStorage.removeItem(TOKEN_KEY);
  setState('pair-state','bad','Token refusé');
  feedback.textContent=String(e).replace(/^Error:\\s*/,'');
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
 if(!token()) return;
 try{
  const data=await api('/v1/dashboard/repositories');
  const repos=data.repositories||[];
  const selects=[
   document.getElementById('repository'),
   document.getElementById('managed-create-repository')
  ].filter(Boolean);
  selects.forEach(function(select){
   const selected=select.value;
   select.innerHTML='';
   repos.forEach(function(x){
    const option=document.createElement('option');
    option.value=x.full_name;
    option.textContent=x.full_name+(x.private?' · privé':'');
    if(x.full_name===selected||(!selected&&x.full_name==='dbrckk/Jumpy')) option.selected=true;
    select.appendChild(option);
   });
   if(!repos.length){
    const option=document.createElement('option');
    option.value='dbrckk/Jumpy';
    option.textContent='dbrckk/Jumpy';
    select.appendChild(option);
   }
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
  const message=String(e).replace(/^Error:\\s*/,'');
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
  listEl.innerHTML='<div class="empty">Productions indisponibles · '+esc(String(e).replace(/^Error:\\s*/,''))+'</div>';
 }
}

function githubAssetUrls(repository,path){
 const repo=String(repository||'').trim();
 const value=String(path||'').replace(/^\\/+/, '');
 if(!/^[A-Za-z0-9_.-]+\\/[A-Za-z0-9_.-]+$/.test(repo)||!value||value.includes('..')) return null;
 const encoded=value.split('/').map(encodeURIComponent).join('/');
 return {view:'https://github.com/'+repo+'/blob/main/'+encoded,raw:'https://raw.githubusercontent.com/'+repo+'/main/'+encoded};
}
function isPreviewableAsset(path){return /\\.(png|webp|jpe?g|gif|svg)$/i.test(String(path||''))}
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

async function loadLaunchReadiness(){
 const el=document.getElementById('launch-readiness');
 const repository=document.getElementById('repository').value.trim();
 if(!token()||!repository){
  launchReadiness=null;
  el.className='launch-readiness';
  el.textContent='Disponibilité : appairage requis.';
  return null;
 }
 try{
  const data=await api(
   '/v1/dashboard/launch-readiness?repository='+encodeURIComponent(repository)
  );
  launchReadiness=data;
  const immediate=data.execution==='immediate';
  el.className='launch-readiness '+(immediate?'ready':'queued');
  el.textContent=immediate
   ?'Prêt · '+String(data.available_workers||0)+' worker(s) disponible(s) · '+String(data.queued_jobs||0)+' job(s) en file.'
   :'Mise en file sûre · aucun worker disponible immédiatement · '+String(data.queued_jobs||0)+' job(s) déjà en attente.';
  return data;
 }catch(e){
  launchReadiness=null;
  el.className='launch-readiness';
  el.textContent='Disponibilité : '+String(e).replace(/^Error:\\s*/,'');
  return null;
 }
}
function rememberLastProject(projectId){
 const value=String(projectId||'').trim();
 if(value)localStorage.setItem(LAST_PROJECT_KEY,value);
}
async function openLastProduction(projectId){
 navigate({
  view:'managed',
  workerId:null,
  repository:null,
  tab:null,
  focus:String(projectId||'')||null
 });
}
async function cancelLastProduction(projectId){
 const value=String(projectId||'').trim();
 if(!value)return;
 if(!window.confirm(
  "Annuler cette production active ? Le projet restera disponible pour inspection ou relance."
 ))return;
 try{
  const result=await api(
   "/v1/managed-projects/"+encodeURIComponent(value)+"/cancel",
   {
    method:"POST",
    body:JSON.stringify({confirm:"CANCEL_ACTIVE_PRODUCTION"})
   }
  );
  const state=String(result.status||"");
  const status=document.getElementById("launch-status");
  if(status){
   status.textContent=state==="cancel_requested"
    ?"Annulation demandée · arrêt coopératif du worker en cours."
    :"Production annulée.";
  }
  await Promise.all([
   loadLastProduction(),
   loadManagedProjects(),
   loadAttention()
  ]);
 }catch(e){
  const status=document.getElementById("launch-status");
  if(status)status.textContent=String(e).replace(/^Error:\s*/,"");
 }
}
async function loadLastProduction(){
 const el=document.getElementById('last-production-card');
 const projectId=String(localStorage.getItem(LAST_PROJECT_KEY)||'').trim();
 if(!token()||!projectId){
  el.hidden=true;
  el.innerHTML='';
  return null;
 }
 try{
  const data=await api(
   '/v1/dashboard/production-status?project_id='+encodeURIComponent(projectId)
  );
  const project=data.project||{};
  const runtime=data.runtime||{};
  const outcome=project.outcome||{};
  const generation=Number(project.generation||1);
  const phase=String(runtime.phase||'preparing');
  const labels={
   preparing:'Préparation',
   queued:'En file',
   claimed:'Réclamé',
   running:'En cours',
   cancelling:'Annulation',
   review_required:'À revoir',
   needs_attention:'Action requise',
   done:'Terminé'
  };
  const label=labels[phase]||phase;
  const details=[];
  if(runtime.worker_id)details.push('worker '+String(runtime.worker_id));
  if(runtime.attempt!=null)details.push('tentative '+String(runtime.attempt));
  if(runtime.stage)details.push('stage '+String(runtime.stage));
  if(runtime.queue_position!=null)details.push('position '+String(runtime.queue_position));
  if(runtime.last_telemetry_at)details.push('télémétrie '+String(runtime.last_telemetry_at));
  const rawProgress=Number(runtime.progress_percent);
  const hasProgress=Number.isFinite(rawProgress);
  const progress=hasProgress?Math.max(0,Math.min(100,rawProgress)):null;
  const progressHtml=hasProgress
   ?'<div class="live-progress" aria-label="Progression '+esc(String(progress))+' %"><div class="live-progress-fill" style="width:'+esc(String(progress))+'%"></div></div>'
   :'';
  el.hidden=false;
  el.innerHTML=
   '<div class="section-head"><strong>Dernière production</strong><span class="badge">'+esc(label)+'</span></div>'+
   '<div class="small"><strong>'+esc(String(project.repository||''))+'</strong> · génération '+formatNumber(generation)+'</div>'+
   '<div class="small">'+esc(String(project.final_goal||''))+'</div>'+
   '<div class="live-runtime"><div class="small"><strong>Exécution :</strong> '+esc(String(runtime.message||label))+'</div>'+
   (details.length?'<div class="small">'+esc(details.join(' · '))+'</div>':'')+
   progressHtml+'</div>'+
   renderProductionOutcome(outcome,true)+
   '<div class="attention-actions">'+
   '<button class="secondary-btn" type="button" data-project-id="'+esc(projectId)+'" onclick="openLastProduction(this.dataset.projectId)">Ouvrir le projet</button>'+
   (["preparing","queued","claimed","running"].includes(phase)
    ?'<button class="danger-btn" type="button" data-project-id="'+esc(projectId)+'" onclick="cancelLastProduction(this.dataset.projectId)">Annuler la production</button>'
    :phase==="cancelling"
      ?'<button class="danger-btn" type="button" disabled>Annulation en cours</button>'
      :'')+
   '</div>';
  return data;
 }catch(e){
  el.hidden=false;
  el.innerHTML='<div class="small">Dernière production indisponible · '+esc(String(e).replace(/^Error:\\s*/,''))+'</div>';
  return null;
 }
}

function launchDraftFingerprint(repository,task){
 const text=String(repository||'')+'\u0000'+String(task||'');
 let hash=2166136261;
 for(let index=0;index<text.length;index++){
  hash^=text.charCodeAt(index);
  hash=Math.imul(hash,16777619);
 }
 return (hash>>>0).toString(16).padStart(8,'0')+':'+String(text.length);
}
function newLaunchRequestId(){
 if(window.crypto&&typeof window.crypto.randomUUID==='function'){
  return window.crypto.randomUUID();
 }
 return 'launch-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,14);
}
function pendingLaunchRequest(repository,task){
 const fingerprint=launchDraftFingerprint(repository,task);
 try{
  const raw=localStorage.getItem(PENDING_LAUNCH_KEY);
  const previous=raw?JSON.parse(raw):null;
  if(
   previous
   &&previous.repository===repository
   &&previous.fingerprint===fingerprint
   &&typeof previous.request_id==='string'
   &&previous.request_id
  ){
   return previous.request_id;
  }
 }catch(_e){}
 const requestId=newLaunchRequestId();
 localStorage.setItem(PENDING_LAUNCH_KEY,JSON.stringify({
  repository:repository,
  fingerprint:fingerprint,
  request_id:requestId
 }));
 return requestId;
}
function clearPendingLaunchRequest(requestId){
 try{
  const raw=localStorage.getItem(PENDING_LAUNCH_KEY);
  const previous=raw?JSON.parse(raw):null;
  if(previous&&previous.request_id===requestId){
   localStorage.removeItem(PENDING_LAUNCH_KEY);
  }
 }catch(_e){
  localStorage.removeItem(PENDING_LAUNCH_KEY);
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
 const requestId=pendingLaunchRequest(repository,task);
 button.disabled=true;button.textContent='Lancement…';status.textContent='Création du workflow…';
 try{
  const created=await api('/v1/dashboard/launch',{
   method:'POST',
   body:JSON.stringify({
    repository:repository,
    instruction:task,
    request_id:requestId
   })
  });
  const project=created.project||{};
  const workflowId=String(project.current_workflow_id||'');
  const projectId=String(project.project_id||'');
  rememberLastProject(projectId);
  clearPendingLaunchRequest(requestId);
  const immediate=launchReadiness&&launchReadiness.execution==='immediate';
  status.textContent=immediate
   ?'Production lancée et persistante · exécution disponible · '+projectId.slice(0,12)
   :'Production persistante créée · en attente du worker · mise en file sûre · '+projectId.slice(0,12);
  document.getElementById('instruction').value='';
  await Promise.all([
   loadRecentRuns(),
   loadManagedProjects(),
   loadAttention(),
   loadLastProduction(),
   loadLaunchReadiness()
  ]);
  if(workflowId) appState.repository=repository;
 }catch(e){
  status.textContent=String(e).replace(/^Error:\\s*/,'');
 }finally{
  button.disabled=false;button.textContent='Lancer la production';
 }
}

async function refreshDashboard(){
 if(refreshBusy) return;
 refreshBusy=true;
 try{
  await checkServer();
  await Promise.all([
   loadWorkerStatus(),
   loadRecentRuns(),
   loadVisualQuality(),
   loadLaunchReadiness(),
   loadLastProduction()
  ]);
 }finally{refreshBusy=false}
}

loadRepositories().then(function(){return refreshDashboard()});
document.getElementById('repository').addEventListener('change',loadVisualQuality);
document.getElementById('repository').addEventListener('change',loadRecentRuns);
document.getElementById('repository').addEventListener('change',loadLaunchReadiness);
setInterval(loadVisualQuality,10000);
setInterval(function(){
 loadWorkerStatus();
 loadRecentRuns();
 loadLaunchReadiness();
},10000);
setInterval(loadLastProduction,5000);

const appState={view:"attention",workerId:null,repository:null,tab:null,focus:null,window:"7d",polling:new Map()};
(function restoreNavigation(){
 const q=new URLSearchParams(window.location.search);
 const view=q.get("view");
 if(["attention","overview","projects","workers","autopilot","managed","activity"].includes(view))appState.view=view;
 appState.workerId=q.get("worker")||null;
 appState.repository=q.get("repo")||null;
 appState.tab=q.get("tab")||null;
 appState.focus=q.get("target")||null;
})();

function clearViewPolls(){
 appState.polling.forEach(function(id){clearInterval(id)});
 appState.polling.clear();
}
function setDashboardWindow(windowName){
 if(!["24h","7d","30d"].includes(windowName))return;
 appState.window=windowName;
 renderActiveView();
}
function formatNumber(value){
 if(value===null||value===undefined)return "—";
 return new Intl.NumberFormat("fr-FR",{maximumFractionDigits:2}).format(value);
}
function formatBytes(value){
 if(value===null||value===undefined)return "Indisponible";
 const bytes=Number(value);
 if(!Number.isFinite(bytes)||bytes<0)return "Indisponible";
 const units=["o","Ko","Mo","Go","To"];
 let amount=bytes,index=0;
 while(amount>=1024&&index<units.length-1){amount/=1024;index++}
 return new Intl.NumberFormat("fr-FR",{maximumFractionDigits:2}).format(amount)+" "+units[index];
}
function errorCard(error){
 return '<div class="card"><div class="small">'+esc(String(error).replace(/^Error:\\s*/,''))+'</div></div>';
}
function repoApiPath(repository){
 return String(repository).split("/").map(encodeURIComponent).join("/");
}
function incidentPlaybookActionLabel(action){
 const labels={
  "kick":"Réveiller le worker GitHub Actions",
  "inspect-worker":"Inspecter le worker",
  "recover-stuck":"Récupérer le job expiré",
  "inspect-job":"Inspecter le job",
  "cancel-current":"Annuler le job actif"
 };
 return labels[action]||String(action||"Action");
}
async function runIncidentPlaybookAction(action,workerId,jobKey,incidentId){
 if(action==="inspect-worker"){
  if(workerId)openWorker(encodeURIComponent(workerId));
  return;
 }
 if(action==="inspect-job"){
  if(workerId)openWorker(encodeURIComponent(workerId));
  return;
 }
 if(!workerId)throw new Error("Worker requis pour cette remédiation.");
 await runWorkerControl(workerId,action,jobKey||null,incidentId||null);
 await loadOverview();
}
function renderIncidentPlaybook(item){
 const playbook=item&&item.playbook||{};
 const suggestions=playbook.suggestions||[];
 if(!suggestions.length)return '<div class="small">Aucune remédiation proposée.</div>';
 return '<div class="small"><strong>Playbook :</strong></div>'+
  suggestions.map(function(suggestion){
   const action=String(suggestion.action||"");
   const availability=String(suggestion.availability||"unavailable");
   const available=availability==="available"||availability==="fallback";
   const workerId=suggestion.worker_id==null?"":String(suggestion.worker_id);
   const jobKey=suggestion.job_key==null?"":String(suggestion.job_key);
   const badge=availability==="fallback"?"fallback":availability;
   const button=available
    ?'<button class="secondary-btn" type="button" data-playbook-action="'+esc(action)+'" data-worker-id="'+esc(workerId)+'" data-job-key="'+esc(jobKey)+'" data-incident-id="'+esc(String(item.id||""))+'" onclick="runIncidentPlaybookAction(this.dataset.playbookAction,this.dataset.workerId,this.dataset.jobKey,this.dataset.incidentId)">'+esc(incidentPlaybookActionLabel(action))+'</button>'
    :'<button class="secondary-btn" type="button" disabled>'+esc(incidentPlaybookActionLabel(action))+'</button>';
   return '<div class="small" style="margin-top:8px">'+button+
    ' <span class="badge">'+esc(badge)+'</span><br>'+
    esc(String(suggestion.reason||""))+'</div>';
  }).join("");
}
async function pruneExpiredHistory(expected){
 const count=Number(expected);
 if(!Number.isInteger(count)||count<=0)return;
 if(!window.confirm(
  "Supprimer définitivement "+count+
  " ligne(s) historiques expirée(s) ? Les données protégées seront conservées."
 ))return;
 try{
  const result=await api(
   "/v1/dashboard/maintenance/prune",
   {
    method:"POST",
    body:JSON.stringify({
     confirm:"PRUNE_EXPIRED_HISTORY",
     expected_candidate_rows:count
    })
   }
  );
  await loadOverview();
  const receipt=document.getElementById("maintenance-prune-status");
  if(receipt){
   receipt.textContent="Nettoyage terminé · "+formatNumber(result.deleted_rows)+" ligne(s) supprimée(s).";
  }
 }catch(e){
  await loadOverview();
  const receipt=document.getElementById("maintenance-prune-status");
  if(receipt)receipt.textContent=String(e).replace(/^Error:\\s*/,"");
 }
}
async function pruneExpiredBackups(expected,fingerprint){
 const count=Number(expected);
 const hash=String(fingerprint||"").trim().toLowerCase();
 if(!Number.isInteger(count)||count<=0||!/^[0-9a-f]{64}$/.test(hash))return;
 if(!window.confirm(
  "Supprimer définitivement "+count+
  " ancienne(s) sauvegarde(s) vérifiée(s) ? Les 3 plus récentes et celles liées à une restauration resteront protégées."
 ))return;
 try{
  const result=await api(
   "/v1/dashboard/backups/prune-expired",
   {
    method:"POST",
    body:JSON.stringify({
     confirm:"PRUNE_EXPIRED_VERIFIED_BACKUPS",
     expected_candidate_count:count,
     expected_candidate_fingerprint:hash
    })
   }
  );
  await loadOverview();
  const receipt=document.getElementById("backup-status-message");
  if(receipt){
   receipt.textContent=
    "Anciens backups nettoyés · "+formatNumber(result.deleted_count)+
    " sauvegarde(s) · "+formatBytes(result.deleted_bytes);
  }
 }catch(e){
  await loadOverview();
  const receipt=document.getElementById("backup-status-message");
  if(receipt)receipt.textContent=String(e).replace(/^Error:\\s*/,"");
 }
}
async function pruneStaleBackupTemps(expected){
 const count=Number(expected);
 if(!Number.isInteger(count)||count<=0)return;
 if(!window.confirm(
  "Supprimer "+count+
  " fichier(s) temporaire(s) de backup datant d’au moins 24 h ?"
 ))return;
 try{
  const result=await api(
   "/v1/dashboard/backups/prune-temp",
   {
    method:"POST",
    body:JSON.stringify({
     confirm:"PRUNE_STALE_BACKUP_TEMPS",
     expected_candidate_count:count
    })
   }
  );
  await loadOverview();
  const receipt=document.getElementById("backup-status-message");
  if(receipt){
   receipt.textContent=
    "Temporaires nettoyés · "+formatNumber(result.deleted_count)+
    " fichier(s) · "+formatBytes(result.deleted_bytes);
  }
 }catch(e){
  await loadOverview();
  const receipt=document.getElementById("backup-status-message");
  if(receipt)receipt.textContent=String(e).replace(/^Error:\\s*/,"");
 }
}
async function createVerifiedBackup(){
 if(!window.confirm(
  "Créer une sauvegarde SQLite vérifiée côté serveur ? La restauration reste désactivée."
 ))return;
 try{
  const result=await api(
   "/v1/dashboard/backups/create",
   {
    method:"POST",
    body:JSON.stringify({confirm:"CREATE_VERIFIED_BACKUP"})
   }
  );
  await loadOverview();
  const receipt=document.getElementById("backup-status-message");
  if(receipt){
   receipt.textContent="Sauvegarde vérifiée créée · "+esc(String(result.backup_id||""))+" · "+formatBytes(result.size_bytes);
  }
 }catch(e){
  await loadOverview();
  const receipt=document.getElementById("backup-status-message");
  if(receipt)receipt.textContent=String(e).replace(/^Error:\\s*/,"");
 }
}
async function verifyBackupReadiness(backupId){
 if(!backupId)return;
 if(!window.confirm(
  "Vérifier que cette sauvegarde est restaurable ? Aucune restauration ne sera exécutée."
 ))return;
 try{
  const result=await api(
   "/v1/dashboard/backups/"+encodeURIComponent(backupId)+"/verify",
   {
    method:"POST",
    body:JSON.stringify({confirm:"VERIFY_BACKUP_FOR_RESTORE"})
   }
  );
  const receipt=document.getElementById("backup-status-message");
  if(receipt){
   receipt.textContent=
    "Restaurabilité vérifiée · schéma "+String(result.schema_version||"—")+
    " · intégrité "+String(result.integrity||"—")+
    " · restauration toujours désactivée";
  }
 }catch(e){
  const receipt=document.getElementById("backup-status-message");
  if(receipt)receipt.textContent=String(e).replace(/^Error:\\s*/,"");
 }
}
async function stageBackupRestore(backupId){
 if(!backupId)return;
 if(!window.confirm(
  "Préparer une restauration isolée à partir de cette sauvegarde ? La base active ne sera pas modifiée et l’activation restera désactivée."
 ))return;
 try{
  const result=await api(
   "/v1/dashboard/backups/"+encodeURIComponent(backupId)+"/stage-restore",
   {
    method:"POST",
    body:JSON.stringify({confirm:"STAGE_VERIFIED_RESTORE"})
   }
  );
  const receipt=document.getElementById("backup-status-message");
  if(receipt){
   receipt.textContent=
    "Restauration préparée · candidat "+String(result.candidate_id||"—")+
    " · schéma "+String(result.schema_version||"—")+
    " · intégrité "+String(result.integrity||"—")+
    " · activation désactivée";
  }
 }catch(e){
  const receipt=document.getElementById("backup-status-message");
  if(receipt)receipt.textContent=String(e).replace(/^Error:\\s*/,"");
 }
}
async function loadOverview(){
 const el=document.getElementById("overview-metrics");
 try{
  const results=await Promise.all([
   api("/v1/dashboard/overview?window="+encodeURIComponent(appState.window)),
   api("/v1/dashboard/health"),
   api("/v1/dashboard/incidents?limit=20"),
   api("/v1/dashboard/maintenance").catch(function(){
    return {status:"unknown",database_size_bytes:null,total_rows:null,candidate_rows:null,tables:[],errors:[{error:"unavailable"}]};
   }),
   api("/v1/dashboard/backups").catch(function(){
    return {status:"unknown",backend_kind:"unknown",create_supported:false,restore_enabled:false,backups:[]};
   })
  ]);
  const data=results[0],health=results[1]||{},incidentData=results[2]||{},maintenance=results[3]||{},backups=results[4]||{};
  const w=data.workers||{},p=data.productions||{},u=data.usage||{},c=data.commits||{},perf=data.performance||{},alerts=data.alerts||[];
  const healthReasons=health.reasons||[];
  const incidents=incidentData.incidents||[];
  const incidentsHtml=
   '<div class="card"><div class="section-head"><h2>Incidents</h2><span class="badge">'+formatNumber(incidents.length)+'</span></div>'+
   (incidents.length?incidents.map(function(item){
    const ack=item.status==="open"
     ?'<button class="secondary-btn" type="button" data-incident-id="'+esc(String(item.id||""))+'" onclick="acknowledgeIncident(this.dataset.incidentId)">Acquitter</button>'
     :'';
    return '<div class="small"><strong>'+esc(String(item.title||item.code||"Incident"))+'</strong> · '+esc(String(item.status||""))+' · '+esc(String(item.severity||""))+' · '+esc(String(item.target_type||""))+':'+esc(String(item.target_id||""))+' '+ack+
     '<div style="margin:8px 0 14px">'+renderIncidentPlaybook(item)+'</div></div>';
   }).join(""):'<div class="small">Aucun incident durable.</div>')+
   '</div>';
  const healthHtml=
   '<div class="card"><div class="section-head"><h2>Santé opérationnelle</h2><span class="badge">'+esc(String(health.status||"inconnu"))+'</span></div>'+
   (healthReasons.length?healthReasons.map(function(item){
    return '<div class="small"><strong>'+esc(String(item.code||"diagnostic"))+'</strong> · '+esc(String(item.severity||""))+'</div>';
   }).join(""):'<div class="small">Aucune dégradation opérationnelle détectée.</div>')+
   '</div>';
  const alertsHtml=alerts.length?
   '<div class="card"><div class="section-head"><h2>Alertes opérationnelles</h2><span class="badge">'+formatNumber(alerts.length)+'</span></div>'+
   alerts.map(function(item){
    return '<div class="small"><strong>'+esc(String(item.title||item.code||"Alerte"))+'</strong> · '+esc(String(item.severity||""))+'<br>'+esc(String(item.message||""))+'</div>';
   }).join('')+'</div>':'';
  const maintenanceTables=maintenance.tables||[];
  const prunable=Number(maintenance.prunable_candidate_rows||0);
  const protectedRows=Number(maintenance.protected_candidate_rows||0);
  const pruneButton=prunable>0
   ?'<button class="secondary-btn" type="button" data-prunable="'+esc(String(prunable))+'" onclick="pruneExpiredHistory(Number(this.dataset.prunable))">Nettoyer l’historique expiré</button>'
   :'';
  const maintenanceHtml=
   '<div class="card"><div class="section-head"><h2>Stockage & rétention</h2><span class="badge">'+esc(String(maintenance.status||"unknown"))+'</span></div>'+
   '<p class="small"><strong>Backend :</strong> '+esc(String(maintenance.backend_kind||"inconnu"))+' · <strong>Taille :</strong> '+esc(formatBytes(maintenance.database_size_bytes))+' · <strong>Lignes suivies :</strong> '+formatNumber(maintenance.total_rows)+'</p>'+
   '<p class="small"><strong>Prunables :</strong> '+formatNumber(prunable)+' · <strong>Protégées :</strong> '+formatNumber(protectedRows)+'</p>'+
   (maintenanceTables.length?maintenanceTables.map(function(row){
    const invalid=Number(row.invalid_timestamps||0);
    return '<div class="small"><strong>'+esc(String(row.name||row.table||"table"))+'</strong> · '+formatNumber(row.rows)+' lignes · rétention '+formatNumber(row.retention_days)+' j · prunables '+formatNumber(row.prunable_candidate_rows)+' · protégées '+formatNumber(row.protected_candidate_rows)+(invalid?' · timestamps invalides '+formatNumber(invalid):'')+'</div>';
   }).join(""):'<div class="small">Diagnostic de stockage indisponible.</div>')+
   '<div style="margin-top:10px">'+pruneButton+'</div>'+
   '<div id="maintenance-prune-status" class="status-message"></div>'+
   '</div>';
  const backupRows=backups.backups||[];
  const activationRows=backups.activations||[];
  const backupStorage=backups.storage||{};
  const backupFilesystem=backupStorage.filesystem||{};
  const backupAge=backupStorage.backup_age||{};
  const backupAgeBuckets=backupAge.buckets||{};
  const backupRetention=backupStorage.retention_preview||{};
  const backupRetentionReasons=backupRetention.protected_reasons||{};
  const lastBackup=backupRows.length?backupRows[0]:null;
  const backupButton=backups.create_supported===true
   ?'<button class="secondary-btn" type="button" onclick="createVerifiedBackup()">Créer une sauvegarde vérifiée</button>'
   :'';
  const staleTempCount=Number(backupStorage.stale_temp_count||0);
  const backupTempPruneButton=staleTempCount>0
   ?'<button class="secondary-btn" type="button" data-stale-temp-count="'+esc(String(staleTempCount))+'" onclick="pruneStaleBackupTemps(Number(this.dataset.staleTempCount))">Nettoyer temporaires anciens</button>'
   :'';
  const retentionCandidateCount=Number(backupRetention.candidate_count||0);
  const retentionFingerprint=String(backupRetention.candidate_fingerprint||"");
  const backupRetentionPruneButton=retentionCandidateCount>0&&/^[0-9a-f]{64}$/.test(retentionFingerprint)
   ?'<button class="secondary-btn" type="button" data-retention-count="'+esc(String(retentionCandidateCount))+'" data-retention-fingerprint="'+esc(retentionFingerprint)+'" onclick="pruneExpiredBackups(Number(this.dataset.retentionCount),this.dataset.retentionFingerprint)">Nettoyer anciens backups</button>'
   :'';
  const backupCatalogHtml=backupRows.length?backupRows.slice(0,5).map(function(row){
   const id=String(row.backup_id||"");
   return '<div class="small"><strong>'+esc(String(row.created_at||id))+'</strong> · '+formatBytes(row.size_bytes)+
    ' <button class="secondary-btn" type="button" data-backup-id="'+esc(id)+'" onclick="verifyBackupReadiness(this.dataset.backupId)">Vérifier restaurabilité</button>'+
    ' <button class="secondary-btn" type="button" data-backup-id="'+esc(id)+'" onclick="stageBackupRestore(this.dataset.backupId)">Préparer restauration</button></div>';
  }).join(""):'<div class="small">Aucune sauvegarde vérifiée.</div>';
  const backupHtml=
   '<div class="card"><div class="section-head"><h2>Sauvegarde</h2><span class="badge">'+esc(String(backups.status||"unknown"))+'</span></div>'+
   '<p class="small"><strong>Backend :</strong> '+esc(String(backups.backend_kind||"inconnu"))+' · <strong>Restauration :</strong> '+(backups.restore_enabled?'activée':'désactivée')+'</p>'+
   '<p class="small"><strong>Dernière sauvegarde vérifiée :</strong> '+(lastBackup?esc(String(lastBackup.created_at||""))+' · '+formatBytes(lastBackup.size_bytes):'Aucune')+'</p>'+
   '<p class="small"><strong>Stockage backup :</strong> '+formatBytes(backupStorage.total_size_bytes)+' · backups '+formatNumber(backupStorage.backup_count)+' · candidats '+formatNumber(backupStorage.restore_candidate_count)+' · reçus '+formatNumber(backupStorage.activation_receipt_count)+'</p>'+
   '<p class="small"><strong>Filesystem :</strong> '+esc(String(backupFilesystem.status||"unknown"))+' · <strong>Disponible :</strong> '+formatBytes(backupFilesystem.available_bytes)+' · <strong>Utilisé :</strong> '+(backupFilesystem.used_percent==null?'Indisponible':formatNumber(backupFilesystem.used_percent)+' %')+'</p>'+
   '<p class="small"><strong>Âge backups vérifiés :</strong> &lt;24 h '+formatNumber(backupAgeBuckets.under_24h)+' · 1–7 j '+formatNumber(backupAgeBuckets.one_to_seven_days)+' · 7–30 j '+formatNumber(backupAgeBuckets.seven_to_thirty_days)+' · &gt;30 j '+formatNumber(backupAgeBuckets.over_thirty_days)+(Number(backupAge.invalid_timestamp_count||0)?' · timestamps invalides '+formatNumber(backupAge.invalid_timestamp_count):'')+'</p>'+
   '<p class="small"><strong>Prévisualisation rétention :</strong> candidats '+formatNumber(backupRetention.candidate_count)+' ('+formatBytes(backupRetention.candidate_bytes)+') · protégés '+formatNumber(backupRetention.protected_count)+' · seuil '+formatNumber(backupRetention.retention_days)+' j · minimum conservé '+formatNumber(backupRetention.min_keep_latest)+'</p>'+
   '<p class="small"><strong>Protections :</strong> récents '+formatNumber(backupRetentionReasons.recent)+' · derniers '+formatNumber(backupRetentionReasons.latest_floor)+' · historique restauration '+formatNumber(backupRetentionReasons.restore_history)+' · timestamps invalides '+formatNumber(backupRetentionReasons.invalid_timestamp)+'</p>'+
   '<p class="small"><strong>Temporaires :</strong> '+formatNumber(backupStorage.temp_file_count)+' · <strong>Anciens ≥24 h :</strong> '+formatNumber(staleTempCount)+' · <strong>Inconnus :</strong> '+formatNumber(backupStorage.unknown_file_count)+'</p>'+
   (backups.message?'<p class="small">'+esc(String(backups.message))+'</p>':'')+
   backupCatalogHtml+
   '<h3 style="font-size:.85rem;margin:15px 0 6px">Historique des activations</h3>'+
   (activationRows.length?activationRows.slice(0,5).map(function(row){
    return '<div class="small"><strong>'+esc(String(row.activated_at||""))+'</strong> · candidat '+esc(String(row.candidate_id||""))+' · rollback '+esc(String(row.rollback_backup_id||""))+'</div>';
   }).join(""):'<div class="small">Aucune activation de restauration enregistrée.</div>')+
   '<div style="margin-top:10px">'+backupButton+' '+backupTempPruneButton+' '+backupRetentionPruneButton+'</div>'+
   '<div id="backup-status-message" class="status-message"></div>'+
   '</div>';
  el.innerHTML=
   '<div class="status-grid">'+
   '<div class="status-card"><div class="status-label">Workers en ligne</div><div class="status-value">'+formatNumber(w.online)+' / '+formatNumber(w.total)+'</div></div>'+
   '<div class="status-card"><div class="status-label">Productions actives</div><div class="status-value">'+formatNumber(p.running)+'</div></div>'+
   '<div class="status-card"><div class="status-label">Tokens · '+esc(appState.window)+'</div><div class="status-value">'+formatNumber(u.tokens)+'</div></div>'+
   '</div>'+
   '<div class="card"><div class="section-head"><h2>Activité mesurée</h2></div>'+
   '<p class="small">API calls : '+formatNumber(u.api_calls)+' · coût estimé : '+formatNumber(u.estimated_cost_usd)+' USD</p>'+
   '<p class="small">Commits Production-OS : '+formatNumber(c.production_os)+' · branche par défaut GitHub : '+formatNumber(c.github_default_branch)+'</p>'+
   '<p class="small">Taux de réussite : '+formatNumber(perf.success_rate)+' % · temps d’exécution : '+formatNumber(perf.execution_seconds)+' s</p></div>'+
   healthHtml+
   maintenanceHtml+
   backupHtml+
   incidentsHtml+
   alertsHtml;
 }catch(e){el.innerHTML=errorCard(e)}
}
function autopilotWaitLabel(value){
 const labels={
  assigned_worker_unavailable:"Worker assigné indisponible",
  no_worker:"Aucun worker enregistré",
  missing_capability:"Capacité requise indisponible",
  worker_controlled:"Worker en pause ou drain",
  capacity_full:"Capacité worker saturée",
  no_online_worker:"Aucun worker en ligne"
 };
 return value?(labels[value]||String(value)):"Prêt à être pris";
}
async function loadAutopilot(){
 const el=document.getElementById("autopilot-list");
 const count=document.getElementById("autopilot-count");
 try{
  const data=await api("/v1/dashboard/autopilot?limit=50");
  const jobs=data.jobs||[],summary=data.summary||{};
  count.textContent=String(jobs.length);
  const summaryHtml=
   '<div class="status-grid">'+
   '<div class="status-card"><div class="status-label">Prêts maintenant</div><div class="status-value">'+formatNumber(summary.ready_now)+'</div></div>'+
   '<div class="status-card"><div class="status-label">Bloqués</div><div class="status-value">'+formatNumber(summary.blocked)+'</div></div>'+
   '<div class="status-card"><div class="status-label">Slots libres</div><div class="status-value">'+formatNumber(summary.free_slots)+'</div></div>'+
   '</div>'+
   '<div class="card"><p class="small"><strong>ETA connue :</strong> '+(summary.known_eta_minutes==null?'Indisponible':formatNumber(summary.known_eta_minutes)+' min')+
   ' · <strong>Couverture :</strong> '+formatNumber(summary.eta_coverage_jobs)+' / '+formatNumber(summary.eta_total_jobs)+' jobs</p></div>';
  if(!jobs.length){
   el.innerHTML=summaryHtml+'<div class="empty">Aucun job en attente.</div>';
   return;
  }
  el.innerHTML=summaryHtml+jobs.map(function(row){
   const ready=!row.wait_reason;
   const worker=row.preferred_worker||"—";
   const caps=(row.required_capabilities||[]).join(", ")||"Aucune";
   return '<div class="card'+(appState.focus===String(row.job_key||"")?' attention-focus':'')+'" data-job-key="'+esc(String(row.job_key||""))+'">'+
    '<div class="section-head"><h2>#'+esc(String(row.position))+' · '+esc(String(row.task||row.job_key))+'</h2>'+
    '<span class="badge">'+(ready?'Prêt':'En attente')+'</span></div>'+
    '<p class="small"><strong>Projet :</strong> '+esc(String(row.repository||""))+'</p>'+
    '<p class="small"><strong>Score :</strong> '+formatNumber(row.score)+' · <strong>ETA :</strong> '+formatNumber(row.predicted_minutes)+' min · <strong>Âge :</strong> '+formatNumber(row.age_minutes)+' min</p>'+
    '<p class="small"><strong>Chemin critique :</strong> '+(row.critical?'Oui':'Non')+' · <strong>Dépendants :</strong> '+formatNumber(row.descendants)+'</p>'+
    (row.ranking_status==="degraded"?'<p class="small"><strong>Ranking :</strong> Dégradé · workflow de référence indisponible</p>':'')+
    '<p class="small"><strong>Capacités requises :</strong> '+esc(caps)+'</p>'+
    '<p class="small"><strong>Worker préféré :</strong> '+esc(worker)+'</p>'+
    '<p class="small"><strong>État :</strong> '+esc(autopilotWaitLabel(row.wait_reason))+'</p>'+
    '</div>';
  }).join("");
  if(appState.focus){
   const focused=el.querySelector('[data-job-key="'+CSS.escape(String(appState.focus))+'"]');
   if(focused)setTimeout(function(){focused.scrollIntoView({block:"center"})},0);
  }
 }catch(e){
  count.textContent="—";
  el.innerHTML=errorCard(e);
 }
}
async function acknowledgeIncident(incidentId){
 try{
  await api(
   "/v1/dashboard/incidents/"+encodeURIComponent(incidentId)+"/acknowledge",
   {method:"POST",body:"{}"}
  );
  await loadOverview();
 }catch(e){
  document.getElementById("overview-metrics").insertAdjacentHTML(
   "afterbegin",
   errorCard(e)
  );
 }
}

function openProject(encoded){
 navigate({view:"projects",repository:decodeURIComponent(encoded),workerId:null,tab:"overview"});
}
async function loadProjectsView(){
 const list=document.getElementById("projects-list");
 try{
  const data=await api("/v1/dashboard/projects");
  const rows=data.projects||[];
  list.innerHTML=rows.length?rows.map(function(item){
   const repo=String(item.repository||"");
   return '<button class="secondary-btn" type="button" data-repo="'+esc(encodeURIComponent(repo))+'" onclick="openProject(this.dataset.repo)">'+esc(repo)+'</button>';
  }).join(" "):'<div class="empty">Aucun projet observé.</div>';
  if(appState.repository)await loadProjectDetail(appState.repository);
  else document.getElementById("project-detail").innerHTML='<div class="empty">Sélectionne un projet.</div>';
 }catch(e){list.innerHTML=errorCard(e)}
}
async function loadProjectDetail(repository){
 const el=document.getElementById("project-detail");
 try{
  const base="/v1/dashboard/projects/"+repoApiPath(repository);
  const results=await Promise.all([
   api(base),
   api(base+"/progress"),
   api(base+"/commits?window="+encodeURIComponent(appState.window)),
   api(base+"/usage?window="+encodeURIComponent(appState.window)),
   api(base+"/workflows"),
   api(base+"/history")
  ]);
  const detail=results[0],progress=results[1],commits=results[2],usage=results[3],workflows=results[4],history=results[5];
  const production=progress.production||{},estimate=progress.estimate||{},totals=usage.totals||{};
  const usageProviders=usage.providers||[],usageTimeline=usage.timeline||[];
  const evidence=progress.estimate&&progress.estimate.evidence;
  const remainingWork=progress.estimate&&progress.estimate.remaining_work;
  const blockers=progress.estimate&&progress.estimate.blockers;
  const components=estimate.components||{};
  function componentValue(name){
   const item=components[name]||{};
   return item.score==null?(item.status==="not_applicable"?"N/A":"Indisponible"):formatNumber(item.score)+" %";
  }
  function progressList(value){
   if(Array.isArray(value))return value.length?value.map(function(item){return esc(typeof item==="string"?item:JSON.stringify(item))}).join(" · "):"Aucun";
   if(value&&typeof value==="object")return esc(JSON.stringify(value));
   return value==null?"Indisponible":esc(String(value));
  }
  el.innerHTML=
   '<div class="card"><div class="section-head"><h2>'+esc(repository)+'</h2><span class="badge">'+esc(String((detail.snapshot||{}).ci_status||"CI inconnue"))+'</span></div>'+
   '<p class="small"><strong>Production actuelle :</strong> '+formatNumber(production.percent)+' %</p>'+
   '<p class="small"><strong>Projet estimé :</strong> '+formatNumber(estimate.score)+' %</p>'+
   '<p class="small"><strong>Confiance :</strong> '+esc(String(estimate.confidence||"inconnue"))+'</p>'+
   '<p class="small"><strong>Preuves :</strong> '+progressList(evidence)+'</p>'+
   '<p class="small"><strong>Travail restant :</strong> '+progressList(remainingWork)+'</p>'+
   '<p class="small"><strong>Blocages :</strong> '+progressList(blockers)+'</p>'+
   '<div class="status-grid">'+
   '<div class="status-card"><div class="status-label">Code</div><div class="status-value">'+componentValue("code")+'</div></div>'+
   '<div class="status-card"><div class="status-label">Tests</div><div class="status-value">'+componentValue("tests")+'</div></div>'+
   '<div class="status-card"><div class="status-label">Stabilité</div><div class="status-value">'+componentValue("stability")+'</div></div>'+
   '<div class="status-card"><div class="status-label">Release</div><div class="status-value">'+componentValue("release")+'</div></div>'+
   '</div>'+
   '<p class="small"><strong>Fenêtre commits :</strong> '+esc(String(commits.window||appState.window))+'</p>'+
   '<div class="status-grid">'+
   '<div class="status-card"><div class="status-label">Commits Production-OS</div><div class="status-value">'+formatNumber(commits.production_os)+'</div></div>'+
   '<div class="status-card"><div class="status-label">Commits branche GitHub</div><div class="status-value">'+(commits.github_default_branch==null?'Indisponible':formatNumber(commits.github_default_branch))+'</div></div>'+
   '</div>'+
   '<div class="status-grid">'+
   '<div class="status-card"><div class="status-label">Appels API projet</div><div class="status-value">'+formatNumber(totals.api_calls)+'</div></div>'+
   '<div class="status-card"><div class="status-label">Tokens projet</div><div class="status-value">'+formatNumber(totals.total_tokens)+'</div></div>'+
   '</div>'+
   '<h3 style="font-size:.85rem;margin:15px 0 6px">Consommation par modèle</h3>'+
   (usageProviders.length?usageProviders.map(function(row){return '<div class="small"><strong>Fournisseur :</strong> '+esc(String(row.provider||"inconnu"))+' · <strong>Modèle :</strong> '+esc(String(row.model||"inconnu"))+' · '+formatNumber(row.api_calls)+' appels · '+formatNumber(row.total_tokens)+' tokens</div>'}).join(""):'<div class="empty">Aucune consommation API détaillée.</div>')+
   '<p class="small">Points de tendance : '+formatNumber(usageTimeline.length)+'</p>'+
   '<p class="small">Workflows : '+formatNumber((workflows.workflows||[]).length)+' · exécutions récentes : '+formatNumber((history.executions||[]).length)+' · couverture historique : '+esc(String(history.history_coverage||"complète"))+'</p></div>';
 }catch(e){el.innerHTML=errorCard(e)}
}
function openWorker(encoded){
 navigate({view:"workers",workerId:decodeURIComponent(encoded),repository:null,tab:"overview"});
}
async function loadWorkersView(){
 const list=document.getElementById("workers-list");
 try{
  const data=await api("/v1/dashboard/workers");
  const rows=data.workers||[];
  list.innerHTML=rows.length?rows.map(function(worker){
   const id=String(worker.worker_id||"");
   return '<button class="secondary-btn" type="button" data-worker="'+esc(encodeURIComponent(id))+'" onclick="openWorker(this.dataset.worker)">'+esc(id)+' · '+esc(String(worker.status||"inconnu"))+'</button>';
  }).join(" "):'<div class="empty">Aucun worker enregistré.</div>';
  if(appState.workerId)await loadWorkerDetail(appState.workerId);
  else document.getElementById("worker-detail").innerHTML='<div class="empty">Sélectionne un worker.</div>';
 }catch(e){list.innerHTML=errorCard(e)}
}
function confirmControlAction(action,jobKey){
 if(!["cancel-current","retry","recover-stuck"].includes(action))return true;
 const target=jobKey?(" sur "+jobKey):"";
 const label=action==="retry"
  ?"Relancer cette tentative"
  :(action==="recover-stuck"?"Récupérer ce job bloqué":"Annuler cette tâche");
 return window.confirm(label+target+" ?");
}
function renderControlReceipt(result){
 const el=document.getElementById("worker-control-receipt");
 if(!el)return;
 const status=String((result&&result.status)||"");
 if(status==="scheduled_fallback"){
  el.textContent="Action demandée · Réveil automatique prévu ≤ 5 min";
  return;
 }
 if(status==="dispatched"){
  el.textContent="Action demandée · Réveil GitHub Actions demandé";
  return;
 }
 if(result&&result.acknowledged===true){
  el.textContent="Confirmée par le worker";
  return;
 }
 el.textContent="Action demandée · en attente de confirmation du worker";
}
async function runWorkerControl(workerId,action,jobKey=null,incidentId=null){
 if(!confirmControlAction(action,jobKey))return;
 const body={action:action};
 if(jobKey)body.job_key=jobKey;
 if(incidentId)body.incident_id=incidentId;
 const result=await api(
  "/v1/dashboard/workers/"+encodeURIComponent(workerId)+"/control",
  {method:"POST",body:JSON.stringify(body)}
 );
 renderControlReceipt(result);
 await loadWorkerDetail(workerId);
}
async function loadWorkerDetail(workerId){
 const el=document.getElementById("worker-detail");
 try{
  const base="/v1/dashboard/workers/"+encodeURIComponent(workerId);
  const results=await Promise.all([
   api(base),
   api(base+"/logs?limit=50"),
   api(base+"/usage?window="+encodeURIComponent(appState.window))
  ]);
  const detail=results[0],logs=results[1],usage=results[2],worker=detail.worker||{},totals=usage.totals||{};
  const executions=detail.executions||[];
  const recoverableJobs=detail.recoverable_jobs||[];
  const activeExecution=executions.find(function(row){return row.status==="running"})||null;
  const retryExecution=executions.find(function(row){return row.status==="failed"||row.status==="cancelled"})||null;
  const currentTask=activeExecution?(activeExecution.workflow_task_id||activeExecution.job_key||"En cours"):"Aucune";
  const currentProgress=activeExecution?activeExecution.progress_percent:null;
  const activeJobKey=activeExecution&&activeExecution.job_key?String(activeExecution.job_key):"";
  const retryJobKey=retryExecution&&retryExecution.job_key?String(retryExecution.job_key):"";
  const recent=(logs.logs||[]).slice(0,8);
  el.innerHTML=
   '<div class="card"><div class="section-head"><h2>'+esc(workerId)+'</h2><span class="badge">'+esc(String(worker.status||"inconnu"))+'</span></div>'+
   '<p class="small"><strong>Tâche actuelle :</strong> '+esc(String(currentTask))+'</p>'+
   '<p class="small"><strong>Progression :</strong> '+formatNumber(currentProgress)+' %</p>'+
   '<p class="small"><strong>Dernier heartbeat :</strong> '+esc(String(worker.last_heartbeat||"Indisponible"))+'</p>'+
   '<p class="small"><strong>Santé du worker :</strong> '+esc(String(worker.status||"inconnu"))+'</p>'+
   '<p class="small"><strong>Concurrence :</strong> '+formatNumber(worker.active_tasks)+' / '+formatNumber(worker.max_concurrency)+'</p>'+
   '<p class="small"><strong>Capacités :</strong> '+esc(Array.isArray(worker.capabilities)?worker.capabilities.join(", "):String(worker.capabilities||"Indisponible"))+'</p>'+
   '<p class="small">Exécutions : '+formatNumber(executions.length)+'</p>'+
   '<div class="status-grid">'+
   '<div class="status-card"><div class="status-label">Appels API</div><div class="status-value">'+formatNumber(totals.api_calls)+'</div></div>'+
   '<div class="status-card"><div class="status-label">Tokens</div><div class="status-value">'+formatNumber(totals.total_tokens)+'</div></div>'+
   '<div class="status-card"><div class="status-label">Coût estimé</div><div class="status-value">'+(totals.estimated_cost_usd==null?'Indisponible':formatNumber(totals.estimated_cost_usd)+' USD')+'</div></div>'+
   '</div>'+
   '<h3 style="font-size:.85rem;margin:15px 0 6px">Logs récents</h3>'+
   (recent.length?recent.map(function(row){return '<div class="small">'+esc(String(row.created_at||""))+' · <strong>Niveau :</strong> '+esc(String(row.level||"info"))+' · <strong>Étape :</strong> '+esc(String(row.stage||"—"))+' · '+esc(String(row.message||""))+'</div>'}).join(""):'<div class="empty">Aucun log récent.</div>')+
   '<h3 style="font-size:.85rem;margin:15px 0 6px">Control</h3>'+
   '<p class="small"><strong>État demandé :</strong> '+esc(String(worker.desired_state||"active"))+' · <strong>Action demandée :</strong> '+esc(String(worker.control_requested_at||"—"))+'</p>'+
   '<p class="small"><strong>Confirmée par le worker :</strong> '+esc(String(worker.control_acknowledged_at||"En attente"))+'</p>'+
   '<div class="v3-tabs">'+
   '<button class="secondary-btn" data-control-action="pause" onclick="runWorkerControl('+JSON.stringify(workerId)+',\'pause\')">Pause</button>'+
   '<button class="secondary-btn" data-control-action="resume" onclick="runWorkerControl('+JSON.stringify(workerId)+',\'resume\')">Reprendre</button>'+
   '<button class="secondary-btn" data-control-action="drain" onclick="runWorkerControl('+JSON.stringify(workerId)+',\'drain\')">Drain</button>'+
   '<button class="secondary-btn" data-control-action="kick" onclick="runWorkerControl('+JSON.stringify(workerId)+',\'kick\')">Kick</button>'+
   (activeJobKey?'<button class="secondary-btn" data-control-action="cancel-current" data-job-key="'+esc(activeJobKey)+'" onclick="runWorkerControl('+JSON.stringify(workerId)+',\'cancel-current\',this.dataset.jobKey)">Annuler '+esc(activeJobKey)+'</button>':'')+
   (retryJobKey?'<button class="secondary-btn" data-control-action="retry" data-job-key="'+esc(retryJobKey)+'" onclick="runWorkerControl('+JSON.stringify(workerId)+',\'retry\',this.dataset.jobKey)">Retry '+esc(retryJobKey)+'</button>':'')+
   recoverableJobs.map(function(row){
    const key=String(row.key||"");
    return '<button class="secondary-btn" data-control-action="recover-stuck" data-job-key="'+esc(key)+'" onclick="runWorkerControl('+JSON.stringify(workerId)+',\'recover-stuck\',this.dataset.jobKey)">Récupérer '+esc(key)+'</button>';
   }).join("")+
   '</div><div id="worker-control-receipt" class="status-message"></div>'+
   '<h3 style="font-size:.85rem;margin:15px 0 6px">Historique d’exécution</h3>'+
   (executions.length?executions.slice(0,8).map(function(row){return '<div class="small"><strong>Résultat :</strong> '+esc(String(row.status||"inconnu"))+' · '+esc(String(row.started_at||""))+' · <strong>Durée :</strong> '+(row.duration_seconds==null?'—':formatNumber(row.duration_seconds)+' s')+'</div>'}).join(""):'<div class="empty">Aucune exécution enregistrée.</div>')+
   '</div>';
 }catch(e){el.innerHTML=errorCard(e)}
}
async function createManagedProject(){
 const repository=document.getElementById("managed-create-repository").value.trim();
 const finalGoal=document.getElementById("managed-create-goal").value.trim();
 const budget=Number(document.getElementById("managed-create-budget").value||0);
 const agent=document.getElementById("managed-create-agent").value||"auto";
 const status=document.getElementById("managed-create-status");
 if(!repository||!finalGoal||!Number.isFinite(budget)||budget<=0){
  status.textContent="Repository, objectif final et budget positif requis.";
  return;
 }
 try{
  const result=await api(
   "/v1/managed-projects",
   {method:"POST",body:JSON.stringify({
    repository:repository,
    final_goal:finalGoal,
    token_budget:Math.floor(budget),
    agent_preference:agent
   })}
  );
  status.textContent="Projet créé · génération "+String((result.project||{}).generation||1);
  document.getElementById("managed-create-goal").value="";
  await loadManagedProjects();
 }catch(e){
  status.textContent=String(e).replace(/^Error:\\s*/,"");
 }
}
async function managedAction(projectId,action){
 const path="/v1/managed-projects/"+encodeURIComponent(projectId)+"/"+action;
 let body={};
 const status=document.getElementById("managed-action-status-"+projectId);
 if(action==="instructions"){
  const field=document.getElementById("managed-instruction-"+projectId);
  const instruction=field?field.value.trim():"";
  if(!instruction){
   if(status)status.textContent="Saisis une instruction.";
   return;
  }
  body={instruction:instruction};
 }
 if(action==="complete"){
  if(!window.confirm("Valider définitivement ce projet ?"))return;
  body={confirm:"MARK_PROJECT_DONE"};
 }
 try{
  await api(path,{method:"POST",body:JSON.stringify(body)});
  await loadManagedProjects();
 }catch(e){
  if(status)status.textContent=String(e).replace(/^Error:\\s*/,"");
 }
}
function renderProductionOutcome(outcome,includeSummary){
 const value=outcome||{};
 if(value.available!==true)return "";
 const parts=[];
 if(value.workflow_status)parts.push(
  "<strong>Workflow :</strong> "+esc(String(value.workflow_status))
 );
 if(value.validation_status)parts.push(
  "<strong>Validation :</strong> "+esc(String(value.validation_status))
 );
 const tests=value.validation_tests||[];
 if(tests.length)parts.push(
  "<strong>Tests :</strong> "+tests.map(function(x){return esc(String(x))}).join(", ")
 );
 const commits=value.commit_shas||[];
 if(commits.length)parts.push(
  "<strong>Commits :</strong> "+commits.map(function(x){return esc(String(x).slice(0,12))}).join(", ")
 );
 if(Number(value.artifact_count||0)>0)parts.push(
  "<strong>Artefacts :</strong> "+formatNumber(value.artifact_count)
 );
 if(Number(value.changed_file_count||0)>0)parts.push(
  "<strong>Fichiers modifiés :</strong> "+formatNumber(value.changed_file_count)
 );
 const pr=value.pull_request||null;
 if(pr&&(pr.number!=null||pr.state)){
  parts.push(
   "<strong>PR :</strong> "+
   (pr.number!=null?"#"+esc(String(pr.number)):"")+
   (pr.state?" · "+esc(String(pr.state)):"")
  );
 }
 const summary=includeSummary&&value.summary
  ?'<div class="small outcome-summary"><strong>Résultat :</strong> '+esc(String(value.summary))+'</div>'
  :"";
 return summary+(parts.length?'<div class="small outcome-evidence">'+parts.join(" · ")+'</div>':"");
}
function attentionKindLabel(kind){
 const labels={
  incident:"Incident",
  validation_failed:"CI / validation",
  project_attention:"Projet bloqué",
  project_review:"À revoir",
  blocked_job:"En attente",
  completed_project:"Terminé"
 };
 return labels[kind]||String(kind||"Action");
}
function attentionSeverityClass(severity){
 return severity==="critical"||severity==="high"?"bad":severity==="medium"?"warn":"ok";
}
async function openAttentionItem(view,targetType,targetId){
 navigate({
  view:view||"overview",
  workerId:null,
  repository:null,
  tab:null,
  focus:targetId||null
 });
}
async function attentionManagedInstruction(projectId){
 const field=document.getElementById("attention-instruction-"+projectId);
 const instruction=field?field.value.trim():"";
 if(!instruction){
  const el=document.getElementById("attention-action-status-"+projectId);
  if(el)el.textContent="Saisis une instruction.";
  return;
 }
 try{
  await api(
   "/v1/managed-projects/"+encodeURIComponent(projectId)+"/instructions",
   {method:"POST",body:JSON.stringify({instruction:instruction})}
  );
  await loadAttention();
 }catch(e){
  const el=document.getElementById("attention-action-status-"+projectId);
  if(el)el.textContent=String(e).replace(/^Error:\\s*/,"");
 }
}
async function attentionManagedAction(projectId,action){
 if(action==="complete"){
  if(!window.confirm("Valider définitivement ce projet comme DONE ?"))return;
 }
 try{
  const body=action==="complete"?{confirm:"MARK_PROJECT_DONE"}:{};
  await api(
   "/v1/managed-projects/"+encodeURIComponent(projectId)+"/"+action,
   {method:"POST",body:JSON.stringify(body)}
  );
  await loadAttention();
 }catch(e){
  const el=document.getElementById("attention-action-status-"+projectId);
  if(el)el.textContent=String(e).replace(/^Error:\\s*/,"");
 }
}
async function acknowledgeAttentionIncident(incidentId){
 try{
  await api(
   "/v1/dashboard/incidents/"+encodeURIComponent(incidentId)+"/acknowledge",
   {method:"POST",body:"{}"}
  );
  await loadAttention();
 }catch(e){
  const el=document.getElementById("attention-action-status-"+incidentId);
  if(el)el.textContent=String(e).replace(/^Error:\\s*/,"");
 }
}
async function attentionPlaybookAction(action,workerId,jobKey,incidentId){
 try{
  await runIncidentPlaybookAction(
   action,
   workerId||"",
   jobKey||"",
   incidentId||""
  );
  await loadAttention();
 }catch(e){
  const el=document.getElementById("attention-action-status-"+incidentId);
  if(el)el.textContent=String(e).replace(/^Error:\\s*/,"");
 }
}
function renderAttentionActions(item){
 const actions=item.actions||[];
 const targetId=String(item.target_id||"");
 const incidentId=String(item.incident_id||"");
 const buttons=actions.map(function(action){
  const name=String(action.name||"");
  if(name==="instructions"){
   return '<div class="attention-inline-instruction"><textarea id="attention-instruction-'+esc(targetId)+'" rows="2" placeholder="Instruction supplémentaire"></textarea><button class="secondary-btn" type="button" data-project-id="'+esc(targetId)+'" onclick="attentionManagedInstruction(this.dataset.projectId)">'+esc(String(action.label||"Ajouter instruction"))+'</button></div>';
  }
  if(name==="verify"||name==="complete"){
   return '<button class="secondary-btn" type="button" data-project-id="'+esc(targetId)+'" data-action="'+esc(name)+'" onclick="attentionManagedAction(this.dataset.projectId,this.dataset.action)">'+esc(String(action.label||name))+'</button>';
  }
  if(name==="acknowledge"){
   return '<button class="secondary-btn" type="button" data-incident-id="'+esc(incidentId)+'" onclick="acknowledgeAttentionIncident(this.dataset.incidentId)">'+esc(String(action.label||"Acquitter"))+'</button>';
  }
  if(name==="playbook"){
   const controlAction=String(action.control_action||"");
   return '<button class="secondary-btn" type="button" data-action="'+esc(controlAction)+'" data-worker-id="'+esc(String(action.worker_id||""))+'" data-job-key="'+esc(String(action.job_key||""))+'" data-incident-id="'+esc(incidentId)+'" onclick="attentionPlaybookAction(this.dataset.action,this.dataset.workerId,this.dataset.jobKey,this.dataset.incidentId)">'+esc(incidentPlaybookActionLabel(controlAction))+'</button>';
  }
  return "";
 }).join("");
 return buttons?'<div class="attention-actions">'+buttons+'</div>':"";
}
async function loadAttention(){
 const el=document.getElementById("attention-list");
 const count=document.getElementById("attention-count");
 try{
  const data=await api("/v1/dashboard/attention?limit=50");
  const summary=data.summary||{};
  const rows=data.items||[];
  count.textContent=String(summary.action_required||0);
  const headline=
   '<div class="card attention-summary"><div class="section-head"><strong>Priorités</strong><span class="badge">'+formatNumber(summary.action_required||0)+' action(s)</span></div>'+
   '<div class="small"><strong>À revoir :</strong> '+formatNumber(summary.projects_to_review||0)+
   ' · <strong>À débloquer :</strong> '+formatNumber(summary.projects_needing_attention||0)+
   ' · <strong>Jobs bloqués :</strong> '+formatNumber(summary.blocked_jobs||0)+
   (Number(summary.blocked_jobs||0)>Number(summary.blocked_jobs_shown||0)?' ('+formatNumber(summary.blocked_jobs_shown||0)+' affichés)':'')+
   ' · <strong>Incidents :</strong> '+formatNumber(summary.incidents||0)+
   ' · <strong>Terminés récemment :</strong> '+formatNumber(summary.recently_completed||0)+'</div></div>';
  if(!rows.length){
   el.innerHTML=headline+'<div class="card"><strong>Rien d’urgent.</strong><div class="small">Les productions autonomes n’attendent aucune action opérateur.</div></div>';
   return;
  }
  const cards=rows.map(function(item){
   const required=item.action_required===true;
   const repository=item.repository?'<div class="small"><strong>'+esc(String(item.repository))+'</strong></div>':'';
   const summaryText=item.summary?'<div class="small">'+esc(String(item.summary))+'</div>':'';
   const outcomeHtml=renderProductionOutcome(item.outcome||{},false);
   const openButton=item.view
    ?'<button class="secondary-btn" type="button" data-view="'+esc(String(item.view||"overview"))+'" data-target-type="'+esc(String(item.target_type||""))+'" data-target-id="'+esc(String(item.target_id||""))+'" onclick="openAttentionItem(this.dataset.view,this.dataset.targetType,this.dataset.targetId)">Ouvrir</button>'
    :'';
   const contextual=required?renderAttentionActions(item):"";
   const statusId=String(item.incident_id||item.target_id||item.id||"");
   return '<div class="card attention-card '+(required?'attention-required':'attention-done')+'">'+
    '<div class="section-head"><strong>'+esc(String(item.title||"Action"))+'</strong>'+
    '<span class="badge">'+dot(attentionSeverityClass(String(item.severity||"info")))+esc(attentionKindLabel(item.kind))+'</span></div>'+
    repository+summaryText+outcomeHtml+
    '<div class="small">'+(required?'Action opérateur requise':'Information récente')+(item.updated_at?' · '+esc(String(item.updated_at)):'')+'</div>'+
    '<div class="attention-actions">'+openButton+'</div>'+contextual+
    '<div id="attention-action-status-'+esc(statusId)+'" class="status-message"></div></div>';
  }).join("");
  el.innerHTML=headline+cards;
 }catch(e){
  count.textContent="!";
  el.innerHTML=errorCard(e);
 }
}

async function loadManagedProjects(){
 const el=document.getElementById("managed-list");
 const count=document.getElementById("managed-count");
 try{
  await loadRepositories();
  const data=await api("/v1/managed-projects");
  const rows=data.projects||[];
  count.textContent=String(rows.length);
  el.innerHTML=rows.length?rows.map(function(row){
   const usage=row.usage||{};
   const outcome=row.outcome||{};
   const projectId=String(row.project_id||row.id||row.workflow_id||"");
   const status=String(row.status||row.state||"");
   const canFollow=status==="REVIEW_REQUIRED"||status==="NEEDS_ATTENTION";
   const canComplete=status==="REVIEW_REQUIRED";
   const runs=row.runs||[];
   const actions=canFollow
    ?'<textarea id="managed-instruction-'+esc(projectId)+'" rows="3" placeholder="Instruction supplémentaire"></textarea><div class="v3-tabs"><button class="secondary-btn" data-project-id="'+esc(projectId)+'" onclick="managedAction(this.dataset.projectId,\'instructions\')">Ajouter instruction</button><button class="secondary-btn" data-project-id="'+esc(projectId)+'" onclick="managedAction(this.dataset.projectId,\'verify\')">Retester</button>'+(canComplete?'<button class="secondary-btn" data-project-id="'+esc(projectId)+'" onclick="managedAction(this.dataset.projectId,\'complete\')">Valider DONE</button>':'')+'</div><div id="managed-action-status-'+esc(projectId)+'" class="status-message"></div>'
    :'';
   const history=runs.length?'<div class="small"><strong>Générations :</strong> '+runs.map(function(run){return 'g'+esc(String(run.generation||""))+' '+esc(String(run.kind||""))}).join(" · ")+'</div>':'';
   return '<div class="card'+(appState.focus===projectId?' attention-focus':'')+'" data-managed-project-id="'+esc(projectId)+'"><div class="section-head"><strong>'+esc(String(row.repository||""))+'</strong><span class="badge">'+esc(status)+'</span></div>'+
    '<div class="small"><strong>Objectif :</strong> '+esc(String(row.final_goal||""))+'</div>'+
    renderProductionOutcome(outcome,true)+
    '<div class="small"><strong>Génération actuelle :</strong> '+formatNumber(row.generation||1)+' · <strong>Budget :</strong> '+formatNumber(row.token_budget)+' tokens · <strong>Utilisés :</strong> '+formatNumber(usage.total_tokens||0)+' · <strong>Agent :</strong> '+esc(String(row.agent_preference||"auto"))+'</div>'+
    history+actions+'</div>';
  }).join(""):'<div class="empty">Aucun projet managé.</div>';
  if(appState.focus){
   const focused=el.querySelector('[data-managed-project-id="'+CSS.escape(String(appState.focus))+'"]');
   if(focused)setTimeout(function(){focused.scrollIntoView({block:"center"})},0);
  }
 }catch(e){el.innerHTML=errorCard(e)}
}
async function loadActivityView(){
 const el=document.getElementById("activity-list");
 try{
  const results=await Promise.all([
   api("/v1/dashboard/activity?limit=100"),
   api("/v1/dashboard/control-audit?limit=50"),
   api("/v1/dashboard/remediations?limit=50"),
   api("/v1/dashboard/remediation-analytics?window="+encodeURIComponent(appState.window))
  ]);
  const data=results[0],audit=results[1],remediation=results[2],analytics=results[3]||{},rows=data.events||[],controls=audit.events||[],remediations=remediation.events||[];
  const remediationSummary=analytics.summary||{};
  const remediationByAction=analytics.by_action||[];
  const remediationByIncident=analytics.by_incident_code||[];
  const auditHtml=
   '<div class="card"><div class="section-head"><h2>Audit des contrôles</h2><span class="badge">'+formatNumber(controls.length)+'</span></div>'+
   (controls.length?controls.map(function(row){
    const target=row.job_key?(' · job '+String(row.job_key)):(' · worker '+String(row.worker_id||""));
    const error=row.error_code?(' · erreur '+String(row.error_code)):'';
    return '<div class="small"><strong>'+esc(String(row.action||"action"))+'</strong>'+esc(target)+' · '+esc(String(row.outcome||""))+' · '+esc(String(row.requested_by||""))+' · '+esc(String(row.requested_at||""))+esc(error)+'</div>';
   }).join(""):'<div class="empty">Aucune action opérateur enregistrée.</div>')+
   '</div>';
  const remediationAnalyticsHtml=
   '<div class="card"><div class="section-head"><h2>Analytics des remédiations</h2><span class="badge">'+esc(appState.window)+'</span></div>'+
   '<p class="small"><strong>Total :</strong> '+formatNumber(remediationSummary.total)+' · <strong>Résolues :</strong> '+formatNumber(remediationSummary.resolved)+' · <strong>Toujours actives :</strong> '+formatNumber(remediationSummary.still_active)+' · <strong>En attente :</strong> '+formatNumber(remediationSummary.pending)+' · <strong>Non applicables :</strong> '+formatNumber(remediationSummary.not_applicable)+'</p>'+
   '<p class="small"><strong>Taux de résolution observé :</strong> '+(remediationSummary.observed_resolution_rate==null?'Indisponible':formatNumber(remediationSummary.observed_resolution_rate)+' %')+' · <strong>Échantillon d’efficacité :</strong> '+formatNumber(remediationSummary.effectiveness_denominator)+' · <strong>Médiane détection résolution :</strong> '+(remediationSummary.median_resolution_detection_seconds==null?'Indisponible':formatNumber(remediationSummary.median_resolution_detection_seconds)+' s')+'</p>'+
   '<p class="small"><strong>Surveillance de récidive :</strong> '+formatNumber(remediationSummary.watching_recurrence)+' · <strong>Récidives observées :</strong> '+formatNumber(remediationSummary.recurred)+' · <strong>Taux de récidive observé :</strong> '+(remediationSummary.observed_recurrence_rate==null?'Indisponible':formatNumber(remediationSummary.observed_recurrence_rate)+' %')+' · <strong>Échantillon récidive :</strong> '+formatNumber(remediationSummary.recurrence_denominator)+'</p>'+
   '<p class="small"><strong>Médiane avant récidive :</strong> '+(remediationSummary.median_time_to_recurrence_seconds==null?'Indisponible':formatNumber(remediationSummary.median_time_to_recurrence_seconds)+' s')+' · <strong>Min :</strong> '+(remediationSummary.min_time_to_recurrence_seconds==null?'—':formatNumber(remediationSummary.min_time_to_recurrence_seconds)+' s')+' · <strong>Max :</strong> '+(remediationSummary.max_time_to_recurrence_seconds==null?'—':formatNumber(remediationSummary.max_time_to_recurrence_seconds)+' s')+' · <strong>Âge médian des résolutions surveillées :</strong> '+(remediationSummary.median_watching_age_seconds==null?'Indisponible':formatNumber(remediationSummary.median_watching_age_seconds)+' s')+'</p>'+
   '<h3 style="font-size:.85rem;margin:12px 0 6px">Par action</h3>'+
   (remediationByAction.length?remediationByAction.map(function(row){
    return '<div class="small"><strong>'+esc(String(row.name||"action"))+'</strong> · '+formatNumber(row.resolved)+' résolue(s) / '+formatNumber(row.effectiveness_denominator)+' vérifiée(s) · taux '+(row.observed_resolution_rate==null?'—':formatNumber(row.observed_resolution_rate)+' %')+'</div>';
   }).join(""):'<div class="empty">Aucune donnée vérifiée.</div>')+
   '<h3 style="font-size:.85rem;margin:12px 0 6px">Par incident</h3>'+
   (remediationByIncident.length?remediationByIncident.map(function(row){
    return '<div class="small"><strong>'+esc(String(row.name||"incident"))+'</strong> · '+formatNumber(row.resolved)+' résolue(s) / '+formatNumber(row.effectiveness_denominator)+' vérifiée(s) · taux '+(row.observed_resolution_rate==null?'—':formatNumber(row.observed_resolution_rate)+' %')+'</div>';
   }).join(""):'<div class="empty">Aucune donnée vérifiée.</div>')+
   '</div>';
  const remediationHtml=
   '<div class="card"><div class="section-head"><h2>Historique des remédiations</h2><span class="badge">'+formatNumber(remediations.length)+'</span></div>'+
   (remediations.length?remediations.map(function(row){
    const target=row.job_key?('job '+String(row.job_key)):('worker '+String(row.worker_id||"—"));
    const error=row.error_code?(' · erreur '+String(row.error_code)):'';
    const verification=String(row.verification_state||"pending");
    const verified=row.verified_at?(' · vérifié '+String(row.verified_at)):'';
    const recurrence=String(row.recurrence_state||"not_evaluated");
    const recurred=row.recurred_at?(' · récidive '+String(row.recurred_at)):'';
    const checks=Number(row.verification_checks||0);
    return '<div class="small"><strong>'+esc(String(row.action||"action"))+'</strong> · incident '+esc(String(row.incident_id||""))+' · '+esc(target)+' · résultat '+esc(String(row.outcome||""))+' · vérification '+esc(verification)+' ('+formatNumber(checks)+' contrôle(s))'+esc(verified)+' · récidive '+esc(recurrence)+esc(recurred)+' · '+esc(String(row.requested_by||""))+' · '+esc(String(row.requested_at||""))+esc(error)+'</div>';
   }).join(""):'<div class="empty">Aucune remédiation liée à un incident.</div>')+
   '</div>';
  const activityHtml=rows.length?rows.slice().reverse().map(function(row){
   return '<div class="card"><div class="section-head"><strong>'+esc(String(row.event_type||"événement"))+'</strong><span class="badge">'+esc(String(row.repository||"global"))+'</span></div><div class="small">'+esc(String(row.created_at||""))+'</div></div>';
  }).join(""):'<div class="empty">Aucune activité enregistrée.</div>';
  el.innerHTML=remediationAnalyticsHtml+remediationHtml+auditHtml+activityHtml;
 }catch(e){el.innerHTML=errorCard(e)}
}
function navigate(next){
 Object.assign(appState,next||{});
 const params=new URLSearchParams();
 if(appState.view)params.set("view",appState.view);
 if(appState.workerId)params.set("worker",appState.workerId);
 if(appState.repository)params.set("repo",appState.repository);
 if(appState.tab)params.set("tab",appState.tab);
 if(appState.focus)params.set("target",appState.focus);
 history.replaceState(null,"","/dashboard?"+params.toString());
 renderActiveView();
}
async function renderActiveView(){
 document.querySelectorAll(".v3-view").forEach(function(el){el.classList.remove("active")});
 const target=document.getElementById("view-"+appState.view);
 if(target)target.classList.add("active");
 clearViewPolls();
 const loaders={attention:loadAttention,overview:loadOverview,projects:loadProjectsView,workers:loadWorkersView,autopilot:loadAutopilot,managed:loadManagedProjects,activity:loadActivityView};
 const loader=loaders[appState.view]||loadAttention;
 await loader();
 schedulePoll("active-view",appState.view==="overview"?15000:5000,loader);
}
function schedulePoll(key,intervalMs,fn){
 if(appState.polling.has(key))clearInterval(appState.polling.get(key));
 const id=setInterval(async function(){
  const y=window.scrollY;
  await fn();
  if(Math.abs(window.scrollY-y)>1)window.scrollTo({top:y,behavior:"instant"});
 },intervalMs);
 appState.polling.set(key,id);
}
renderActiveView();
</script>
</body>
</html>"""
