# Active Context - CrushMe

## Current Focus

Wave 2 repository cleanup and hermetic development/test foundations. Wave 1
aligned all AI ecosystems without changing production runtime behavior.

## Current Coordinate

- Runtime: `/home/ryzepeck/webapps/crushme_project` on `main`.
- Authoring: temporary worktree under `/home/ryzepeck/webapps/.wt/`.
- Domain: `crushme.com.co` and `www.crushme.com.co`.
- Data: MySQL `crushme`, Redis cache DB 1, Huey DB 2.

## Active Decisions

- Release one PR per wave directly to `main`.
- Reuse the old modernization branch only as reviewed source material.
- Preserve function-based DRF views and the single frontend HTTP client.
- Preserve existing business behavior unless a verified security defect requires
  a compatibility-conscious correction.
- Never run QA or fake-data commands against production data.

## Next Gate

Audit and land Wave 2 from the resulting `main`: verified repository cleanup,
isolated test settings, deterministic fake-data guards, partitioned CI, lint,
and the test-quality platform.
