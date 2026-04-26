"""Root conftest for crushme_project.

Provides shared pytest fixtures used across all test modules
and a custom coverage reporter.
"""

import os

import coverage as coverage_module
import pytest
from rest_framework.test import APIClient

# Bar widths: per-file bars use MINI, the TOTAL row uses WIDE
_MINI_W = 13
_WIDE_W = 15
_APP_NAME = "crushme_app"


def _color_for(pct):
    """Return a pytest terminal color name based on coverage percentage."""
    if pct > 80:
        return "green"
    if pct >= 50:
        return "yellow"
    return "red"


def _bar(pct, width):
    """Build a Unicode progress bar: filled for covered, dots for uncovered."""
    filled = round(pct / 100 * width)
    return "\u2588" * filled + "\u00b7" * (width - filled)


def pytest_sessionstart(session) -> None:
    """Suppress the default pytest-cov terminal summary."""
    cov_plugin = session.config.pluginmanager.get_plugin("_cov")
    if cov_plugin is None:
        return
    hook = session.config.pluginmanager.hook.pytest_terminal_summary
    for impl in hook.get_hookimpls():
        if impl.plugin is cov_plugin:
            impl.function = lambda *args, **kw: None
            break


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Remove term report formats from pytest-cov options."""
    try:
        if hasattr(config.option, "cov_report"):
            config.option.cov_report = [
                r for r in config.option.cov_report
                if not r.startswith("term")
            ]
    except Exception:
        pass


@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Custom coverage report with per-file table and Top-N focus footer."""
    cov_file = os.path.join(os.path.dirname(__file__), ".coverage")
    if not os.path.exists(cov_file):
        return

    try:
        cov = coverage_module.Coverage(data_file=cov_file)
        cov.load()
    except Exception:
        return

    results = []
    try:
        measured = cov.get_data().measured_files()
    except Exception:
        return

    for filepath in measured:
        norm = filepath.replace("\\", "/")
        if _APP_NAME not in norm or "/tests/" in norm:
            continue
        try:
            analysis = cov._analyze(filepath)
            stmts = len(analysis.statements)
            if stmts == 0:
                continue
            missing = len(analysis.missing)
            pct = (stmts - missing) / stmts * 100
            idx = norm.find(_APP_NAME)
            short = norm[idx:] if idx >= 0 else norm
            results.append({"path": short, "stmts": stmts, "missing": missing, "pct": pct})
        except Exception:
            continue

    if not results:
        return

    results.sort(key=lambda r: r["path"])
    total_stmts = sum(r["stmts"] for r in results)
    total_missing = sum(r["missing"] for r in results)
    total_pct = (total_stmts - total_missing) / total_stmts * 100 if total_stmts > 0 else 0
    top_n = sorted([r for r in results if r["missing"] > 0], key=lambda x: (x["pct"], -x["missing"]))[:3]

    try:
        term_w = terminalreporter._tw._width
    except AttributeError:
        import shutil
        term_w = shutil.get_terminal_size().columns

    _FIXED = 2 + 2 + 5 + 2 + 4 + 2 + 7 + 2 + 1 + _MINI_W + 1
    path_w = min(max(term_w - _FIXED - 2, 20), max((len(r["path"]) for r in results), default=40))
    path_w = max(path_w, 20)

    for r in results:
        if len(r["path"]) > path_w:
            r["path"] = r["path"][:path_w - 1] + "\u2026"

    tw = terminalreporter
    tw.write_sep("=", "COVERAGE REPORT", bold=True)
    tw.write("\n")
    for r in results:
        color = _color_for(r["pct"])
        mini = _bar(r["pct"], _MINI_W)
        tw.write(f"  {r['path']:<{path_w}}  {r['stmts']:>5}  {r['missing']:>4}  ")
        tw.write(f"{r['pct']:>6.1f}%  ", **{color: True})
        tw.write("[")
        tw.write(mini, **{color: True})
        tw.write("]\n")

    tw.write("\n")
    c = _color_for(total_pct)
    wide = _bar(total_pct, _WIDE_W)
    tw.write(f"  {'TOTAL':<{path_w}}  {total_stmts:>5}  {total_missing:>4}  ", bold=True)
    tw.write(f"{total_pct:>6.1f}%  ", bold=True, **{c: True})
    tw.write("[", bold=True)
    tw.write(wide, bold=True, **{c: True})
    tw.write("]\n\n", bold=True)

    dash = "\u2500" * 10
    n = len(top_n)
    label = f"Top-{n} files to focus on" if top_n else "All files fully covered"
    tw.write(f"  {dash}  {label}  ", bold=True)
    tw.write(f"(total project: {total_pct:.1f}%)  ", bold=True)
    tw.write(f"{dash}\n", bold=True)
    if not top_n:
        tw.write("\n", green=True)
    else:
        for i, r in enumerate(top_n, 1):
            color = _color_for(r["pct"])
            mini = _bar(r["pct"], _MINI_W)
            tw.write(f"  {i}.  ")
            tw.write(f"{r['pct']:>5.1f}%", **{color: True})
            tw.write("  [")
            tw.write(mini, **{color: True})
            tw.write(f"]  {r['path']}")
            tw.write(f"   ({r['missing']} lines uncovered)\n")
        tw.write("\n")


@pytest.fixture
def api_client():
    """Unauthenticated DRF API client."""
    return APIClient()


@pytest.fixture
def user(db):
    """Regular authenticated user."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass123',
    )


@pytest.fixture
def admin_user(db):
    """Staff user for admin-gated endpoints."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        is_staff=True,
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """API client authenticated as a regular user."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """API client authenticated as an admin user."""
    api_client.force_authenticate(user=admin_user)
    return api_client
