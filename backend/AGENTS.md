# Backend Rules - CrushMe Django/DRF

These instructions extend the root `AGENTS.md` for files under `backend/`.

## Architecture

- Keep the single business app, `crushme_app`, unless a separate refactor is
  explicitly approved.
- DRF endpoints use function-based views with `@api_view`. Do not convert them
  to `APIView`, generic views, or viewsets as incidental cleanup.
- Keep request parsing and response construction in views. Put reusable
  business logic in `crushme_app/services/` and input validation in serializers.
- Use the custom `crushme_app.User` model through `get_user_model()`; do not
  introduce Django's default user model.
- Use Django ORM and parameterized queries. Avoid raw SQL unless profiling
  demonstrates a concrete need.
- Preserve offline ES/EN translation during WooCommerce sync. Do not introduce
  real-time machine translation in request paths.

## Integrations

- WooCommerce is the catalog source and order destination. Keep credentials and
  API URL in environment variables.
- PayPal is the USD gateway and Wompi is the COP gateway. Production values are
  explicit; development, test, and staging must use sandbox or disabled values.
- Verify webhook signatures before changing order state. Webhook endpoints are
  the only acceptable CSRF exemptions.
- Long-running and periodic work uses Huey. Tests use `MemoryHuey`; staging and
  production use isolated Redis queues.

## Settings

- Shared settings: `crushme_project.settings`.
- Production: `DJANGO_ENV=production` with the shared module.
- Staging: `DJANGO_SETTINGS_MODULE=crushme_project.settings_staging`.
- Tests/E2E: `DJANGO_SETTINGS_MODULE=crushme_project.settings_test`.
- Never let tests inherit `backend/.env` deployment resources.
- Fake-data commands must call `ensure_fake_data_allowed()` before reading or
  mutating database rows. There is no production override flag.

## Security

- Validate all request data through serializers before service/model calls.
- Scope querysets and object lookups to the authenticated user where ownership
  applies.
- Never expose password hashes, tokens, gateway secrets, or internal payment
  metadata in serializers or logs.
- Validate uploaded file extension, MIME type, and size at the server boundary.
- Keep CSRF middleware and secure-cookie/HSTS production settings enabled.
- Add schema changes through new migrations; never rewrite applied migrations.

## Commands

```bash
cd backend
source venv_cpu/bin/activate
python manage.py check --settings=crushme_project.settings_test
pytest crushme_app/tests/path/to/test_file.py -v
python manage.py makemigrations --check --dry-run
```

The runtime venv is `backend/venv_cpu/`, not `backend/venv/`.

## Testing

- Never run the full suite. Run at most 20 tests per invocation and no more
  than three test commands per cycle.
- Tests must use `settings_test`, isolated SQLite, in-memory cache/Huey, and
  sandboxed integrations.
- One test verifies one observable behavior. Use Arrange/Act/Assert, deterministic
  data, and mocks only at system boundaries.
- Add regression coverage for authorization, payment/webhook idempotency,
  totals, wishlist privacy, and destructive command guardrails.
