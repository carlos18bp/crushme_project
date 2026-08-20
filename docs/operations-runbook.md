# CrushMe Operations Runbook

## Runtime Contract

CrushMe has one runtime coordinate:

| Item | Production value |
|---|---|
| Checkout | `/home/ryzepeck/webapps/crushme_project` on `main` |
| Domain | `crushme.com.co`, `www.crushme.com.co` |
| Database | MySQL `crushme` |
| Cache / queue | Redis DB 1 / DB 2 |
| Web / worker | `crushme_project.service` / `crushme-huey.service` |
| Socket | `crushme_project.socket` -> `/run/gunicorn.sock` |
| Daily backup | `crushme-dbbackup.timer` |

Temporary Git worktrees are authoring surfaces only. They never receive a
database, domain, environment file, socket, or service.

## Versioned Configuration

The project copies below mirror the deployable fleet configuration:

- `scripts/nginx/crushme.conf`
- `scripts/systemd/crushme_project.service`
- `scripts/systemd/crushme_project.socket`
- `scripts/systemd/crushme_project.override.conf`
- `scripts/systemd/huey.service`
- `scripts/systemd/crushme-huey.override.conf`
- `scripts/systemd/crushme-dbbackup.service`
- `scripts/systemd/crushme-dbbackup.timer`

There are no alternate Nginx or Gunicorn files under `backend/`. Before
installing a release, preserve the active `/etc` files, compare them with these
templates, run `systemd-analyze verify` and `nginx -t`, and keep the rollback
copies through the observation window.

## Backup Topology

Backups do not depend on Huey:

- `crushme-dbbackup.timer` runs daily at 02:10 UTC with up to five minutes of
  randomized delay. It writes compressed MySQL and media backups to
  `/var/backups/crushme_project` and retains four copies. The backup directory
  is owner-only (`0700`) and Django storage creates every archive and metadata
  file as owner-only (`0600`).
- `vps-backup.timer` creates the independent weekly fleet snapshot, including
  database and media, under `/home/ryzepeck/backups/vps`.
- `vps-backup-restore-test.timer` performs the monthly fleet restore test.

Manual verification after installation:

```bash
sudo systemctl start crushme-dbbackup.service
systemctl status crushme-dbbackup.service --no-pager
systemctl list-timers crushme-dbbackup.timer --all --no-pager
journalctl -u crushme-dbbackup.service --since today --no-pager
```

Never restore over `crushme`. A rehearsal must create a disposable database,
restore the latest dump, verify tables/data, and drop the disposable database
even when validation fails. The canonical fleet rehearsal is:

```bash
sudo bash /home/ryzepeck/webapps/vps-ops-toolkit/scripts/maintenance/test-backup-restore.sh
```

The same rehearsal extracts media into a temporary directory and compares its
contents; listing a tarball alone is not sufficient evidence.

## Health And Logs

`GET /api/health/` checks the application, MySQL, and Redis. It returns HTTP
200 only when all three are ready, HTTP 503 otherwise, and never includes an
exception or credential in its payload.

Web, Huey, and backup output is centralized in journald:

```bash
journalctl -u crushme_project.service --since '30 minutes ago' --no-pager
journalctl -u crushme-huey.service --since '30 minutes ago' --no-pager
journalctl -u crushme-dbbackup.service --since '2 days ago' --no-pager
```

The fleet registry declares `logrotate: false` for CrushMe. No
`/etc/logrotate.d/crushme_project*` file should exist; fleet verification treats
an unexpected file as drift because these services do not write application
log files.

The fleet healthcheck and weekly reports remain the alerting/retention layer.
Silk is disabled by default and may be enabled only for a bounded diagnostic
window; its reports are not a substitute for service logs.

## Capacity Gate

Run the read-only representative load after the service has warmed up:

```bash
python3 scripts/operations/runtime_headroom.py \
  --requests 32 \
  --concurrency 1 \
  --min-headroom 30
```

The probe uses only public GET flows and refuses concurrency above four. The
gate requires no HTTP failures, p95 at or below two seconds, at least 30%
headroom against both the service memory limit and CPU quota, and at least 20%
host memory available. Preserve its JSON output in the wave audit.

Argos is imported lazily: Spanish requests and ordinary worker startup do not
load Torch/ONNX. A request that genuinely needs offline translation still uses
the same Argos models and may increase one worker's memory; the existing
resource limits and worker recycling remain in force.

## Controlled Release And Rollback

Before a runtime release:

1. Confirm clean production `main` and green PR checks.
2. Create fresh database and media backups and verify archive integrity.
3. Preserve the current commit, environment, `/etc` units/site, and
   `staticfiles`.
4. Install code/dependencies, run checks/migrations/build/collectstatic.
5. Validate candidate units and Nginx before daemon reload.
6. Restart web/Huey, enable the backup timer, and run post-deploy, health,
   logs, restore, and capacity gates.

Rollback uses the preserved commit and `/etc` files, rebuilds static assets,
reloads systemd/Nginx, and restarts services. Database/media restore is only
needed when a release changed data incompatibly; never restore merely to roll
back application code.
