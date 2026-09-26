from __future__ import annotations
from .dashboard_ui_legacy import DASHBOARD_HTML as _BASE_HTML

DASHBOARD_HTML = _BASE_HTML
DASHBOARD_HTML = DASHBOARD_HTML.replace(
    '.production-inbox-card{scroll-margin-top:80px}',
    '.production-filter-tabs{display:flex;gap:6px;overflow-x:auto;margin:0 0 10px}.production-filter-tabs button{white-space:nowrap}.production-inbox-card{scroll-margin-top:80px}',
)
DASHBOARD_HTML = DASHBOARD_HTML.replace(
    '<div id="view-productions" class="v3-view"><div class="section-head"><h2>Productions</h2><span id="productions-count" class="badge">0</span></div><div id="productions-list"></div></div>',
    '<div id="view-productions" class="v3-view"><div class="section-head"><h2>Productions</h2><span id="productions-count" class="badge">0</span></div><div class="production-filter-tabs" aria-label="Filtrer les productions"><button type="button" data-production-filter="all" onclick="setProductionFilter(\'all\')">Toutes</button><button type="button" data-production-filter="active" onclick="setProductionFilter(\'active\')">Actives</button><button type="button" data-production-filter="review" onclick="setProductionFilter(\'review\')">À revoir</button><button type="button" data-production-filter="problems" onclick="setProductionFilter(\'problems\')">Problèmes</button><button type="button" data-production-filter="completed" onclick="setProductionFilter(\'completed\')">Terminées</button></div><div id="productions-list"></div></div>',
)
DASHBOARD_HTML = DASHBOARD_HTML.replace(
    'let launchReadiness=null;',
    'let launchReadiness=null;\nlet productionFilter="all";',
)
DASHBOARD_HTML = DASHBOARD_HTML.replace(
    'async function loadProductionInbox(){',
    'function setProductionFilter(value){\n productionFilter=String(value||"all");\n return loadProductionInbox();\n}\nasync function loadProductionInbox(){',
)
DASHBOARD_HTML = DASHBOARD_HTML.replace(
    'const data=await api("/v1/dashboard/productions?limit=50");',
    'const data=await api("/v1/dashboard/productions?limit=50"+"&filter="+encodeURIComponent(productionFilter));',
)
DASHBOARD_HTML = DASHBOARD_HTML.replace(
    "'<strong>Actives :</strong> '+formatNumber(summary.active||0)+",
    "'<strong>Total :</strong> '+formatNumber(summary.total||0)+' · <strong>Actives :</strong> '+formatNumber(summary.active||0)+",
)
