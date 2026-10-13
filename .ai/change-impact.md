# Change impact

Base: f7325526e47310f5d79412a089361b0cf06d81fd
Head: 972ef8328894d9cc1f18e7a6c7db96b5eb5b4aa1

## Changed files
- M .github/workflows/ci.yml
- A docs/asset-review-branch-guard.md
- M docs/production-readiness.md
- A docs/worktree-delivery-symlinks.md
- M integration/godot4_relocated_import_smoke.py
- M integration/real_producer_bundle_smoke.py
- M src/production_os/asset_forge.py
- M src/production_os/github_client.py
- M tests/test_asset_forge.py

## Affected areas
- .github
- docs
- integration
- src
- tests

## Related test candidates
- tests/test_asset_forge.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.
