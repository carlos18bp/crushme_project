# Active Context - CrushMe

## Current Focus

Close the production cold-start capacity finding, then continue the Wave 7
stage-1 observation without changing CrushMe business behavior.

## Current Coordinate

- Production checkout: `/home/ryzepeck/webapps/crushme_project`; deploy branch
  is `main` on `srv571894`.
- Domain: `crushme.com.co` and `www.crushme.com.co`.
- Data: MySQL `crushme`, Redis cache DB 1, Huey DB 2.
- Runtime services: `crushme_project.service`, `crushme_project.socket`,
  `crushme-huey.service`, and `crushme-translation.service`.
- QA uses only `settings_test`/`settings_e2e` with isolated SQLite. Production
  MySQL, Redis, media, domain, and environment values are never test fixtures.

## Wave State

- Three-layer QA is merged and deployed through PR #23 (`a2bc660`). CI passed
  143 backend tests, 58 frontend unit tests, 178 hermetic E2E tests, MySQL
  compatibility, standards, flow sync, and the strict quality gate.
- The flow registry is green at 64/64 covered flows with no partial,
  junk-only, unvalidated, or missing entries.
- A fresh database/media backup and root-only rollback bundle were created at
  `/var/backups/crushme_project/wave7-deploy-20260821T040537Z`; database and
  media restoration passed.
- `ctranslate2_cpu` is active in production with pinned static-int8 ES/EN
  models. The runtime has no Torch, CUDA, NVIDIA, Stanza, spaCy, or ONNX
  Runtime packages.
- Public health, ES/EN routes, Django-to-daemon translation, service journals,
  and the generic post-deploy gate are green.
- A cold restart charged 71.4 MiB of model file cache to the daemon cgroup and
  produced a 200.5 MiB peak. Process RSS stayed near 160 MiB, but the original
  256 MiB hard limit left only 21.7% headroom.
- The cold-start correction preserves `MemoryHigh=200M` for early file-cache
  reclaim and raises only `MemoryMax` to 320M. It does not change runtime
  allocation, CPU quota, threads, packages, models, or application behavior.

## Active Decisions

- Release every production change through a green PR to `main`.
- Preserve function-based DRF views, the single frontend HTTP client, and all
  established business flows.
- Never run QA, E2E, fake-data, or mutation probes against production data.
- Keep CTranslate2 isolated in `backend/venv_translation`, CPU/int8-only and
  single-threaded, with no automatic fallback into Gunicorn or Huey.
- Keep Argos/Torch CPU-only as an explicit rollback until the stage-1 gate
  closes; do not retire dependencies early.
- Treat file-cache charges as part of cold-start capacity, even when they are
  reclaimable, so the hard limit retains operational margin.
- Keep backup availability independent from Huey and retain the weekly fleet
  snapshot as a second mechanism.
- Keep lifecycle `modernizing` until observation and representative sync close.

## Next Gate

Merge and deploy the cold-start limit correction, rerun the live translation
probe with at least 25% daemon headroom, and restart the 48-hour observation
clock from that final rollout. Stage 2 requires one representative WooCommerce
sync plus zero translation errors, OOM events, restart loops, or API regressions.
