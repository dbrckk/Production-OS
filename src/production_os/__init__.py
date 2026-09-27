"""Production-OS portfolio control plane."""

__version__ = "0.1.0"

# Release 56 keeps dashboard runtime/API contracts intact while layering the
# presentation system before consumers import DASHBOARD_HTML.
from . import dashboard_ui as _dashboard_ui
from .dashboard_stable_ui import apply_stable_dashboard_theme as _apply_stable_dashboard_theme

_dashboard_ui.DASHBOARD_HTML = _apply_stable_dashboard_theme(_dashboard_ui.DASHBOARD_HTML)
