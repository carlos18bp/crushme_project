# Functional QA Audit - 2026-08-20

## Verdict

**YELLOW.** The test platform and every authored spec are executable and clean,
but functional coverage is not complete enough for promotion.

The canonical conductor reports:

```text
covered=4 partial=16 junk_only=0 unvalidated=0 missing=36
outcomes=56/56 negative_case_gaps=1 gate_errors=0 gate_warnings=0
```

## Executable Inventory

| Layer | Files | Test declarations | Runtime |
|---|---:|---:|---|
| Backend behavior | 18 | 49 | pytest + isolated SQLite |
| Frontend unit | 7 | 18 | Jest |
| Frontend E2E | 11 | 21 | Playwright + guarded SQLite |

Six historical Python scripts outside `backend/crushme_app/tests/` are not
counted as behavior coverage.

## Work Completed

- Built a 56-outcome flow registry from real routes, views, stores, and APIs.
- Added deterministic E2E users, recipient, address, catalog, cart, and payment
  fixtures guarded against production-grade databases.
- Covered 20 unique UI flows across auth, catalog, cart, checkout, payment
  status, navigation, public pages, and wishlist creation.
- Added backend regression coverage for auth/security, uploads, payment
  integrity, discounts, currency, external services, tasks, settings, and data
  guards.
- Added unit coverage for auth, cart, currency, payment, product, HTTP refresh,
  and alert behavior.
- Ran verifier and auditor roles for each authored batch; final verdict is KEEP
  for all eight tests in the last critical batch and its shared helper.

## Final Critical Batch

Commit `d2be38f` covers:

- `auth-verify-email` invalid-code error
- `auth-logout` protected-route enforcement
- `cart-checkout-validation` successful navigation
- `checkout-shipping-details` incomplete-form block
- `checkout-paypal` create/capture contract and success UI
- `checkout-wompi` provider failure UI
- `checkout-gift-recipient` recipient integrity in the payment payload
- `wishlist-create` real persistence plus asserted cleanup

The cart/wishlist batch was healed without retries or sleeps: setup moved from
the noisy Home view to a static Navbar host, navigation observation is installed
before the click, cold lazy-route actions have a bounded 20-second timeout, and
wishlist text stays in the requested locale so unrelated offline translation
does not contaminate the scenario.

## Verification Evidence

| Check | Result |
|---|---|
| Canonical `qa-agent.sh --verify` on final four specs | 0 errors, 0 warnings |
| Frontend unit batch | 7 suites, 18 tests passed |
| Auth + checkout Playwright batch | 6 passed |
| Cart + wishlist Playwright batch | 6 passed in 58.0s; cleanup DELETE 200 |
| Final test-quality pre-commit | Pass |
| Canonical QA read-out | 0 junk-only, 0 unvalidated, 36 missing |
| Project AI catalogs | Claude 35/35, Codex 35/35, Windsurf 32/32; no project drift |
| PR #3 partitioned CI | 6/6 jobs passed |
| Production data/runtime | Not accessed or modified |

## Remaining Work

Thirty-six flows remain missing. Critical examples include catalog search,
wishlist item management and shared gifting, profile update/crush verification,
order/gift history, and public diary profiles. High-priority gaps also remain in
password recovery UI, locale switching, product filtering/variation/favorites,
discount UI, public wishlist search, profile media/favorites, reviews, and admin.

One negative outcome class is still absent. PR #3's complete partitioned CI is
green; it must run again after future QA authoring. The full suite was
intentionally not run locally under the project execution policy.

## Promotion Decision

Wave 4 remains in progress. Do not promote lifecycle or merge the release into
`main` until the missing flow worklist, negative-case gap, and integration CI
are green. DNS, staging certification, credential rotation, restore rehearsal,
performance headroom, and the production observation window remain separate
blocking gates.
