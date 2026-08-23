<!-- fleet-base:begin v=2 -->
# CLAUDE.md — CrushMe (`crushme_project`)

Esta seccion es la **base comun del fleet** y se sincroniza desde
`vps-ops-toolkit/workflows/.claude/base/CLAUDE.md.tmpl`. No editar manualmente:
los cambios se pierden en el proximo sync. Para customizar este proyecto, usar
la seccion `project-specific` mas abajo.

## Convencion de lenguaje

- Codigo, identificadores y nombres de variable: **ingles**.
- Mensajes de commit: **ingles** (Conventional Commits).
- Docs operativos, skills y reportes: **espanol** (terminos tecnicos en ingles donde son de uso corriente).
- Mensajes de error visibles al usuario final: idioma del proyecto.

<!-- session-start-protocol:begin -->
## Session Start Protocol

Al inicio de **cada sesión y antes de editar archivos**, ubicate: el hook te dice DÓNDE arrancaste y esta sección qué se hace ahí. Razón: N sesiones en paralelo comparten el clon principal, que es el checkout del servicio/deploy — editarlo o "sincronizarlo" con stash/rebase pisa el trabajo de los demás.

**Flujo:**
1. Un hook `SessionStart` (definido en `.claude/settings.json`) ejecuta `git fetch + git status` read-only y te inyecta `[session-start] <repo> @ <rama> | behind=N ahead=M dirty=D | tree=main-clone|worktree:<slug>`.
2. **Arrancaste en el clon principal (`~/webapps/<repo>`)** → NO invoques `/git-sync`, digan lo que digan `behind`/`dirty`. Acá sólo hacés lectura y `git fetch` (lista canónica completa en la sección 1 del protocolo siguiente). `dirty>0` es trabajo de otra sesión: reportalo como anomalía y no lo toques (ni stash, ni reset, ni checkout — el hook guard lo bloquea igual). Para modificar archivos, creá tu worktree de sesión desde `origin/<BASE>` (sección 5 del bloque siguiente) y ENTRÁ en él.
3. **Arrancaste en / entraste a tu worktree (`~/webapps/.wt/<repo>/<slug>`)** → `behind>0` contra su upstream ⇒ invocá `/git-sync` (absorbe la base movida con merge, nunca con rebase). `dirty>0` es tu propio trabajo en curso; `ahead>0` se resuelve con el commit+push normal.
4. **Sesión de sólo lectura** (revisar, diagnosticar, responder) → quedate en el clon principal; no hace falta worktree.

**Importante:** Nunca uses `git pull --force`, `git reset --hard` ni stash automático; en el clon principal de un repo del fleet, ni siquiera `/git-sync` — ahí sólo lectura + `fetch` (lista canónica en la sección 1). La rama de deploy del clon principal la mueve el operador/deploy, no una sesión.
<!-- session-start-protocol:end -->

<!-- git-branch-protocol:begin -->
## Reglas de trabajo con Git: ramas, worktrees y commits (protocolo por sesión)

**Nunca hagas commits directamente sobre `main`/`master`, sobre una rama release, ni sobre la rama de OTRA sesión, y nunca mergees: el merge no es de la sesión.**

**El modelo es 1 sesión = 1 rama = 1 worktree = 1 PR, y el trabajo se ENTREGA como PR abierto con CI verde (sección 10).** Cada sesión crea SU rama al arrancar trabajo, en SU git worktree, y abre el PR en el primer push con dueño e intención declarados. Está PROHIBIDO reutilizar la rama de otra sesión o acumular trabajo de varias tareas en una rama compartida — eso produce ramas con N dueños, archivos contaminados con hunks ajenos y merges imposibles de ordenar (medido en el fleet el 2026-08-16). El drenaje ordenado de vuelta a la base lo hace `/merge-queue` o el operador a mano: una sesión nunca mergea su propio PR. Antes de cualquier `git commit`, seguí este protocolo:

### 0. (Fleet) Confirmá la coordenada: host + base de integración

Si este repo pertenece al fleet `vps-ops-toolkit` (existe `~/webapps/vps-ops-toolkit/projects.yml`), la **fuente de verdad de dónde se trabaja y sobre qué BASE se corta tu rama** es `projects.yml` validado contra los PRs abiertos:

```bash
# pre-entry: corre en el clon principal, antes de EnterWorktree
OPS=~/webapps/vps-ops-toolkit
RESOLVER="$OPS/scripts/maintenance/resolve-work-coordinate.sh"
# OJO worktrees: el nombre del proyecto sale del git-common-dir (el clon
# principal) — en un worktree, el toplevel es ~/webapps/.wt/<repo>/<slug>.
PROJ=$(basename "$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")")
[[ -x "$RESOLVER" ]] && bash "$RESOLVER" --check "$PROJ"   # imprime vps_work, resolved_branch, pr_state, host_status, matches_yml
```

Si YA estás dentro de tu worktree (Claude, después de `EnterWorktree`) ese bloque compuesto se rechaza: pedí el mismo dato —y el resto de la coordenada— con **un** comando simple, que además resuelve el proyecto solo:

```bash
bash ~/webapps/vps-ops-toolkit/scripts/maintenance/session-worktree.sh status
```

- **`host_status=wrong-host`** → **PARÁ**. El trabajo de este proyecto va en OTRO clon (el `vps_work` que imprime el resolver — p.ej. kore se trabaja en el clon de `vps-projectapp-staging`, no en el de producción). Avisá al operador antes de tocar nada acá.
- **`BASE` de tu rama de sesión**: con `pr_state=single` (repo con release activa) la base es **`resolved_branch`** — tu rama sale DE la release y tu PR apunta A la release (modelo stacked; la release mantiene su propio PR hacia `main`/`master`, gateado por `release_merge`). Con `prod-direct`/`no-pr`, la base es la default (`main`/`master`). **NUNCA hagas checkout de la release ni commitees en ella** — la release sólo recibe trabajo vía PRs de sesión.
- **`matches_yml=no`** (el candidato a release difiere del registrado, p.ej. la release anterior se mergeó y hay otra) → avisá al operador; puede que haya que refrescar `projects.yml` con `bash "$RESOLVER" --apply "$PROJ"` en el toolkit.
- **`branch_deploy_status=yml-stale`** (el clon acá ya está en la rama nueva y el `branch:` de projects.yml quedó viejo) → avisá y refrescá el yml con `bash "$RESOLVER" --fix "$PROJ"` (desde el toolkit). NUNCA hagas checkout de la rama vieja del yml sobre el clon. Si es `unbacked` o `server_status` marca host ajeno → derivar a `migrate-project` / revisión manual, sin auto.
- **Sin toolkit, o el proyecto no está en `projects.yml`** → base = `main`/`master` y seguí con la sección 1.

### 1. Dónde estás parado determina qué hacés

```bash
git rev-parse --show-toplevel
```

- **Bajo `~/webapps/.wt/<repo>/<slug>`** → estás en un worktree de sesión. **TUYA** = la rama la creaste vos en esta sesión, o en un turno anterior de la MISMA sesión; en duda, `session-worktree.sh list` o la línea `Sesión:` del body del PR. Si es TUYA: commiteá (sección 8). Si es de otra sesión: no toques nada — creá el tuyo (sección 2).
- **En el clon principal (`~/webapps/<repo>`)** → **acá no se edita ni se commitea**: es el checkout del servicio/deploy. **Lista canónica de lo permitido acá — la única del protocolo, el resto de las secciones apunta a esta:** `git status/log/diff/fetch`, `git worktree list/add/remove` (operan sobre el registro de worktrees, no sobre el checkout) y `git pull --ff-only` (el único pull que el hook no deniega; igual la rama de deploy la mueve el operador/deploy, no una sesión). Todo lo demás está prohibido: `git checkout`/`switch`, `git commit`/`add`, `git stash`, `git reset`, `git merge`/`rebase`, `git pull` sin `--ff-only` y borrar `node_modules`. Un hook `PreToolUse` deniega esas operaciones —y `Edit`/`Write`— en el clon principal de un repo del fleet; **no** intercepta las escrituras que el shell hace por otras vías (`sed -i`, heredocs, redirecciones) y no corre donde no esté instalado: la regla aplica igual. Creá tu worktree (sección 2) y trabajá allá.
- **Guard del cwd para las herramientas de archivos**: `Read`/`Edit`/`Write` resuelven las rutas contra el cwd de la sesión, y el archivo de instrucciones del repo (`CLAUDE.md`/`AGENTS.md`) se descubre desde ahí — si te quedás en el clon principal editás el clon principal aunque "tengas" un worktree. Por eso, una vez creado, ENTRÁ en él:
  - **Claude Code:** herramienta nativa `EnterWorktree` con `path=$HOME/webapps/.wt/<repo>/<slug>` — funciona con un worktree creado por `git worktree add` y la primera vez pide aprobación porque la ruta está fuera de `.claude/worktrees/`: aceptala. Desde ahí toda ruta relativa y todo comando corren en el worktree. `ExitWorktree` **no** borra un worktree entrado por `path=`; el retiro es `session-worktree.sh remove <slug>` (sección 5).
  - **Codex:** no tiene worktrees nativos — `cd` al worktree y ejecutá TODO comando posterior con ese directorio como workdir; las rutas absolutas apuntan al worktree, nunca a `~/webapps/<repo>`.
  Antes de escribir, confirmá que `git rev-parse --show-toplevel` cae bajo `~/webapps/.wt/`.
- **Post-`EnterWorktree` (Claude): UN comando simple por llamada.** Adentro de un worktree nativo, Claude inspecciona el **string literal** del comando antes de correrlo y rechaza dos familias enteras — se cae el bloque completo, no la línea:
  - **Forma** ("too complex to verify that it stays inside the worktree"): sustitución de comando `$(...)`, expansión de llaves `{a,b}`, un `for`/`while`, o un heredoc cuyo cuerpo tenga sustitución. **Sí** pasan el comando simple, el pipe `|`, las cadenas `&&`/`||` de comandos simples y `gh … -q '<jq>'`.
  - **Destino**: `git -C <el clon principal de este worktree>` y `cd <el clon principal>` (el subshell no ayuda). Leer el clon principal (`ls`, `cat`, `Read`) sí se permite, y `git -C <OTRO repo>` también. `Edit`/`Write` sobre una ruta del clon principal se rechazan: editá la copia del worktree.
  Consecuencia práctica: **no computes valores en bash**. Pedí UN registro con `bash ~/webapps/vps-ops-toolkit/scripts/maintenance/session-worktree.sh status` — imprime `project repo main_clone worktree branch default_branch resolved_branch registered_branch deploy_branch open_pr pr_state_coord release_merge host_status base pr_number pr_state pr_url ci dirty unpushed upstream in_base age_h locked verdict` — leelo y escribí esos valores **literales** en las llamadas siguientes (`gh pr create --base <base>`, `gh pr checks <n>`, …). Los bloques que corren ANTES de entrar (sección 5: crear la rama y el worktree desde el clon principal) no tienen este límite.
- **Regla compartida**: toda skill que escriba en el repo (tests, docs, configs, memoria de metodología, reportes) hereda esto — escribe en el worktree de la sesión y, si no existe, lo crea primero (sección 5). Ninguna skill necesita repetirlo.

### 2. Arrancando trabajo nuevo: SIEMPRE tu propia rama + worktree

No busques ramas abiertas para reutilizar — **cada sesión corta la suya** desde la BASE de la sección 0 (comandos exactos en la sección 5). Una rama de otra sesión nunca se reutiliza, ni "para un cambio chico"; la única excepción es un pedido explícito del operador. Si tu sesión YA tiene su rama/worktree de un turno anterior, seguí usándolos — pero entrá al worktree primero (sección 1): un turno nuevo arranca en el clon principal. Tu trabajo en curso se acumula en TU rama.

### 3. Formato obligatorio del nombre de rama

`<prefijo>/<DDMMYYYY>-<descripcion-corta>`

- **`<prefijo>`** según el tipo de cambio:
  - `feat` — nueva funcionalidad
  - `fix` — corrección de bug
  - `docs` — cambios en documentación
  - `refactor` — refactorización sin cambio funcional
  - `test` — añadir o modificar tests
  - `chore` — mantenimiento (dependencias, configs)
  - `style` — formato/estilo, sin cambio de lógica
  - `perf` — mejoras de rendimiento
  - `ci` — cambios en workflows o pipelines
  - `hotfix` — corrección urgente en producción

- **`<DDMMYYYY>`** debe ser la fecha actual del sistema obtenida con `date +%d%m%Y`. Nunca la asumas ni la inventes.

- **`<descripcion-corta>`** en kebab-case, máximo 5 palabras, en inglés o español según el idioma del proyecto.

### 4. Ejemplos de nombres válidos

- `feat/15052026-login-google-oauth`
- `fix/15052026-typo-readme`
- `refactor/15052026-extract-user-service`
- `docs/15052026-update-deploy-guide`
- `chore/15052026-bump-django-version`

### 5. Comandos exactos a ejecutar

```bash
# pre-entry: corre en el clon principal, antes de EnterWorktree
# 1. Fecha del día (no asumirla) + identidad del repo y la base (sección 0)
TODAY=$(date +%d%m%Y)
REPO=$(basename "$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")")
BASE=<base de integración de la sección 0>       # release si pr_state=single; main/master si no
SLUG=<descripcion-corta>

# 2a. PREFERIDO (elegí 2a O 2b, nunca las dos): el helper resuelve la base, crea
#     el worktree, enlaza los .env gitignoreados del clon principal e imprime
#     worktree= branch= base= pr_base= pr_state= — corré esto desde cualquier cwd
#     dentro del repo; fuera de él, agregá --project=<nombre>
bash "$HOME/webapps/vps-ops-toolkit/scripts/maintenance/session-worktree.sh" create <prefijo> "$SLUG"

# 2b. Manual (sin toolkit), desde el clon principal ~/webapps/<repo>
git fetch origin "$BASE" --quiet
git worktree add "$HOME/webapps/.wt/${REPO}/${SLUG}" -b <prefijo>/${TODAY}-${SLUG} "origin/${BASE}"

# 3. ENTRAR al worktree (sección 1). Claude Code: herramienta nativa, NO un
#    comando bash → EnterWorktree path=$HOME/webapps/.wt/<repo>/<slug>
cd "$HOME/webapps/.wt/${REPO}/${SLUG}"   # sólo Codex — en Claude ya entraste con EnterWorktree

# 4. Guard: confirmar que estás bajo .wt/ ANTES de escribir. En Claude un `cd` de
#    bash NO mueve el cwd de la sesión: el guard sólo vale después de EnterWorktree.
git rev-parse --show-toplevel   # debe caer bajo ~/webapps/.wt/ — si no, frená

# 5. Recién entonces hacer add y commit
git add <archivos>
git commit -m "<mensaje siguiendo conventional commits>"
```

- `npm ci` / instalar dependencias **dentro del worktree** sólo si tu tarea necesita frontend (build/tests). Jamás toques el `node_modules`, los refs o los stashes de otro tree.
- Los `.env` gitignoreados NO viajan con `git worktree add`: el helper los enlaza desde el clon principal; sin helper, `ln -s ~/webapps/<repo>/backend/.env "$HOME/webapps/.wt/${REPO}/${SLUG}/backend/.env"`. Nunca los copies a una ruta versionada.
- `backend/venv` NO se enlaza nunca: corré los tests con `~/webapps/<repo>/backend/venv/bin/python`.
- **Nunca corras `manage.py migrate` (ni ningún comando que escriba la base de datos) desde el worktree**: el `backend/.env` enlazado apunta a la base de PRODUCCIÓN del clon principal. En el worktree sólo `makemigrations`, `makemigrations --check --dry-run`, `sqlmigrate` y los tests con settings de test; las migraciones las aplica el deploy.
- El worktree se retira cuando su PR YA mergeó: lo hace `/all-in-base` al verificar, y los huérfanos los junta el gc del operador (`session-worktree.sh gc --apply`). Si quedás trabado: `bash "$HOME/webapps/vps-ops-toolkit/scripts/maintenance/session-worktree.sh" remove <slug>` — sin `--force`, nunca (el helper no lo tiene, y el hook deniega `git worktree remove --force` sobre cualquier worktree que no sea `queue-*`).

### 6. Inferencia del prefijo

Determina el prefijo a partir del contenido de los cambios:
- Archivos nuevos que añaden features → `feat`
- Cambios que arreglan comportamiento roto → `fix`
- Solo cambios en `*.md`, comentarios o JSDoc → `docs`
- Cambios en `package.json`, `requirements.txt`, configs → `chore`
- Cambios en `.github/workflows/*` → `ci`
- Archivos `*test*` / `*spec*` modificados o añadidos → `test`
- Reorganización sin alterar comportamiento → `refactor`

Si hay ambigüedad, pregunta al usuario una sola vez antes de crear la rama.

### 7. Excepciones

- Lo permitido en el clon principal es exactamente la lista canónica de la sección 1; no hay excepciones además de esa lista.
- Si el usuario explícitamente pide quedarse en el clon principal para revisar algo sin commitear, respeta esa intención: es una sesión de sólo lectura y no habilita `checkout` ni edición.
- Dentro de TU rama de sesión, los cambios de tu tarea se acumulan como commits sucesivos — no abras una segunda rama por "sub-cambio" de la MISMA tarea. Trabajo NUEVO no relacionado en la misma sesión: preguntale al operador si va como commit en tu rama o como rama de sesión nueva.
- **Convención: 1 sesión = 1 rama = 1 worktree = 1 PR; N PRs de sesión abiertos en paralelo son estado normal.** El límite duro es de RELEASES: máximo 1 PR de release (base=default) por repo, identificado por `branch_working` en projects.yml.
- Sincronizar tu rama: `/git-sync` **desde tu worktree** (en el clon principal no se sincroniza nada — Session Start Protocol) — una rama pusheada con PR se sincroniza contra su propio upstream y absorbe la base movida con `git merge origin/<base>`, **nunca** con rebase (el force push está denegado en el fleet).

### 8. Mensajes de commit

Sigue Conventional Commits, con el mismo prefijo de la rama cuando aplique:

```
feat: add Google OAuth login flow
fix: correct typo in deployment README
refactor: extract user validation into service
```

### 9. PR al primer push (con dueño declarado) + reporte de la URL

En el **primer `git push -u origin <rama>`** de tu rama de sesión, abrí el PR ahí mismo — no lo dejes para después: el PR es lo que le da a tu rama dueño visible, intención declarada y CI corriendo desde temprano.

Un comando por llamada, y con la BASE **literal** (post-`EnterWorktree` no hay `$(...)` que la calcule; sale del `base=` de `session-worktree.sh status` o del `pr_base=` que imprimió `create`):

```bash
git push -u origin <rama>
```
```bash
gh pr create --base <BASE de la sección 0> --fill --body "Sesión: <nombre de tu sesión (el título que le dio el operador), o el slug de la rama si no lo conocés>
Intención: <1 línea: qué entrega esta rama>

<resumen breve de los cambios>"
```

El body va como texto literal entre comillas dobles, con saltos de línea reales — **nunca** `--body "$(printf …)"`: la sustitución de comando hace que Claude rechace el `gh pr create` entero dentro de un worktree.

- Las líneas `Sesión:` y `Intención:` del body son **contrato**: `/merge-queue` las usa para saber a quién delegarle conflictos y fixes. No las omitas.
- Termina tu respuesta con la URL, etiquetada `PR URL: <url>` (si `gh` no está disponible, la URL "Create a pull request" que imprime el push, y decí que el PR quedó pendiente de abrir).
- Pushes posteriores de la misma rama: reporta la URL del PR existente (`gh pr view --json url -q .url`).
- Si por excepción se commiteó directo a `main`/`master` (sólo posible en proyectos sin esta regla), declara explícitamente: "PR URL: n/a (push directo a `main`)".
- Si hubo cambios en varios proyectos en el mismo turno, entrega una **lista** con un `PR URL:` por proyecto.
- El PR abierto con CI verde ES la entrega de la sesión: no sigue ningún merge tuyo (sección 10).

### 10. Cierre: PR abierto + CI verde, y PARÁ

**Definition of done de la sesión:** árbol limpio + rama pusheada + PR abierto (sección 9) + CI verde en ESE PR. Ahí la sesión SE DETIENE.

1. Commiteá y pusheá lo pendiente (secciones 8-9). Con `gh`: `gh pr checks <n> --watch --fail-fast=false`. `/pr-green` conduce este cierre de punta a punta.
2. CI en rojo → fix loop en TU rama (`/pr-green`): arreglá sólo lo atribuible a tu cambio, commit + push y volvé a esperar. Un gate rojo que no es de tests se reporta, no se "arregla" a ciegas.
3. CI verde → reportá `PR URL: <url>` y `CI: ✅` y **no sigas**: NO `gh pr merge`, NO `/merge-when-green`, NO tocar el clon principal, NO "dejar la base al día". El merge lo hace el orquestador (`/merge-queue`) o el operador a mano. Si la queue te delega por mensaje un conflicto o un check rojo, resolvelo en TU worktree y pusheá — la señal de resuelto es el push, no una respuesta. `/merge-when-green` es herramienta del operador (manual-only).
4. Verificación de cierre: **`/all-in-base --check-only`** responde si tu trabajo está ENTREGADO (PR verde, o ya contenido en la base) sin mutar nada. El flag no es opcional: sin el flag, `/all-in-base` delega en `/pr-green` (commit/push/PR/CI) y toca git; con el flag sólo responde. El retiro del worktree lo hace `/all-in-base` recién cuando el PR YA mergeó; con el PR abierto el worktree queda vivo (la queue puede necesitarlo).
5. `vps-ops-toolkit` es la excepción documentada (flujo trunk: commit directo a `master`, sin PR) — este protocolo no aplica ahí.
<!-- git-branch-protocol:end -->

<!-- e2e-user-flows-protocol:begin -->
## E2E User Flows Check

Cuando termines de implementar un cambio que afecte un **flujo de usuario en el frontend** — por ejemplo:
- Crear o editar un formulario (agregar/quitar campos)
- Nueva ruta, página o vista accesible al usuario
- Cambios en flujos de autenticación, checkout, onboarding, búsqueda, perfil
- Modificaciones al registro de flows E2E (`frontend/e2e/flow-definitions.json`, o los shards por-flow + docs derivados en repos con `flow_definitions_dir`)

…debes invocar la skill `e2e-user-flows-check` como **paso final** antes de reportar la implementación como completa. Esa skill audita la cobertura E2E del flujo modificado y reporta brechas/riesgos.

**Por qué:** los flujos de usuario en frontend cambian las assumptions de los tests E2E. Sin auditoría, un campo eliminado deja tests "verdes" pero inválidos, y un form nuevo queda sin cobertura.

**No aplica para:** correcciones aisladas que no cambian el flujo (typos, refactors internos, estilos puros, dependency bumps), ni cambios solo en backend que no alteren UX.

**Recordatorio automático:** un hook `Stop` revisa al cierre del turno si hay cambios uncommitted bajo `frontend/src/`, `frontend/app/`, etc., y te lo inyecta como contexto. El hook es un recordatorio, no bloqueante — la regla aplica igual aunque el hook no dispare. Tras `EnterWorktree` el hook mira el directorio de arranque y puede no ver tus cambios; la regla aplica igual.
<!-- e2e-user-flows-protocol:end -->

## Ecosistemas IA paralelos

Este proyecto tiene dos ecosistemas activos en paralelo: Claude Code (este
archivo + `.claude/`) y Codex (`AGENTS.md` + `.agents/skills/` + `.codex/config.toml`).
Ambos comparten el
mismo cuerpo de instrucciones general; el frontmatter y la estructura cambian
por ecosistema. La fuente de verdad es `vps-ops-toolkit/workflows/`.

<!-- fleet-base:end -->

<!-- project-specific:begin -->
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
CrushMe is a bilingual (ES/EN) e-commerce + wishlist-sharing platform where verified "crush" profiles can receive gifted wishlists. Built with Django 5.2.17 + DRF 3.18 (backend) and Vue 3.5.41 + Vite 7 + Pinia (frontend), backed by MySQL 8, Redis, and Huey for async tasks. Production domain: `crushme.com.co`.

## Commands
```bash
# Backend (always activate venv first — it's venv_cpu, not venv)
cd backend && source venv_cpu/bin/activate
python manage.py runserver                                    # Dev server
pytest crushme_app/tests/path/to/test_file.py -v             # Run specific tests
pytest crushme_app/tests/path/to/test_file.py::test_name -v  # Single test
python manage.py makemigrations crushme_app && python manage.py migrate
python manage.py create_fake_data                             # Seed dev data
python manage.py delete_fake_data --confirm                   # Remove seeded data
python manage.py sync_woocommerce                             # Pull products from WooCommerce

# Frontend
cd frontend && npm run dev          # Vite dev server (:5173, proxies /api/ and /media/ to :8000)
cd frontend && npm run build        # Build → ../backend/static/frontend/
cd frontend && npm test -- path/to/file.spec.js          # Jest unit test
cd frontend && npx playwright test e2e/path/to/spec.js   # Playwright E2E
# Use E2E_REUSE_SERVER=1 if Vite dev server is already running
```

## Testing Constraints
- Never run the full test suite (backend, frontend unit, or E2E).
- Maximum 20 tests per batch and 3 test commands per cycle.
- Run only the smallest slice needed for the changed behavior.
- Backend fixtures in `backend/conftest.py`: `api_client`, `user`, `admin_user`, `authenticated_client`, `admin_client`.
- Pre-commit hook: `test-quality-gate` runs on staged test files with `--semantic-rules strict`.

## Standards Contract
- Canonical development standards are the six hashed documents listed in
  `.standards-baseline.json`, sourced from Base Vue commit `c580ea8`.
- `docs/CRUSHME_ARCHITECTURE_PROFILE.md` maps generic template examples to the
  real CrushMe architecture and runtime without relaxing security or testing.
- Never edit a canonical standard only in CrushMe. Update Base Vue first, copy
  the approved file, update the manifest, and run
  `python3 scripts/check_standards_baseline.py --repo-root .`.
- Preserve the precedence and deviation rules in the project profile.

## Architecture

### Backend — Single Django App (`crushme_app`)
- **Views are 100% function-based** with `@api_view`, split per resource (`auth_views.py`, `product_views.py`, `cart_views.py`, `order_views.py`, `wishlist_views.py`, `paypal_order_views.py`, `wompi_order_views.py`, etc.). Do not convert to CBV/`APIView`/`ViewSets`.
- **Service layer is real**: business logic lives in `crushme_app/services/` (email, translation, woocommerce sync, paypal, wompi). Views are thin wrappers that call services — do not inline business rules into views.
- **Dual auth**: `/api/auth/...` uses JWT via SimpleJWT (15m access, 7d refresh, serialized rotation + blacklist, logout revocation). `/admin/` uses session + CSRF.
- **Offline translation**: a local CTranslate2 CPU-only daemon translates ES↔EN and caches sync-time results in `TranslatedContent`; Argos is stage-1 rollback only.
- **Custom `User` model**: email-as-username, crush verification fields (`is_crush`, `crush_verification_status`). `GuestUser` model supports anonymous checkout via session.
- **Two payment gateways**: PayPal (USD, international) and Wompi (COP, Colombian). Server-calculated `PaymentSession` state is authoritative; captures/webhooks must match it before updating `Order.status`.
- **WooCommerce mirror**: products are pulled from a remote WooCommerce store and mirrored locally with translated content.
- **Conditional Silk**: `django-silk` profiling is gated by `ENABLE_SILK=True` env var. Off by default.
- **Currency middleware**: custom middleware reads `x-currency` header (COP/USD) from frontend requests.

### Frontend — Vue 3 SPA
- **Pinia stores use mixed API styles** with `pinia-plugin-persistedstate`. Most stores (auth, cart, crush, currency, order, payment, product, profile, wishlist) use the **setup/Composition API** (`defineStore('name', () => { ... })`). A few (i18n, review, contact) use the **Options API**. Stores live in `src/stores/modules/`.
- **Single HTTP client**: all API requests go through `src/services/request_http.js` — an Axios wrapper that sends both `X-CSRFToken` and `Authorization: Bearer` headers, injects `Accept-Language` and `X-Currency`, and shares one guarded JWT refresh on concurrent 401 responses.
- **Locale routing**: vue-router uses `/en/...` and `/es/...` prefixes. Active locale comes from `i18nStore`.
- **Bilingual content**: product text is already translated server-side — the frontend just reads localized fields. UI strings (buttons, labels) go through `vue-i18n` locale files in `src/locales/`.
- **Currency**: `currencyStore` tracks COP/USD; `request_http.js` injects `x-currency` header on every request.
- Build output goes to `backend/static/frontend/` — do not edit files there directly.

### Environment & Settings
- Base settings: `backend/crushme_project/settings.py`. It imports `settings_dev` by default and `settings_prod` only when `DJANGO_ENV=production`.
- Pytest uses isolated `settings_test.py`; Playwright uses `settings_e2e.py`. Neither may inherit production database, Redis, email, or payment resources.
- Redis db 1 = Django cache, Redis db 2 = Huey task queue.
- Production systemd units: `crushme_project.service`, `crushme-huey.service`,
  and `crushme-translation.service`. Sockets: `/run/gunicorn.sock` and
  `/run/crushme-translation/translation.sock`.
- Service memory limits: web 650M, Huey 450M, translation 256M.

### Deployment Flow
1. `git pull origin main`
2. `pip install -r requirements.txt` + `python manage.py migrate`
3. `cd frontend && npm ci && npm run build`
4. `python manage.py collectstatic --noinput`
5. `sudo systemctl restart crushme_project crushme-huey`

### Email Templates
Bilingual MJML source templates in `emails/`, rendered HTML in `backend/email_templates/{en,es}/`. Email sending is handled by `crushme_app/services/email_service.py`.

## Working Rules
- The venv is at `backend/venv_cpu/`, not `backend/venv/`.
- Do not change old migrations; add new migrations when schema changes are required.
- Do not hardcode user-facing strings — use `vue-i18n` locale files or server-side translation.
- Do not edit files inside `backend/static/frontend/` — they are Vite build artifacts.
- Prefer existing project patterns over generic framework advice.
<!-- project-specific:end -->
