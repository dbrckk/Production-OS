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

body{overflow-x:hidden}
.v3-nav{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;position:sticky;top:0;z-index:20;padding:8px;background:rgba(8,13,24,.94);backdrop-filter:blur(12px)}
.v3-nav button{border:1px solid var(--line);background:var(--panel);color:var(--text);padding:10px 6px;border-radius:12px;font-weight:700}
.v3-workspace{margin:12px 0}.v3-view{display:none}.v3-view.active{display:block}.v3-tabs{display:flex;gap:6px;overflow-x:auto;padding:6px 0}.v3-tabs button{white-space:nowrap}
@media(max-width:640px){.shell{padding-left:10px;padding-right:10px}.v3-nav{font-size:12px}}
</style>
</head>
<body>
<div class="shell">
<nav class="v3-nav" aria-label="Navigation principale">
<button data-view="overview" onclick="navigate({view:'overview',workerId:null,repository:null,tab:null})">Vue générale</button>
<button data-view="projects" onclick="navigate({view:'projects',workerId:null,repository:null,tab:null})">Projets</button>
<button data-view="workers" onclick="navigate({view:'workers',workerId:null,repository:null,tab:null})">Workers</button>
<button data-view="activity" onclick="navigate({view:'activity',workerId:null,repository:null,tab:null})">Activité</button>
</nav>
<section class="v3-workspace" aria-live="polite">
<div id="view-overview" class="v3-view active"><div class="section-head"><h2>Vue générale</h2><div class="v3-tabs" aria-label="Période"><button type="button" onclick="setDashboardWindow('24h')">24h</button><button type="button" onclick="setDashboardWindow('7d')">7d</button><button type="button" onclick="setDashboardWindow('30d')">30d</button></div></div><div id="overview-metrics"></div></div>
<div id="view-projects" class="v3-view"><h2>Projets</h2><div id="projects-list"></div><div class="v3-tabs" aria-label="Détail projet"><button>Aperçu</button><button>Avancement</button><button>Commits</button><button>API</button><button>Workflows</button><button>Qualité</button><button>Historique</button></div><div id="project-detail"></div></div>
<div id="view-workers" class="v3-view"><h2>Workers</h2><div id="workers-list"></div><div class="v3-tabs" aria-label="Détail worker"><button>Aperçu</button><button>Tâches</button><button>Logs</button><button>API</button><button>Historique</button></div><div id="worker-detail"></div></div>
<div id="view-activity" class="v3-view"><h2>Activité</h2><div id="activity-list"></div></div>
</section>
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
document.getElementById('repository').addEventListener('change',loadVisualQuality);
document.getElementById('repository').addEventListener('change',loadRecentRuns);
setInterval(loadVisualQuality,10000);
setInterval(function(){loadWorkerStatus();loadRecentRuns()},10000);

const appState={view:"overview",workerId:null,repository:null,tab:null,window:"7d",polling:new Map()};
(function restoreNavigation(){
 const q=new URLSearchParams(window.location.search);
 const view=q.get("view");
 if(["overview","projects","workers","activity"].includes(view))appState.view=view;
 appState.workerId=q.get("worker")||null;
 appState.repository=q.get("repo")||null;
 appState.tab=q.get("tab")||null;
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
function errorCard(error){
 return '<div class="card"><div class="small">'+esc(String(error).replace(/^Error:\\s*/,''))+'</div></div>';
}
function repoApiPath(repository){
 return String(repository).split("/").map(encodeURIComponent).join("/");
}
async function loadOverview(){
 const el=document.getElementById("overview-metrics");
 try{
  const data=await api("/v1/dashboard/overview?window="+encodeURIComponent(appState.window));
  const w=data.workers||{},p=data.productions||{},u=data.usage||{},c=data.commits||{},perf=data.performance||{};
  el.innerHTML=
   '<div class="status-grid">'+
   '<div class="status-card"><div class="status-label">Workers en ligne</div><div class="status-value">'+formatNumber(w.online)+' / '+formatNumber(w.total)+'</div></div>'+
   '<div class="status-card"><div class="status-label">Productions actives</div><div class="status-value">'+formatNumber(p.running)+'</div></div>'+
   '<div class="status-card"><div class="status-label">Tokens · '+esc(appState.window)+'</div><div class="status-value">'+formatNumber(u.tokens)+'</div></div>'+
   '</div>'+
   '<div class="card"><div class="section-head"><h2>Activité mesurée</h2></div>'+
   '<p class="small">API calls : '+formatNumber(u.api_calls)+' · coût estimé : '+formatNumber(u.estimated_cost_usd)+' USD</p>'+
   '<p class="small">Commits Production-OS : '+formatNumber(c.production_os)+' · branche par défaut GitHub : '+formatNumber(c.github_default_branch)+'</p>'+
   '<p class="small">Taux de réussite : '+formatNumber(perf.success_rate)+' % · temps d’exécution : '+formatNumber(perf.execution_seconds)+' s</p></div>';
 }catch(e){el.innerHTML=errorCard(e)}
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
  el.innerHTML=
   '<div class="card"><div class="section-head"><h2>'+esc(repository)+'</h2><span class="badge">'+esc(String((detail.snapshot||{}).ci_status||"CI inconnue"))+'</span></div>'+
   '<p class="small"><strong>Production actuelle :</strong> '+formatNumber(production.percent)+' %</p>'+
   '<p class="small"><strong>Projet estimé :</strong> '+formatNumber(estimate.score)+' % · confiance '+esc(String(estimate.confidence||"inconnue"))+'</p>'+
   '<p class="small">Commits Production-OS : '+formatNumber(commits.production_os)+' · branche GitHub : '+formatNumber(commits.github_default_branch)+'</p>'+
   '<p class="small">API : '+formatNumber(totals.api_calls)+' appels · '+formatNumber(totals.total_tokens)+' tokens · '+formatNumber(totals.estimated_cost_usd)+' USD estimés</p>'+
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
  const activeExecution=executions.find(function(row){return row.status==="running"})||null;
  const currentTask=activeExecution?(activeExecution.workflow_task_id||activeExecution.job_key||"En cours"):"Aucune";
  const currentProgress=activeExecution?activeExecution.progress_percent:null;
  const recent=(logs.logs||[]).slice(0,8);
  el.innerHTML=
   '<div class="card"><div class="section-head"><h2>'+esc(workerId)+'</h2><span class="badge">'+esc(String(worker.status||"inconnu"))+'</span></div>'+
   '<p class="small"><strong>Tâche actuelle :</strong> '+esc(String(currentTask))+'</p>'+
   '<p class="small"><strong>Progression :</strong> '+formatNumber(currentProgress)+' %</p>'+
   '<p class="small"><strong>Dernier heartbeat :</strong> '+esc(String(worker.last_heartbeat||"Indisponible"))+'</p>'+
   '<p class="small">Tâches actives : '+formatNumber(worker.active_tasks)+' / '+formatNumber(worker.max_concurrency)+'</p>'+
   '<p class="small">Exécutions : '+formatNumber(executions.length)+' · API : '+formatNumber(totals.api_calls)+' appels · '+formatNumber(totals.total_tokens)+' tokens</p>'+
   '<h3 style="font-size:.85rem;margin:15px 0 6px">Logs récents</h3>'+
   (recent.length?recent.map(function(row){return '<div class="small">'+esc(String(row.created_at||""))+' · '+esc(String(row.level||"info"))+' · '+esc(String(row.message||""))+'</div>'}).join(""):'<div class="empty">Aucun log récent.</div>')+
   '</div>';
 }catch(e){el.innerHTML=errorCard(e)}
}
async function loadActivityView(){
 const el=document.getElementById("activity-list");
 try{
  const data=await api("/v1/dashboard/activity?limit=100");
  const rows=data.events||[];
  el.innerHTML=rows.length?rows.slice().reverse().map(function(row){
   return '<div class="card"><div class="section-head"><strong>'+esc(String(row.event_type||"événement"))+'</strong><span class="badge">'+esc(String(row.repository||"global"))+'</span></div><div class="small">'+esc(String(row.created_at||""))+'</div></div>';
  }).join(""):'<div class="empty">Aucune activité enregistrée.</div>';
 }catch(e){el.innerHTML=errorCard(e)}
}
function navigate(next){
 Object.assign(appState,next||{});
 const params=new URLSearchParams();
 if(appState.view)params.set("view",appState.view);
 if(appState.workerId)params.set("worker",appState.workerId);
 if(appState.repository)params.set("repo",appState.repository);
 if(appState.tab)params.set("tab",appState.tab);
 history.replaceState(null,"","/dashboard?"+params.toString());
 renderActiveView();
}
async function renderActiveView(){
 document.querySelectorAll(".v3-view").forEach(function(el){el.classList.remove("active")});
 const target=document.getElementById("view-"+appState.view);
 if(target)target.classList.add("active");
 clearViewPolls();
 const loaders={overview:loadOverview,projects:loadProjectsView,workers:loadWorkersView,activity:loadActivityView};
 const loader=loaders[appState.view]||loadOverview;
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
