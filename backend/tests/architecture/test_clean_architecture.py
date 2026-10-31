"""Tests de la CLEAN ARCHITECTURE : la règle de dépendance est vérifiée automatiquement.

        api  ─────────────┐
                          ▼
   infrastructure ──►  application ──►  domain ──►  core.kernel
        ▲                                              (Python pur)
        └── composition.py (seul à connaître les implémentations)

Les dépendances vont TOUJOURS vers l'intérieur. Le domaine et les cas d'usage n'importent
donc jamais Django, DRF, l'ORM, ni une autre couche externe.
"""

import sys

import pytest

from apps.dependencies import MODULE_DEPENDENCIES

from .test_module_boundaries import BACKEND, absolute_imports, python_files

APPS_DIR = BACKEND / "apps"
MODULES = sorted(MODULE_DEPENDENCIES)
STDLIB = set(sys.stdlib_module_names)


def _violations(root, *, allowed_prefixes, label):
    problems = []
    for path in python_files(root, include_tests=False):
        for imported in absolute_imports(path):
            top = imported.split(".")[0]
            if not imported or top in STDLIB or top == "__future__":
                continue
            if not any(imported == p or imported.startswith(p + ".") for p in allowed_prefixes):
                problems.append(f"{path.relative_to(BACKEND)} importe {imported} ({label})")
    return problems


@pytest.mark.parametrize("module", MODULES)
def test_domain_is_pure(module):
    """Domaine : bibliothèque standard + lui-même + noyau pur. RIEN d'autre."""
    allowed = (f"apps.{module}.domain", "core.kernel")
    assert not _violations(
        APPS_DIR / module / "domain", allowed_prefixes=allowed, label="le domaine doit être pur"
    )


@pytest.mark.parametrize("module", MODULES)
def test_application_depends_only_on_domain(module):
    """Cas d'usage : domaine + noyau pur. Ni Django, ni infrastructure, ni API."""
    allowed = (f"apps.{module}.domain", f"apps.{module}.application", "core.kernel")
    assert not _violations(
        APPS_DIR / module / "application",
        allowed_prefixes=allowed,
        label="les cas d'usage ne connaissent pas le framework",
    )


@pytest.mark.parametrize("module", MODULES)
def test_api_does_not_reach_into_infrastructure(module):
    """L'API passe par composition.py : elle ignore l'ORM et les repositories."""
    offenders = [
        f"{path.relative_to(BACKEND)} importe {imported}"
        for path in python_files(APPS_DIR / module / "api", include_tests=False)
        for imported in absolute_imports(path)
        if imported.startswith((f"apps.{module}.infrastructure", "core.infrastructure"))
        or imported == f"apps.{module}.models"
    ]
    assert not offenders, "\n".join(offenders)


@pytest.mark.parametrize("module", MODULES)
def test_infrastructure_does_not_depend_on_api(module):
    offenders = [
        f"{path.relative_to(BACKEND)} importe {imported}"
        for path in python_files(APPS_DIR / module / "infrastructure", include_tests=False)
        for imported in absolute_imports(path)
        if imported.startswith((f"apps.{module}.api", f"apps.{module}.composition"))
    ]
    assert not offenders, "\n".join(offenders)


def test_core_kernel_is_pure_python():
    assert not _violations(
        BACKEND / "core" / "kernel", allowed_prefixes=("core.kernel",), label="noyau pur"
    )


def test_core_interface_does_not_use_infrastructure():
    offenders = [
        f"{p.relative_to(BACKEND)} importe {i}"
        for p in python_files(BACKEND / "core" / "interface", include_tests=False)
        for i in absolute_imports(p)
        if i.startswith("core.infrastructure")
    ]
    assert not offenders, "\n".join(offenders)


def test_core_does_not_depend_on_business_modules():
    offenders = [
        f"{p.relative_to(BACKEND)} -> {i}"
        for p in python_files(BACKEND / "core", include_tests=False)
        for i in absolute_imports(p)
        if i == "apps" or i.startswith("apps.")
    ]
    assert not offenders, offenders


def test_no_internet_dependency_in_requirements():
    """Hors ligne : aucun broker ni service cloud obligatoire."""
    lines = (BACKEND / "requirements" / "base.txt").read_text().lower().splitlines()
    names = {
        line.split("#")[0].strip().replace("_", "-").split(">")[0].split("<")[0].split("=")[0]
        for line in lines
        if line.split("#")[0].strip() and not line.startswith("-r")
    }
    forbidden = {"celery", "redis", "boto3", "django-storages", "sentry-sdk"}
    assert not names & forbidden
