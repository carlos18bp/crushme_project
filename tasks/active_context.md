# Active Context — CrushMe

## Current Focus
AI tools ecosystem audit and methodology setup (April 2026).

## Recent Changes
- Audited and corrected all AI guidance files against real codebase (21 files fixed)
- Key corrections: store API pattern, HTTP client architecture, Nuxt→Vue references, projectapp residuals, venv path
- Initialized Memory Bank (`docs/methodology/` + `tasks/`)

## Active Decisions
- Single HTTP client pattern (`request_http.js`) is the established approach — no plans to split
- Mixed Pinia store API styles (setup + Options) are acceptable — match existing style when editing
- PyTorch remains installed but unused (tech debt, not blocking)
