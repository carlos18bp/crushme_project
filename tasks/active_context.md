# Active Context — CrushMe

## Current Focus
Modernization program, waves 1-3 (August 2026).

## Recent Changes
- Registered CrushMe as `modernizing` with an isolated staging work coordinate
- Synchronized Claude 35/35, Codex 35/35, and Windsurf 32/32 skills
- Added isolated test/staging settings and non-bypassable fake-data guards
- Removed 306 generated, unsafe, redundant, or orphaned tracked files

## Active Decisions
- Single HTTP client pattern (`request_http.js`) is the established approach — no plans to split
- Mixed Pinia store API styles (setup + Options) are acceptable — match existing style when editing
- Argos uses CTranslate2; its Stanza dependency pulls PyTorch CPU, while MiniSBD is enforced as the safe runtime path
- Production remains on `main`; modernization work must not change runtime until gates pass
- A credential exposed in Git history must be rotated before promotion
- Permanent staging is blocked until `crushme.projectapp.co` resolves

## Next Gates

- Vulnerability/dependency audit and secret remediation plan
- CI dependency installation plus focused backend/frontend checks
- QA flow map and initial behavior coverage
- Staging deploy, smoke tests, and observation window
