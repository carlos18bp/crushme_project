# Tasks Plan — CrushMe

## Active Tasks

- [ ] Execute `docs/MODERNIZATION_ROADMAP.md` waves 1-6 on `release/crushme-modernization`
- [ ] Rotate the exposed production database credential before lifecycle promotion
- [ ] Establish isolated staging at `crushme.projectapp.co` after DNS is provisioned

## Backlog

### Testing
- [ ] Write backend test suite (views, models, serializers, services, commands)
- [ ] Write frontend unit tests (Pinia stores, composables, utilities)
- [ ] Write frontend E2E tests (user flows: auth, products, cart, checkout, wishlists)

### Tech Debt
- [x] Verify Argos dependency reachability; retain CTranslate2/PyTorch chain and isolate Stanza behind MiniSBD
- [ ] Consider splitting `crushme_app` if it grows further

## Completed

- [x] Add `modernizing` lifecycle and isolated work coordinate
- [x] Synchronize Claude, Codex, and Windsurf baselines/skills
- [x] Add hermetic test/staging settings and fake-data guardrails
- [x] Remove generated artifacts, dead frontend files, and tracked secret file
