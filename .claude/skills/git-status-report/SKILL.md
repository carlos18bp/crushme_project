---
name: git-status-report
description: "Muestra el estado git de los proyectos (limpio/cambios pendientes). Con --all: reporte fleet-wide (todos los VPS) + tabla de coordenada de trabajo desde projects.yml (ramas work/deploy, dónde corre/trabaja cada proyecto)."
allowed-tools: Bash, AskUserQuestion
argument-hint: "[--all-vps (todos los VPS del fleet + coordenada de trabajo; alias: --all) | --all-repos (todos los repos de este host)]"
---

Convención de flags del fleet: **`--all` = todos los VPS** (fleet-wide);
**`--all-repos` = todos los repos de ESTE host**. Ejecutar:

```bash
git-status-report              # este host: LOCAL_PROJECTS + toolkit
git-status-report --all-vps    # FLEET: coordenada de trabajo (projects.yml) + git status en TODOS los VPS (--all = alias)
git-status-report --all-repos  # este host: TODOS los repos de webapps/ (no solo LOCAL_PROJECTS). Alias legacy: --filesystem
```

## Cómo invocar este skill

Gating ([[_output-protocol]] §4): (1) flags explícitos → ejecutar directo, sin
menú; (2) intención clara por la sesión (p.ej. "¿cómo está el git del fleet?")
→ proponer el comando en una línea y esperar confirmación; (3) sin argumentos /
intención difusa → UNA sola AskUserQuestion con Q1; (4) nunca en modo
fleet/headless/cron ni dentro de un barrido.

**Q1 — Alcance** (`multiSelect: false` — modos excluyentes):

| label | description | preview |
|---|---|---|
| Proyectos de este host (Recommended) | LOCAL_PROJECTS + toolkit de este host, read-only | `bash scripts/diagnostics/git-status-report.sh` |
| --all-repos | TODOS los repos de webapps/ de ESTE host (incluye clones residuales y scaffolds) | `bash scripts/diagnostics/git-status-report.sh --all-repos` |
| --all-vps | fleet: tabla de coordenada de trabajo (projects.yml) + git status real en TODOS los VPS vía tailscale | `bash scripts/diagnostics/git-status-report.sh --all-vps` |
| Ambos ejes | acepta los dos flags, pero el fleet corre el scope default en cada VPS (--all-repos no se reenvía a los remotos) | `bash scripts/diagnostics/git-status-report.sh --all-repos --all-vps` |

**Qué NO se pregunta:** los aliases legacy `--all` (= `--all-vps`) y
`--filesystem` (= `--all-repos`) se aceptan tipeados pero no se ofrecen — el
picker sólo muestra las formas canónicas.

Pasá el argumento tal cual lo tipeó el operador (`$ARGUMENTS`) al script
`bash scripts/diagnostics/git-status-report.sh $ARGUMENTS`.

---

## Acciones disponibles

Tras el reporte, si la sesión es interactiva y NO hubo flags explícitos
(reglas de gating de [[_output-protocol]] §4), ofrecer vía AskUserQuestion:

| Opción (label) | description (costo/efecto) | preview (comando exacto) |
|---|---|---|
| --all-vps fleet + coordenada (Recommended) | git status en todos los VPS + tabla de coordenada de trabajo, read-only | `bash scripts/diagnostics/git-status-report.sh --all-vps` |
| --all-repos | TODOS los repos de webapps/ de ESTE host (incluye clones residuales/scaffolds) | `bash scripts/diagnostics/git-status-report.sh --all-repos` |
| Commitear los repos dirty | genera mensaje y commit+push por cada repo ⚠️ de este host | `/git-commit --all-repos` |
| Corregir branch: yml-stale | SÓLO cuando el reporte marcó `yml-stale`; `unbacked`/`foreign-here` van a migrate-project/manual | `bash scripts/maintenance/resolve-work-coordinate.sh --fix <proj>` |

## Output final

Reportar siguiendo [[_output-protocol]]. Multi-repo → columna `proyecto` en vez
de `Dimensión` (cada fila es un repo). Plantilla específica de `/git-status-report`:

```markdown
🟢 git-status-report OK — host <srv>, N repos limpios

| proyecto | Estado | Detalle |
|---|---|---|
| <proyecto> | ✅ | [<rama>] limpio |
| vps-ops-toolkit | ✅ | [master] limpio |
| <proyecto> | ⚠️ | [<rama>] N staged, N modificados, N sin trackear |
| <proyecto> | ℹ️ | dir ausente o sin .git en este host |
```

- Todos limpios → `🟢 git-status-report OK`. ≥1 repo con cambios sin commitear
  → `🟡 git-status-report OK con N warning(s)` (una celda ⚠️ por repo dirty).
- `dir ausente` / `sin .git` son ℹ️ (informativo, no penaliza): el repo no es
  operacional en este host.
- **`branch: drift`** (sólo en VPS): si la rama real del clon ≠ `branch:` declarado
  en `projects.yml`, la fila anexa `⚠ branch: drift (yml=<X>, real=<Y>)`. Es señal de
  que el `branch:` de deploy quedó viejo (caso típico: el clon se actualizó a la nueva
  rama release y el yml no). Clasificarlo y corregirlo:
  `bash scripts/maintenance/resolve-work-coordinate.sh --check <proyecto>` (y `--fix` si
  `branch_deploy_status=yml-stale`). En dev NO se muestra (el clon suele estar en una
  feature branch mid-trabajo).
- Scope default: `LOCAL_PROJECTS` + `vps-ops-toolkit` (este host).
- **`--all` (fleet):** primero la tabla **Coordenada de trabajo** desde `projects.yml`
  (Proyecto · Corre en · Trabaja en `vps_work` · Rama work `branch_working` · Rama
  deploy `branch:` · Env · Status; `↩ redirect` marca los que se trabajan en otro
  VPS, ej. kore) — es global al fleet, se computa una vez. Después, el git status
  **real por VPS** (via `tailscale ssh`, o local si es este host). Si Tailscale pide
  auth, muestra el link y hay que autorizar + re-correr.
- **`--all-repos`** (alias legacy `--filesystem`)**:** en ESTE host, itera todos los repos de `webapps/` (incluye
  clones residuales / scaffolds fuera de `LOCAL_PROJECTS`).

## Next steps
- `cd ~/webapps/<proyecto> && claude` → `/git-commit` — commitear + push cada repo ⚠️
- `git-status-report --all` — vista fleet completa (todos los VPS + coordenada de trabajo)
- `git-status-report --all-repos` — auditar TODOS los repos de este host
