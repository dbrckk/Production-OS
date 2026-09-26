from __future__ import annotations
from . import control_plane_legacy as _legacy
from .dashboard_service import set_request_production_filter

_original_parse_qs = _legacy.parse_qs

def _release46_parse_qs(query_string, *args, **kwargs):
    parsed = _original_parse_qs(query_string, *args, **kwargs)
    set_request_production_filter(parsed.get("filter", [None])[0])
    return parsed

_legacy.parse_qs = _release46_parse_qs
from .control_plane_legacy import *
