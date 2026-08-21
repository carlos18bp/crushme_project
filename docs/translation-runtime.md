# CPU-Only Translation Runtime

## Runtime Contract

CrushMe keeps ES/EN translation offline. Application code calls the existing
`TranslationService`, which sends translation-only requests through
`/run/crushme-translation/translation.sock`. The local
`crushme-translation.service` owns the models so Gunicorn and Huey never load
them into their cgroups.

The unit deliberately does not load Django's `.env`: it receives only the
non-secret socket, model path, and log-level configuration. Keep the matching
application socket and model values explicit in the production `.env`.

When `TRANSLATION_ENGINE=ctranslate2_cpu`, `/api/health/` checks the daemon's
engine identity and confirms that Torch is not loaded. The unit is part of the
web service lifecycle, so the standard web restart also reloads daemon code.

The daemon is isolated in `backend/venv_translation`. Its exact runtime
dependencies are in `backend/requirements-translation.txt`; Torch, Stanza,
spaCy, ONNX Runtime, CUDA, and NVIDIA packages are prohibited there. The
service hardcodes CTranslate2 `device=cpu`, `compute_type=int8`, one inter-op
thread, and one intra-op thread.

The runtime installer verifies the exact package allowlist and rejects any
importable heavyweight engine. Model downloads use a disposable Hugging Face
cache inside the build directory, so source weights do not remain on the VPS.

## Model Provenance

The models are Apache-2.0 OPUS-MT releases from Helsinki-NLP:

| Pair | Source | Pinned revision |
|---|---|---|
| ES -> EN | `Helsinki-NLP/opus-mt-es-en` | `c96e2c5399ebfae4fc43d9669556b9afa74bb69d` |
| EN -> ES | `Helsinki-NLP/opus-mt-en-es` | `5bc4493d463cf000c1f0b50f8d56886a392ed4ab` |

`translation_manifest.py` pins every converted runtime file by SHA-256. The
build environment contains Torch only while converting source weights and is
deleted afterward. Models and build environments are never committed.

## Build And Install

```bash
# Build reproducible static-int8 artifacts outside the runtime.
bash scripts/translation/build-models.sh /tmp/crushme-models

# Install the minimal runtime and reject Torch contamination.
bash scripts/translation/install-runtime.sh

# Copy a verified model bundle into the configured shared directory.
cd backend
source venv_cpu/bin/activate
python manage.py install_translation_models --source-dir /tmp/crushme-models
python manage.py install_translation_models --check
```

The default production model directory is
`~/.local/share/crushme/translation-models`. It is reproducible and does not
belong in database/media backups.

## Stage-1 Rollout

1. Create and restore-test fresh database/media backups; preserve the current
   commit, `.env`, units, staticfiles, and venv inventory.
2. Build and verify models, install `venv_translation`, and install/verify the
   new systemd unit before changing application settings.
3. Set `TRANSLATION_ENGINE=ctranslate2_cpu`, restart the translation daemon,
   then restart web and Huey. Existing cached translations remain unchanged.
4. Run focused tests, public ES/EN smoke checks, journals, post-deploy checks,
   and `python3 scripts/operations/translation_runtime_probe.py`.
5. Observe 48 hours and at least one representative WooCommerce sync. Require
   zero OOM events, restart loops, translation errors, and API regressions.

Rollback during this window is explicit: set `TRANSLATION_ENGINE=argos`,
restart web/Huey, then stop `crushme-translation.service` after those dependent
units have restarted. The application never falls back automatically to Argos
because an unplanned fallback could load Torch inside an already constrained
web/worker cgroup.

## Stage-2 Retirement

Only after the stage-1 observation passes:

- remove Argos, Torch, Stanza, spaCy, MiniSBD, and proven orphan dependencies;
- change the `TranslatedContent.translation_engine` model default only after
  the Argos rollback path has been retired;
- remove `ARGOS_*` and the PyTorch package index;
- recreate the main backend environment as `backend/venv`, switch all units and
  fleet metadata, then remove `venv_cpu` after rollback verification;
- delete the old Argos model directory after verifying the CTranslate2 bundle;
- rerun `pip check`, vulnerability audits, focused QA, restore rehearsal,
  systemd validation, public smoke checks, and capacity gates.

Measured authoring baseline on 2026-08-20: 158 MB for both static-int8 models,
233 MB for the isolated runtime, and 156 MiB hot daemon RSS with two threads.
A production cold start on 2026-08-21 peaked at 200.5 MiB after charging 71.4
MiB of model file cache to the cgroup. The limits are therefore
`MemoryHigh=240M`, `MemoryMax=320M`, and `CPUQuota=40%`: runtime consumption is
unchanged while the measured cold-start peak retains 37% hard-limit headroom.
