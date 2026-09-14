from __future__ import annotations

import html
import json
from pathlib import Path


def render_control_surface(payload: dict) -> str:
    schedule = payload.get("schedule", {})
    allocation = payload.get("resource_allocation", {})
    work = schedule.get("work", [])

    rows = []
    for item in work:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('lane','')))}</td>"
            f"<td>{html.escape(str(item.get('repository','')))}</td>"
            f"<td>{html.escape(str(item.get('task','')))}</td>"
            f"<td>{html.escape(str(item.get('score','')))}</td>"
            f"<td>{html.escape(', '.join(item.get('blockers',[])))}</td>"
            "</tr>"
        )

    allocation_rows = []
    for item in allocation.get("allocations", []):
        allocation_rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('repository','')))}</td>"
            f"<td>{html.escape(str(item.get('task','')))}</td>"
            f"<td>{html.escape(str(item.get('slots','')))}</td>"
            "</tr>"
        )

    raw = html.escape(json.dumps(payload, indent=2, ensure_ascii=False))

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Production-OS Control Surface</title>
<style>
body{{font-family:system-ui,sans-serif;margin:2rem;line-height:1.4}}
table{{border-collapse:collapse;width:100%;margin:1rem 0 2rem}}
th,td{{border:1px solid #ccc;padding:.55rem;text-align:left;vertical-align:top}}
pre{{white-space:pre-wrap;overflow:auto;background:#f5f5f5;padding:1rem}}
</style>
</head>
<body>
<h1>Production-OS Control Surface</h1>
<h2>Schedule</h2>
<table><thead><tr><th>Lane</th><th>Repository</th><th>Task</th><th>Score</th><th>Blockers</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<h2>Resource allocation</h2>
<table><thead><tr><th>Repository</th><th>Task</th><th>Slots</th></tr></thead>
<tbody>{''.join(allocation_rows)}</tbody></table>
<h2>Raw payload</h2>
<pre>{raw}</pre>
</body></html>"""


def write_control_surface(payload: dict, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_control_surface(payload), encoding="utf-8")
