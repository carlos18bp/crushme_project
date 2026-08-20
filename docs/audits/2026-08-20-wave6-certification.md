# Wave 6 Certification Report

Date: 2026-08-20 UTC

Coordinate: production-only `crushme_project`

Runtime release: PR #14, commit `1d476d8`

## Verdict

**CONDITIONALLY GREEN FOR CRUSHME; PROMOTION HELD.** The immediate Wave 6
certification is complete: the project-specific AI ecosystem, dependency
audit, focused regression tests, required CI, controlled deployment, restore
rehearsal, public smoke checks, service health, and capacity gate passed.

The fleet lifecycle remains `modernizing`, not `active`. Promotion requires a
full 24 hours of healthy production operation after the final runtime restart.
Observation started at **2026-08-20 15:13:06 UTC** and cannot close before
**2026-08-21 15:13:06 UTC**.

## Certification Evidence

| Surface | Result |
|---|---|
| Codex and Claude Code baseline | Zero project baseline drift; 35/35 project skills present with zero hash drift; no retired ecosystem directories; credential checks passed |
| QA read-out | 56/56 outcomes mapped: 4 covered, 16 partial, 36 missing, 0 junk-only, 0 unvalidated, 0 exempt, and 1 negative-case gap; gate errors 0, infrastructure errors 0, warnings 0 |
| Frontend dependencies | `npm audit` reported 0 vulnerabilities; only intentionally deferred framework majors remain outdated |
| Backend requirements | Five reachable secure transitives pinned; resolver, `pip check`, and requirement audit passed except the documented mitigated Stanza advisory |
| Focused regression | 8 tests passed: 4 health, 1 Argos/MiniSBD mitigation, and 3 translation-service behaviors |
| Required project CI | All four PR #14 jobs passed: backend, frontend unit/build, hermetic E2E, and MySQL migration/concurrent refresh |
| Deployment checks | Django deploy check, migration drift, no-op migration, frontend build, static collection, systemd verification, and Nginx syntax passed |
| Public contracts | Health reported application/MySQL/Redis `ok`; English category translation and PayPal/Wompi public configuration contracts passed |
| Runtime capacity | 32 requests, 0 failures, 179.8 ms p95, 81.2% web-memory headroom, 76.3% CPU headroom, and 60.8% host memory available |
| Fleet post-deploy | 14 pass, 0 fail, 2 known non-blocking warnings; service warning journals were empty and the daily backup timer was active |
| Restore rehearsal | 1/1 weekly database, 1/1 media archive, and 1/1 fresh daily database restored; temporary databases and extraction directories were removed |

The QA result is intentionally not represented as complete behavioral
coverage. Its yellow classification is the explicit continuous-QA backlog,
not a certification error or an attempt to grant draft tests credit.

## Dependency Closure

The installed production environment initially reported 16 advisories across
10 packages. Reachability analysis separated current requirements from stale
site-packages left by historical installs:

- Reachable transitives were `click`, `filelock`, `idna`, `protobuf`, and
  `sentencepiece`; all five now have exact secure pins.
- `stanza==1.10.1` remains required by Argos Translate 1.11. Its vulnerable
  pipeline is unreachable because production forces MiniSBD on CPU, application
  code never creates a Stanza pipeline, and the behavior has a real-package
  regression test.
- Eighteen unreachable historical packages were removed from the production
  venv, including the unused Triton installation. Pip was updated to 26.2.1.
- Final audits of both the installed environment and `requirements.txt` report
  only the documented mitigated Stanza advisory. The PyTorch CPU local-version
  wheel remains subject to the mapping limitation documented in
  `audit-report.md`.

## Recovery And Operations

Fresh pre-deploy recovery artifacts were verified:

- Database: `default-srv571894-2026-08-20-150735.dump.gz`.
- Media: `srv571894-2026-08-20-150738.tar.gz`, 38 entries.
- Full rollback point:
  `/var/backups/crushme_project/wave6-deploy-20260820T150804Z`.
- The rollback point contains the prior commit, mode-600 environment, installed
  dependency inventory, runtime configuration, static files, full venv
  snapshot, checksums, and capacity evidence. Its checksums passed.

The fleet full audit with restore finished with 12 green phases and one yellow
phase. Fleet state verification had 237 checks OK, zero drift, and zero missing
resources, including the CrushMe contract. The two host-level warnings are
missing override files for
the unrelated `aero-meteo-mvp` and `aviation-weather-viewer-frontend` services;
therefore the host audit is correctly yellow and is not mislabeled green.

Toolkit commit `92f2d71` preserves the QA and full-audit read-outs. Its GitHub
Actions run was prevented from starting by the repository account's billing or
spending-limit state; the equivalent local configuration validators passed.
Project PR #14 CI was unaffected and fully green.

## Promotion Gate

After 2026-08-21 15:13:06 UTC, a closing review must verify the complete
observation interval rather than a point-in-time sample:

- Web and Huey stayed active without restart loops, failed units, or warning/
  error journal regressions.
- Public health and payment/translation smoke contracts still pass.
- `crushme-dbbackup.timer` ran successfully and its newest artifacts are valid.
- Capacity remains above the documented 30% service-headroom and 20% host
  memory gates.
- Production remains on clean `main`, no CrushMe staging coordinate exists,
  and no new critical/high vulnerability or AI drift appeared.

Only after those checks pass may the fleet lifecycle change from
`modernizing` to `active`. Keep all Wave 3 through Wave 6 rollback and recovery
artifacts until that decision is recorded.
