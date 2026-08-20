# Tasks Plan - CrushMe

## Active Tasks

- [ ] Close the 36 missing QA flows and one negative-case gap.
- [ ] Run complete partitioned CI on a PR targeting `release/crushme-modernization`.
- [ ] Rotate the exposed production database credential and remediate history.
- [ ] Provision DNS and deploy isolated staging at `crushme.projectapp.co`.
- [ ] Prove staging TLS, health, backup restore, observability, translation load,
  payment sandbox behavior, and at least 30% resource headroom.
- [ ] Complete Wave 6 certification before lifecycle promotion.

## Backlog

- [ ] Plan deferred major upgrades for Vite, Vue I18n, Vue Router, Pinia,
  Flowbite, Django, Huey, Redis, Gunicorn, and other compatibility-bound pins.
- [ ] Re-evaluate the Stanza advisory monthly and remove the mitigation when
  Argos supports Stanza 1.12.2 or newer.
- [ ] Consider splitting `crushme_app` only if module growth makes ownership or
  test isolation materially worse.

## Completed

- [x] Add lifecycle `modernizing`, release branch, and isolated work coordinate.
- [x] Synchronize Claude, Codex, Windsurf, skills, QA roles, and instructions.
- [x] Run repository cleanup and refresh verified Memory Bank documentation.
- [x] Apply vulnerability/dependency updates and application hardening.
- [x] Add hermetic test settings, fake-data guards, deterministic fixtures, and CI.
- [x] Add ESLint and synchronized strict test-quality tooling.
- [x] Version fail-fast staging settings and operational artifacts without deploy.
- [x] Establish 18 backend behavior files, 7 frontend-unit files, and 11 E2E specs.
- [x] Validate all 21 authored E2E cases live with no draft or junk-only flow.
