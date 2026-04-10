# CrushMe — Codex AGENTS Configuration

## Project Identity

### Codex Runtime Surfaces
- **Primary instructions**: `AGENTS.md` (root scope) + `backend/AGENTS.md` + `frontend/AGENTS.md`
- **Skills (canonical)**: `.agents/skills/<skill>/SKILL.md` + `agents/openai.yaml`
- **Project config**: `.codex/config.toml`

- **Name**: CrushMe
- **Domain**: `crushme.com.co` / `www.crushme.com.co`
- **Stack**: Django 5.1.5 + DRF (backend) / Vue 3.5 + Vite 7 SPA (frontend) / MySQL 8 / Redis / Huey
- **Server path**: `/home/ryzepeck/webapps/crushme_project`
- **Services**: `gunicorn.service` (Gunicorn), `gunicorn.socket`, `crushme-huey.service`
- **Settings module**: `DJANGO_SETTINGS_MODULE=crushme_project.settings`; production mode activated by `DJANGO_ENV=production` in `.env`
- **Nginx**: `/etc/nginx/sites-available/crushme_project`
- **Static**: `/home/ryzepeck/webapps/crushme_project/backend/staticfiles/`
- **Media**: `/home/ryzepeck/webapps/crushme_project/backend/media/`
- **Resource limits**: MemoryMax=650M, CPUQuota=40%, OOMScoreAdjust=300

---

## General Rules

These should be respected ALWAYS:
1. Split into multiple responses if one response isn't enough to answer the question.
2. IMPROVEMENTS and FURTHER PROGRESSIONS:
- S1: Suggest ways to improve code stability or scalability.
- S2: Offer strategies to enhance performance or security.
- S3: Recommend methods for improving readability or maintainability.
- Recommend areas for further investigation

---

## Security Rules — OWASP / Secrets / Input Validation

### Secrets and Environment Variables

NEVER hardcode secrets. Always use environment variables.

```python
# ✅ Django — use env vars
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DATABASE_URL = os.environ['DATABASE_URL']
STRIPE_API_KEY = os.environ['STRIPE_SECRET_KEY']

# ❌ NEVER do this
SECRET_KEY = 'django-insecure-abc123xyz'
DATABASE_URL = 'mysql://root:password123@localhost/mydb'
```

```typescript
// ✅ Next.js / Nuxt — use env vars
const apiUrl = process.env.NEXT_PUBLIC_API_URL
const secretKey = process.env.API_SECRET_KEY  // server-only, no NEXT_PUBLIC_ prefix

// Nuxt
const config = useRuntimeConfig()
const apiKey = config.apiSecret  // server only
const publicUrl = config.public.apiBase  // client safe

// ❌ NEVER do this
const API_KEY = 'sk-live-abc123xyz'
fetch('https://api.stripe.com/v1/charges', {
  headers: { Authorization: 'Bearer sk-live-abc123xyz' }
})
```

### .env rules

- `.env` files MUST be in `.gitignore`. Always verify before committing
- Use `.env.example` with placeholder values for documentation
- Separate env files per environment: `.env.local`, `.env.staging`, `.env.production`
- Server secrets (API keys, DB passwords) NEVER go in client-side env vars
- In Next.js: only `NEXT_PUBLIC_*` vars are exposed to the browser
- In Nuxt: only `runtimeConfig.public.*` is exposed to the browser

### Input Validation

NEVER trust user input. Validate on both server AND client.

#### Django/DRF

```python
# ✅ Serializer validates input
class OrderSerializer(serializers.Serializer):
    email = serializers.EmailField()
    quantity = serializers.IntegerField(min_value=1, max_value=100)
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError('Product not found')
        return value

# ❌ Using raw request data
def create_order(request):
    product_id = request.data['product_id']  # no validation
    Order.objects.create(product_id=product_id)  # SQL injection risk
```

#### React/Vue

```typescript
// ✅ Validate before sending
import { z } from 'zod'

const orderSchema = z.object({
  email: z.string().email(),
  quantity: z.number().int().min(1).max(100),
  productId: z.number().int().positive(),
})

const handleSubmit = (data: unknown) => {
  const result = orderSchema.safeParse(data)
  if (!result.success) {
    setErrors(result.error.flatten().fieldErrors)
    return
  }
  await submitOrder(result.data)
}
```

### SQL Injection Prevention

```python
# ✅ Django ORM — always safe
users = User.objects.filter(email=user_input)

# ✅ If raw SQL is needed, use parameterized queries
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM users WHERE email = %s", [user_input])

# ❌ NEVER interpolate user input into SQL
cursor.execute(f"SELECT * FROM users WHERE email = '{user_input}'")
```

### XSS Prevention

```typescript
// ✅ React auto-escapes by default — JSX is safe
return <p>{userInput}</p>

// ✅ Vue auto-escapes with {{ }}
// <p>{{ userInput }}</p>

// ❌ NEVER use dangerouslySetInnerHTML with user input
return <div dangerouslySetInnerHTML={{ __html: userInput }} />

// ❌ NEVER use v-html with user input
// <div v-html="userInput" />

// If you MUST render HTML, sanitize first
import DOMPurify from 'dompurify'
const clean = DOMPurify.sanitize(userInput)
```

### CSRF Protection

```python
# ✅ Django — CSRF middleware is on by default, keep it
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',  # NEVER remove
    ...
]

# ✅ DRF — use SessionAuthentication or JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# ❌ NEVER disable CSRF globally
@csrf_exempt  # only for webhooks from external services with signature verification
```

### Authentication and Authorization

```python
# ✅ Always check permissions
from rest_framework.permissions import IsAuthenticated

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own orders
        return Order.objects.filter(user=self.request.user)
```

### Sensitive Data Exposure

```python
# ✅ Exclude sensitive fields from serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']
        # password, tokens, internal IDs are excluded

# ❌ Exposing everything
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # leaks password hash, tokens, etc.
```

### HTTP Security Headers (Django)

```python
# settings.py — enable all security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = True  # in production
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
```

### Dependency Security

- Run `pip audit` (Python) and `npm audit` (Node) regularly
- Never use `*` for dependency versions — pin exact versions
- Review new dependencies before adding them
- Keep dependencies updated, especially security patches

### File Upload Security

```python
# ✅ Validate file type and size
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_upload(file):
    ext = Path(file.name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f'File type {ext} not allowed')
    if file.size > MAX_FILE_SIZE:
        raise ValidationError('File too large')
```

### Security Checklist — Before Every Deployment

- [ ] No secrets in code or git history
- [ ] `.env` is in `.gitignore`
- [ ] All user input is validated (server + client)
- [ ] No raw SQL with user input
- [ ] No `dangerouslySetInnerHTML` / `v-html` with user data
- [ ] CSRF protection enabled
- [ ] Authentication required on all sensitive endpoints
- [ ] Serializers exclude sensitive fields
- [ ] Security headers configured
- [ ] `pip audit` / `npm audit` clean
- [ ] File uploads validated
- [ ] DEBUG = False in production
- [ ] ALLOWED_HOSTS configured properly

---

## Memory Bank System

CrushMe maintains a Memory Bank under `docs/methodology/` and `tasks/`:

**Methodology files** (`docs/methodology/`):
- `product_requirement_docs.md` — Product vision, core features, non-functional requirements
- `architecture.md` — System overview, backend/frontend architecture, infrastructure
- `technical.md` — Technology stack, key decisions, environment setup, deployment
- `error-documentation.md` — Known and resolved issues
- `lessons-learned.md` — Patterns, preferences, tech debt

**Task tracking** (`tasks/`):
- `tasks_plan.md` — Active tasks, backlog, completed
- `active_context.md` — Current focus and recent changes

**Standards files** (`docs/`):
- `DJANGO_VUE_ARCHITECTURE_STANDARD.md`, `GLOBAL_RULES_GUIDELINES.md`, `TESTING_QUALITY_STANDARDS.md`, `BACKEND_AND_FRONTEND_COVERAGE_REPORT_STANDARD.md`, `E2E_FLOW_COVERAGE_REPORT_STANDARD.md`

Use the `methodology-setup` skill to refresh memory files when project structure changes materially.

---

## Directory Structure

```mermaid
flowchart TD
    Root[Project Root]
    Root --> Backend[backend/ — Django + DRF]
    Root --> Frontend[frontend/ — Vue 3 + Vite SPA]
    Root --> Emails[emails/ — bilingual MJML email templates]
    Root --> Docs[docs/ — standards & guides]
    Root --> Scripts[scripts/]
    Root --> AgentSkills[.agents/skills/]

    Backend --> BCrushApp[crushme_app/ — single business app]
    Backend --> BCrushProj[crushme_project/ — Django project module]
    Backend --> BAttachments[django_attachments/ — gallery library]
    Backend --> BVenvCpu[venv_cpu/ — PyTorch CPU build venv]
    Backend --> BMedia[media/ + staticfiles/]

    BCrushApp --> Models[models/ — User, Product, Cart, Order, WishList, Review, etc.]
    BCrushApp --> Views[views/ — FBV with @api_view: auth, product, cart, order, wishlist, payment, etc.]
    BCrushApp --> Services[services/ — email, translation, woocommerce, paypal, wompi]
    BCrushApp --> Tests[tests/ — pytest]

    Frontend --> FSrc[src/]
    FSrc --> FViews[views/ — Home, Login, Register, Products, Detail, Checkout, Profile, Wishlist]
    FSrc --> FComponents[components/]
    FSrc --> FStores[stores/modules/ — Pinia + persisted: auth, product, cart, order, wishlist, profile, payment, currency, i18n, crush, review, contact]
    FSrc --> FComposables[composables/ — useAlert, useCart, useCheckout, useNotifications]
    FSrc --> FServices[services/ — request_http.js: single HTTP client with CSRF + JWT]
    FSrc --> FRouter[router/ — vue-router 4 with locale prefixes]
    FSrc --> FLocales[locales/ — vue-i18n EN/ES]
    Frontend --> FTest[test/ — Jest unit specs]
    Frontend --> FE2E[e2e/ — Playwright]

    AgentSkills --> SkillSet[plan, implement, debug, deploy-and-check, git-commit, etc.]
```

**Important paths**:
- The Python venv lives at `backend/venv_cpu/` (PyTorch CPU build), **not** `backend/venv/`. Activate with `cd backend && source venv_cpu/bin/activate`.
- The systemd unit is named `gunicorn.service` (not `crushme_project.service`) — this is a quirk of this deployment.
- The systemd socket binds to `/run/gunicorn.sock`.

---

## Testing Rules

### Execution Constraints

- **Never run the full test suite** — always specify files.
- **Maximum per execution**: 20 tests per batch, 3 commands per cycle.
- **Backend**: `cd backend && source venv_cpu/bin/activate && pytest crushme_app/tests/path/to/test_file.py -v`. Note the venv is `venv_cpu` (PyTorch CPU build), not `venv`.
- **Frontend unit (Jest)**: `cd frontend && npm test -- path/to/file.spec.js`
- **Frontend E2E (Playwright)**: `cd frontend && npx playwright test e2e/path/to/spec.js` — max 2 files per invocation. Use `E2E_REUSE_SERVER=1` when a Vite dev server is already running.

### Quality Standards

Full reference: `docs/TESTING_QUALITY_STANDARDS.md`

- Each test verifies **ONE specific behavior**
- **No conjunctions** in test names — split into separate tests
- Assert **observable outcomes** (status codes, DB state, rendered UI)
- **No conditionals** in test body — use parameterization
- Follow **AAA pattern**: Arrange → Act → Assert
- Mock only at **system boundaries** (external APIs, clock, email)

---

## Lessons Learned — CrushMe

### Architecture Patterns

#### Single business app: `crushme_app`
- All ~25 models, all views, all serializers, all services live in `backend/crushme_app/`.
- Views are split into per-resource modules: `auth_views.py`, `product_views.py`, `cart_views.py`, `order_views.py`, `wishlist_views.py`, `wishlist_woocommerce_views.py`, `review_views.py`, `paypal_order_views.py`, `wompi_order_views.py`, `woocommerce_local_views.py`, `favorite_product_views.py`, `contact_views.py`, `feed_views.py`, `geolocation_views.py`, `discount_views.py`, `user_search_views.py`, `category_views.py`, `gift_views.py`.

#### Service layer is real here
- `crushme_app/services/` holds the bulk of the business logic:
  - `email_service.py` — SMTP (GoDaddy), template rendering.
  - `translation_service.py` — **offline** ES↔EN translation via `argostranslate` (no external API calls). Auto-detects target locale from `Accept-Language`.
  - `translation_batch_service.py` — bulk translation used by the WooCommerce sync.
  - `woocommerce_service.py` + `woocommerce_sync_service.py` — pull product catalog from a remote WooCommerce store, mirror it locally, sync variants.
  - `woocommerce_order_service.py` — convert local `Order` rows back into WooCommerce orders.
  - `paypal_service.py` — PayPal SDK integration, payment processing.
  - `wompi_service.py` — Wompi (Colombian gateway) integration, webhook handlers.

#### Dual auth strategy
- **Public API** (`/api/auth/...`) uses **JWT via SimpleJWT** with `ACCESS_TOKEN_LIFETIME=30d`, `REFRESH_TOKEN_LIFETIME=60d`, refresh rotation enabled.
- **Django admin** (`/admin/`) uses session + CSRF.
- The frontend uses a **single HTTP client** (`src/services/request_http.js`) that sends both `X-CSRFToken` and `Authorization: Bearer` headers, with automatic token refresh on 401.

#### WooCommerce mirror + offline translation
- The product catalog is **mirrored** from a remote WooCommerce store via `WooCommerceProduct` and `WooCommerceProductVariation` models.
- A `CategoryPriceMargin` model lets the user override pricing per category.
- When products are synced, **all text content is translated offline** via `argostranslate` and cached in a `TranslatedContent` model. This is what `translation_batch_service.py` does.
- There is **no real-time MT** — translations happen at sync time and are persisted.

#### Custom user model with crush verification
- `User` extends `AbstractUser` with email-as-username and a "crush verification" workflow (`is_crush`, `crush_verification_status`, `crush_verified_at`). This is a domain feature: users can verify themselves as "crushes" eligible to receive gifted wishlists.
- `GuestUser` model supports anonymous checkout via session.

#### Dual payment gateways
- **PayPal** for international payments (USD) — see `paypal_order_views.py` + `paypal_service.py`.
- **Wompi** for Colombian payments (COP) — see `wompi_order_views.py` + `wompi_service.py`.
- Both have webhook endpoints that update `Order.status` based on payment events.

#### Wishlists are public and shareable
- `WishList` rows have a UUID and a public-facing share URL.
- A logged-out visitor can view and gift a wishlist without an account (a `GuestUser` is created on checkout).
- `FavoriteWishList` lets users bookmark other people's wishlists.

#### Conditional Silk profiling
- `django-silk` is gated by `ENABLE_SILK=True`. Off by default.

#### Huey periodic tasks
- `scheduled_backup` — Sun 03:00 UTC (DB + media, weekly retention 4).
- `silk_garbage_collection` — daily 03:30 UTC (no-op when Silk is off).
- `weekly_slow_queries_report` — Tue 07:00 UTC.
- `silk_reports_cleanup` — 1st of month 05:30 UTC.

### Code Style & Conventions

#### Backend: 100% function-based views
- Every API view in `crushme_app/*_views.py` uses the `@api_view` decorator.
- Pattern: deserialize → `serializer.is_valid(raise_exception=True)` → `service_call()` (when applicable) → `Response(...)`.
- Never convert to CBV/`APIView`/`ViewSets` unless explicitly requested.

#### Frontend: single HTTP client with CSRF + JWT
- All API requests go through `frontend/src/services/request_http.js` — a single Axios wrapper that sends both `X-CSRFToken` and `Authorization: Bearer` headers, injects `Accept-Language` and `X-Currency`, and handles automatic JWT refresh on 401 responses.
- Exported helpers: `get_request`, `create_request`, `update_request`, `patch_request`, `delete_request`, `upload_request`.
- There is no separate `usePlatformApi.js` composable.

#### Frontend: Pinia stores (mixed API styles) + persisted state
- Most Pinia stores use the **setup/Composition API** pattern (`defineStore('name', () => { ... })`): authStore, cartStore, crushStore, currencyStore, orderStore, paymentStore, productStore, profileStore, wishlistStore.
- A few stores use the **Options API** pattern (`defineStore('name', { state, actions })`): i18nStore, reviewStore, contactStore.
- `pinia-plugin-persistedstate` persists relevant slices (auth, cart, currency) to `localStorage`.
- All 12 stores: `authStore`, `productStore`, `cartStore`, `orderStore`, `wishlistStore`, `profileStore`, `paymentStore`, `currencyStore`, `i18nStore`, `crushStore`, `reviewStore`, `contactStore`.

#### Naming
- Pinia store files: camelCase (`authStore.js`, `productStore.js`, `cartStore.js`).
- Component files: PascalCase (`HomeView.vue`, `LoginView.vue`, `CheckoutView.vue`).
- Backend modules: snake_case.

#### i18n
- `vue-i18n@9.14` with locale files in `frontend/src/locales/`.
- The `i18nStore` Pinia store toggles the active locale.
- Frontend strings go through `t('key')`. Product/blog content from the backend is **already translated** at sync time (via `translation_service.py`); the frontend just picks up the localized field.

### Development Workflow

#### venv lives at `backend/venv_cpu/`
```bash
cd backend && source venv_cpu/bin/activate
```
This is the **PyTorch CPU build venv** — not a regular `venv/`. PyTorch is currently installed but **unused** in code (legacy or future ML feature).

#### Huey immediate mode in dev
- `HUEY['immediate'] = True` in dev settings — tasks run synchronously, no Redis/worker required.
- In prod, Huey runs via `crushme-huey.service` against Redis db 2.

#### Frontend dev server
```bash
cd frontend && npm install && npm run dev   # Vite, default :5173
```

### Production Deployment

See `.agents/skills/deploy-and-check/SKILL.md` for the canonical sequence. Note the systemd quirks:
- The Gunicorn unit is named **`gunicorn.service`** (not `crushme_project.service`).
- The Huey unit is `crushme-huey.service`.
- The socket is at `/run/gunicorn.sock`.

Deploy summary:
1. `git pull origin main`
2. Backend: `cd backend && source venv_cpu/bin/activate && pip install -r requirements.txt && python manage.py migrate`
3. Frontend: `cd frontend && npm install && npm run build`
4. Backend: `python manage.py collectstatic --noinput`
5. Restart: `sudo systemctl restart gunicorn && sudo systemctl restart crushme-huey`
6. Verify: `bash /home/ryzepeck/webapps/ops/vps/scripts/deployment/post-deploy-check.sh crushme_project`

### Testing Insights

- **Backend**: pytest with `backend/pytest.ini`. Tests live in `backend/crushme_app/tests/`.
- **Frontend unit**: Jest with `jest.config.cjs`.
- **Frontend E2E**: Playwright with `playwright.config.js`.
- Quality gate: `scripts/test_quality_gate.py`, multi-suite runner: `scripts/run-tests-all-suites.py`.

### Tech Debt / Things to Be Aware Of

- **PyTorch is in `requirements.txt` but unused** — `torch`, `transformers`, `sklearn` do not appear in any application code. The `venv_cpu` and the 650M memory limit exist because of PyTorch's footprint, even though it isn't actively imported.
- `stanza` and `ctranslate2` are also installed without active integration (probably future translation upgrades).
- The single `crushme_app` is large; consider splitting if it grows further.

---

## Error Documentation — CrushMe

### Known Issues

_No known issues recorded yet. When a bug is discovered that warrants long-lived documentation, add it here with the format:_

```
#### [KNOWN-NNN] short title
- **Context**: ...
- **Workaround**: ...
```

### Resolved Issues

_No resolved issues recorded yet. When fixing a non-trivial bug, document the root cause and resolution here:_

```
#### [ERR-NNN] short title
- ...
- **Resolution**: ...
```
