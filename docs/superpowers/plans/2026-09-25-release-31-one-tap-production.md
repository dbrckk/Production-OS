# Release 31 — One-tap Production

## Goal

Make the primary mobile workflow simply:

- choose repository
- enter instruction
- launch

## Server contract

POST /v1/dashboard/launch

Input:

- repository
- instruction

Server-owned defaults:

- token_budget = 30000
- agent_preference = auto

The endpoint creates a persistent Managed Project before dispatch.

## UX

- one-tap launch card appears before technical navigation
- no per-run agent or token controls on the primary surface
- advanced Managed Project controls remain available but collapsed
- browser refresh/closure does not lose the launched project
- offline worker state remains queued rather than discarded

## Access

- operator required
- viewer/worker cannot launch

## Completion gate

- API regression coverage
- UI regression coverage
- full CI green
- Python 3.11 and 3.12 green
- final diff review clean
