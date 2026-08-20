# Active Context - CrushMe

## Current Focus

Wave-based modernization of the existing production project. There is no
CrushMe staging environment and none will be created for this program.

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

Land Wave 0, then create Wave 1 from the resulting `main` and synchronize the
three AI ecosystems against the canonical toolkit and Vue scaffold.
