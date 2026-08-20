# Wave 5 Operations And Performance Audit

Date: 2026-08-20 UTC

Coordinate: production-only `crushme_project`

Release branch: `ops/20082026-crushme-wave-5`

## Verdict

The release candidate is ready for controlled production installation. It does
not change CrushMe business rules, data models, payments, catalog behavior, or
public URLs. Production acceptance remains conditional on the post-merge
backup, restore, health, capacity, and observation controls below.

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

## Candidate Controls

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
| Fleet configuration parity | Project/runtime copies match toolkit commit `79ec286` |
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

## Production Acceptance

The controlled deploy must record all of the following before Wave 5 can be
declared complete:

- Fresh database and media backups with archive integrity checks.
- Rollback copies of the prior commit, environment, static files, Nginx, and
  systemd configuration.
- Successful systemd and Nginx validation before reload.
- HTTP 200 health payload with both MySQL and Redis at `ok`.
- A genuine English translation request confirming Argos behavior remains
  available.
- Daily backup service execution plus a restore into a disposable database and
  media extraction into a disposable directory.
- Representative load with at least 30% web memory and CPU headroom, at most
  two-second p95, and no HTTP failures.
- Green fleet post-deploy check and clean service journals.

Wave 6 owns the final certification report and the real 24-hour production
observation window. No staging clone is part of either wave.
