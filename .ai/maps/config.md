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
auth.example.json
policy.example.json
repository-catalog.json
workflow.example.json
```

# Files

## File: auth.example.json
```json
{
  "tokens": [
    {
      "name": "dashboard",
      "role": "viewer",
      "sha256": "<sha256-of-token>"
    },
    {
      "name": "worker-1",
      "role": "worker",
      "sha256": "<sha256-of-token>"
    },
    {
      "name": "operator",
      "role": "operator",
      "sha256": "<sha256-of-token>"
    }
  ]
}
```

## File: policy.example.json
```json
{
  "defaults": {
    "max_risk_class": "critical",
    "approval_required_from": "high",
    "allowed_worker_classes": ["python", "node", "android"],
    "freeze_timezone": "Europe/Paris",
    "freeze_windows": [
      {
        "days": ["fri", "sat", "sun"],
        "start": "18:00",
        "end": "08:00"
      }
    ],
    "freeze_risk_classes": ["high", "critical"],
    "require_branch_protection_for": ["high", "critical"],
    "auto_quarantine_after_failures": 3,
    "budgets": {
      "tokens": 1000000,
      "cost": 20,
      "minutes": 600
    },
    "slo": {
      "max_runtime_minutes": 120,
      "max_attempts": 5,
      "max_consecutive_failures": 3
    }
  },
  "portfolio_budgets": {
    "tokens": 5000000,
    "cost": 100,
    "minutes": 3000
  },
  "repositories": [
    {
      "match": "dbrckk/deadline-zero",
      "approval_required_from": "critical",
      "allowed_worker_classes": ["android"],
      "budgets": {
        "tokens": 1500000,
        "minutes": 900
      }
    },
    {
      "match": "dbrckk/ai-dev-server",
      "allowed_worker_classes": ["python", "node"]
    }
  ]
}
```

## File: repository-catalog.json
```json
{
  "schema_version": "production-os/repository-catalog/v1",
  "owner": "dbrckk",
  "repositories": [
    {
      "full_name": "dbrckk/xtts2-hf",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/coqui-XTTS-colab",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/TTS",
      "private": false,
      "archived": false,
      "default_branch": "dev",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/video-site",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/Drackkie-artist",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/Drackkie",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/deal-finder-backend",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/glitchprice-finder",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/Finders",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/page-agent-mobile",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/openclaw-render",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/TrendPulse-",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/tube",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/FTMO",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/personavid-ai",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/Applio",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/viral-android-game",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/deadline-zero",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/zero-to-empire",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/Who-are-you",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/ai-dev-server",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/Jumpy",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/xbow-perso",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/star-list",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/Ai-trading",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/Production-OS",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/zombie-apk",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/repo-standards",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/repo-brain",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/asset-forge",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/vibecheck-android",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/alt-other-lives",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/Colab",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    },
    {
      "full_name": "dbrckk/chaos-survival-roblox",
      "private": false,
      "archived": false,
      "default_branch": "main",
      "pushed_at": null
    }
  ]
}
```

## File: workflow.example.json
```json
{
  "name": "android-release",
  "repository": "dbrckk/deadline-zero",
  "metadata": {
    "purpose": "Example fan-out/fan-in production workflow"
  },
  "tasks": [
    {
      "task_id": "build",
      "title": "Build debug and release artifacts",
      "priority": 100,
      "max_attempts": 2,
      "estimated_minutes": 8,
      "payload": {
        "required_capabilities": [
          "android"
        ],
        "handoff": {
          "task": "Build debug and release artifacts",
          "constraints": {
            "verify_before_completion": true
          }
        }
      }
    },
    {
      "task_id": "unit-tests",
      "title": "Run unit tests",
      "dependencies": [
        "build"
      ],
      "priority": 90,
      "max_attempts": 2,
      "estimated_minutes": 5,
      "payload": {
        "required_capabilities": [
          "android"
        ]
      }
    },
    {
      "task_id": "lint",
      "title": "Run Android lint",
      "dependencies": [
        "build"
      ],
      "priority": 80,
      "max_attempts": 2,
      "estimated_minutes": 4,
      "payload": {
        "required_capabilities": [
          "android"
        ]
      }
    },
    {
      "task_id": "package",
      "title": "Package release candidate",
      "dependencies": [
        "unit-tests",
        "lint"
      ],
      "priority": 70,
      "max_attempts": 1,
      "estimated_minutes": 3,
      "payload": {
        "required_capabilities": [
          "android"
        ]
      }
    }
  ]
}
```
