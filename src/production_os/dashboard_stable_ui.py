from __future__ import annotations

STABLE_DASHBOARD_CSS = r"""
:root{
 --surface-0:#070b14;--surface-1:#0e1624;--surface-2:#152033;
 --border-subtle:#26344b;--border-strong:#385071;
 --radius-card:18px;--radius-control:12px;
 --shadow-card:0 18px 46px rgba(0,0,0,.24);--control-height:44px;
 --focus-ring:0 0 0 3px rgba(110,168,254,.24)
}
html,body{max-width:100%;overflow-x:hidden}
body{background:var(--surface-0)}
.shell{max-width:1040px}
.card,.status-card,.settings-panel{border-color:var(--border-subtle);box-shadow:var(--shadow-card)}
.card{border-radius:var(--radius-card)}
.status-card{background:linear-gradient(180deg,rgba(21,32,51,.92),rgba(14,22,36,.94))}
.status-label{color:#9aa9bd;font-weight:800}
.status-value,.run-title,.small,.worker-detail,.card,.v3-view{overflow-wrap:anywhere}
.icon-btn,.secondary-btn,.primary-btn,.danger-btn,select,input{min-height:var(--control-height);border-radius:var(--radius-control)}
textarea{border-radius:var(--radius-control)}
button,select,input,textarea{transition:border-color .15s ease,background-color .15s ease,box-shadow .15s ease,transform .15s ease}
button:focus-visible,select:focus-visible,input:focus-visible,textarea:focus-visible,a:focus-visible,summary:focus-visible{
 outline:2px solid var(--accent);outline-offset:2px;box-shadow:var(--focus-ring)
}
.v3-nav{grid-template-columns:repeat(8,minmax(0,1fr));border:1px solid var(--border-subtle);border-radius:16px;box-shadow:0 12px 34px rgba(0,0,0,.18)}
.v3-nav button{min-width:0;color:#aebbd0;background:transparent;border-color:transparent}
.v3-nav button:hover{background:var(--surface-2);color:var(--text)}
.v3-nav button.active,.v3-nav button[aria-current="page"]{background:rgba(110,168,254,.14);border-color:rgba(110,168,254,.48);color:#dbeafe}
.section-head{flex-wrap:wrap}
.badge,.run-state,.quality-badge{border:1px solid rgba(148,163,184,.12)}
.empty{border:1px dashed var(--border-subtle);border-radius:var(--radius-control);padding:12px;background:rgba(14,22,36,.55)}
.production-inbox-card,.attention-card{overflow-wrap:anywhere}
.production-detail .detail-actions,.attention-actions{flex-wrap:wrap}
@media(max-width:560px){
 .topbar,.brand,.section-head,.attention-actions,.production-detail .detail-actions{flex-wrap:wrap}
 .v3-nav{display:flex;flex-wrap:wrap;position:sticky;top:0;gap:5px;padding:7px}
 .v3-nav button{flex:1 1 calc(25% - 5px);min-width:72px;padding:9px 5px}
 .launch-row{grid-template-columns:minmax(0,1fr) auto}
 .launch-row .primary-btn{min-width:0}
 .run{grid-template-columns:minmax(0,1fr) auto}
 .run-title{white-space:normal;overflow-wrap:anywhere}
 .production-filter-tabs,.v3-tabs{flex-wrap:wrap;overflow-x:visible}
 .production-filter-tabs button,.v3-tabs button{flex:1 1 auto}
 .status-value{white-space:normal;overflow-wrap:anywhere}
 .settings-actions{grid-template-columns:1fr}
 .settings-actions .secondary-btn:last-child{grid-column:auto}
}
@media (prefers-reduced-motion: reduce){
 *,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;scroll-behavior:auto!important}
}
"""


def apply_stable_dashboard_theme(html: str) -> str:
    """Layer the Release 56 presentation system onto the existing dashboard contract."""
    marker = "</style>"
    if marker not in html or STABLE_DASHBOARD_CSS in html:
        return html
    return html.replace(marker, STABLE_DASHBOARD_CSS + "\n" + marker, 1)
