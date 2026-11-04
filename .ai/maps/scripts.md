This file is a merged representation of a subset of the codebase, containing specifically included files and files not matching ignore patterns, combined into a single document by Repomix.
The content has been processed where content has been compressed (code blocks are separated by ⋮---- delimiter).

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: **/*.{py,js,mjs,cjs,ts,tsx,jsx,java,kt,kts,gd,groovy,gradle,toml,json,yaml,yml,sql,sh}
- Files matching these patterns are excluded: .ai/**, **/node_modules/**, **/.gradle/**, **/build/**, **/dist/**, **/.venv/**, **/__pycache__/**, **/.pytest_cache/**, **/.git/**, **/coverage/**, **/*.lock, **/*.min.js, **/*.map, assets/**, art/**, art_sources/**, marketing/**, colab/**, kaggle/**, discovery-cache.json, health-snapshot.json, history.json
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Content has been compressed - code blocks are separated by ⋮---- delimiter
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
render-start.py
verify-render-cutover.py
```

# Files

## File: render-start.py
```python
#!/usr/bin/env python3
⋮----
def _required(*names: str) -> tuple[str, ...]
⋮----
values = tuple(str(os.environ.get(name) or "").strip() for name in names)
missing = [name for name, value in zip(names, values) if not value]
⋮----
# Report every absent setting in one failed deployment, never values.
⋮----
def digest(value: str) -> str
⋮----
# The owner permanently relocated Production-OS to the studycall12 Render account.
# These three manually created controllers share the same Neon database and must
# never restart as concurrent writers after the original account's quota reset.
# Render supplies RENDER_SERVICE_ID at runtime for both Docker and Python.
_RETIRED_RENDER_SERVICE_IDS = frozenset({
⋮----
"srv-dancka740ujc73bgdddg",  # production-os1
"srv-dancjugae00c73earbe0",  # Production-OS
"srv-dancfm3tqb8s73bek920",  # production-os
⋮----
_PRIMARY_RENDER_SERVICE_ID = "srv-dbj1hiuc6qcc73b7afvg"
⋮----
def main() -> None
⋮----
service_id = str(os.environ.get("RENDER_SERVICE_ID") or "").strip()
# Render guarantees RENDER=true and RENDER_SERVICE_ID at runtime. Missing
# identity on that platform must never silently bypass the writer gate.
⋮----
# Prevent a second controller from activating when secrets are set.
# Enable only after independently suspending the legacy writer.
⋮----
# The existing Actions schedule can poll without a GitHub dispatch PAT.
# Do not reject a valid database + worker/operator configuration merely
# because the faster, optional immediate wake is unavailable.
⋮----
worker_name = str(
⋮----
# Duplicate secrets collapse the operator/worker role boundary. Refuse
# to start rather than choosing an arbitrary role for the same digest.
⋮----
# render.yaml does not configure an already manually created Render service.
# Missing dispatch routing otherwise yields a healthy API with no worker wake.
⋮----
# Render has no durable local disk. A hostless PostgreSQL URI may fall
# back to a Unix socket or PGHOST; an omitted database may select a
# default database. Neither is the existing persistent Neon store.
database_url_error = (
⋮----
parsed_database_url = urlsplit(database_url)
database_host = parsed_database_url.hostname
database_port = parsed_database_url.port
⋮----
port = str(os.environ.get("PORT") or "8787").strip()
⋮----
runtime_dir = Path(os.environ.get("PRODUCTION_OS_RUNTIME_DIR") or "/tmp/production-os")
# Reject a symlink before touching the directory: a redirected runtime
# location must not receive even hashed authentication material.
⋮----
auth_path = runtime_dir / "auth.json"
payload = json.dumps(
# Publish the credential hashes through an atomic, owner-only file.
# Writing directly to auth.json first can follow an existing symlink
# and expose/truncate another file before chmod has run.
pending_path = None
⋮----
pending_path = Path(pending.name)
⋮----
argv = [
```

## File: verify-render-cutover.py
```python
#!/usr/bin/env python3
"""Read-only HTTP gate for the Production-OS Render migration.

This gate cannot prove that the old Render service is durably suspended:
that requires checking Render's service state independently before cutover.
No credential is ever sent to the legacy URL or printed to stdout/stderr.
"""
⋮----
NEW_URL = "https://production-os-control-plane.onrender.com"
LEGACY_URL = "https://production-os1.onrender.com"
READ_LIMIT = 8192
⋮----
class NoRedirect(urllib.request.HTTPRedirectHandler)
⋮----
def redirect_request(self, req, fp, code, msg, headers, newurl)
⋮----
def validated_origin(raw: str) -> str
⋮----
value = str(raw).strip().rstrip("/")
parsed = urlsplit(value)
loopback = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
⋮----
_ = parsed.port
⋮----
"""Return sanitized (HTTP status, bounded JSON) without raising network errors."""
headers = {"Accept": "application/json", "User-Agent": "production-os-cutover-check"}
⋮----
request = urllib.request.Request(
opener = urllib.request.build_opener(NoRedirect())
⋮----
raw = response.read(READ_LIMIT + 1)
⋮----
data = json.loads(raw)
⋮----
data = None
⋮----
# Do not expose HTTP error bodies, Location headers or auth credentials.
⋮----
def check_new(origin: str, *, attempts: int, interval: float, timeout: float) -> bool
⋮----
def check_legacy(origin: str, *, attempts: int, interval: float, timeout: float) -> bool
⋮----
# A Render Free instance may initially return 503 and then wake into a
# healthy, DB-connected controller. One 503 is not evidence of isolation.
⋮----
missing = [key for key, value in (
⋮----
def main(argv: list[str] | None = None) -> int
⋮----
parser = argparse.ArgumentParser(description=__doc__)
⋮----
args = parser.parse_args(argv)
⋮----
new = validated_origin(args.new_url)
legacy = validated_origin(args.legacy_url)
⋮----
# Check both endpoints regardless of readiness result: the old controller
# can still be live when the intended new service is failing.
new_ok = check_new(new, attempts=args.attempts, interval=args.interval,
legacy_ok = check_legacy(legacy, attempts=args.attempts, interval=args.interval,
auth_ok = True
⋮----
auth_ok = check_auth(
⋮----
auth_ok = False
```
