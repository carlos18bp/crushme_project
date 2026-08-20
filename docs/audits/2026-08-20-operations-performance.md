# Wave 5 Operations And Performance Audit

Date: 2026-08-20 UTC

Coordinate: production-only `crushme_project`

Release: PR #13, commit `79a25e4`

## Verdict

**GREEN.** Wave 5 was installed in production on 2026-08-20. Fresh recovery
artifacts, restore rehearsal, dependency-aware health, translation behavior,
runtime configuration, logs, timers, and measured capacity all passed. The
release did not change CrushMe business rules, data models, payments, catalog
behavior, or public URLs.

## Measured Baseline

A read-only representative run against production completed eight requests at
concurrency one with zero HTTP failures and 223.4 ms p95 latency. CPU headroom
was 77.0% and host memory available was 45.7%, but the web cgroup peaked at
486.3 MiB of its 650 MiB limit: 25.2% memory headroom, below the required 30%.

Process maps traced the excess memory to the eager import of Argos Translate,
which loaded CTranslate2, ONNX, Torch, and NumPy into ordinary Gunicorn workers.
The application now imports Argos only when an offline translation is actually
required. Spanish traffic and worker startup retain the existing response
behavior without loading that engine.

## Implemented Controls

| Control | Result |
|---|---|
| Dependency-aware `/api/health/` | App, MySQL, and Redis contract covered by four behavior tests |
| Lazy translation loading | Import, bypass, and translation paths covered by three behavior tests |
| Focused backend tests | 7 passed |
| Test Quality Gate | 100/100, zero findings |
| Django system check | Passed |
| Migration drift | No changes detected |
| systemd syntax | Web, socket, Huey, backup service, and timer passed `systemd-analyze verify` |
| systemd hardening | Web, Huey, and backup score 3.4 `OK` offline |
| Fleet configuration parity | Project/runtime copies match the fleet standard; journald-only logging is explicit |
| Repository hygiene | Obsolete duplicate Nginx/Gunicorn files removed; canonical copies remain under `scripts/` |

## Operational Design

- `crushme-dbbackup.timer` creates daily compressed database and media backups
  independently from Huey, with persistent scheduling and four-copy retention.
- Gunicorn, Huey, and backup output is centralized in journald; the obsolete
  file logger and legacy logrotate target are retired.
- Nginx serves collected static files, keeps hashed assets immutable, prevents
  SPA HTML caching, limits uploads to the validated business maximum, and
  bounds upstream requests to the Gunicorn timeout.
- `scripts/operations/runtime_headroom.py` applies a guarded read-only load and
  fails unless HTTP, latency, service memory/CPU, and host memory gates pass.
- Hardened systemd units preserve the existing 650 MiB web and 450 MiB Huey
  limits instead of concealing the eager-import problem with larger limits.

## Production Acceptance Evidence

| Gate | Production result |
|---|---|
| Fresh database backup | `default-srv571894-2026-08-20-143603.dump.gz`, gzip integrity passed |
| Fresh media backup | `srv571894-2026-08-20-143613.tar.gz`, archive integrity passed |
| Rollback point | `/var/backups/crushme_project/wave5-deploy-20260820T143651Z`, prior commit `98adad8` plus environment, runtime configuration, and static files |
| Configuration validation | Candidate systemd units and `nginx -t` passed before reload |
| Public health | HTTP 200 with application, MySQL, and Redis all `ok` |
| Translation behavior | A genuine English category request returned translated content |
| Restore rehearsal | 1/1 weekly database, 1/1 media, and 1/1 fresh daily database restored; disposable resources removed |
| Capacity | 32 requests, 0 failures, 231.2 ms p95, 81.1% web-memory headroom, 75.5% CPU headroom, 63.0% host memory available |
| Runtime checks | Web and Huey active, daily timer active, warning journals empty |
| Fleet post-deploy | 14 pass, 0 fail, 2 non-blocking warnings: root disk usage and a known valid empty generated CSS asset |

Wave 5 is complete. Wave 6 owns dependency revalidation, final certification,
and the real 24-hour production observation window. No staging clone is part of
either wave, and all rollback artifacts remain retained until observation
closes.
