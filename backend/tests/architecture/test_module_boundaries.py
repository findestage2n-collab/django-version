"""Tests d'architecture : ils font échouer la CI si une règle est violée.

Règles entre modules :
1. Un module n'importe un autre module que via `apps.<autre>.public`.
2. Cette dépendance doit être déclarée dans `apps/dependencies.py`.
3. Le graphe des dépendances est sans cycle.
4. Chaque module respecte la structure standard et est installé.
"""

import ast
from pathlib import Path

import pytest
from django.conf import settings

from apps.dependencies import MODULE_DEPENDENCIES

BACKEND = Path(__file__).resolve().parents[2]
APPS_DIR = BACKEND / "apps"
MODULES = sorted(MODULE_DEPENDENCIES)


def absolute_imports(path: Path):
    """Noms de modules importés, imports relatifs résolus en noms absolus."""
    package = ".".join(path.relative_to(BACKEND).with_suffix("").parts[:-1])
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package.split(".")
                base = base[: len(base) - (node.level - 1)]
                module = ".".join([*base, node.module] if node.module else base)
            else:
                module = node.module or ""
            yield module
            yield from (f"{module}.{alias.name}" for alias in node.names)


def python_files(root: Path, *, include_tests: bool = True):
    return [
        p
        for p in root.rglob("*.py")
        if "migrations" not in p.parts and (include_tests or "tests" not in p.parts)
    ]


@pytest.mark.parametrize("module", MODULES)
def test_module_only_uses_public_api_of_declared_dependencies(module):
    allowed = set(MODULE_DEPENDENCIES[module])
    violations = []
    for path in python_files(APPS_DIR / module):
        for imported in absolute_imports(path):
            parts = imported.split(".")
            if parts[0] != "apps" or len(parts) < 2 or parts[1] == module:
                continue
            other = parts[1]
            if other not in MODULE_DEPENDENCIES:
                continue
            relative = path.relative_to(BACKEND)
            if other not in allowed:
                violations.append(f"{relative}: dépendance non déclarée vers '{other}'")
            elif len(parts) < 3 or parts[2] != "public":
                violations.append(
                    f"{relative}: import interne de '{other}' ({imported}); "
                    f"utiliser apps.{other}.public"
                )
    assert not violations, "\n".join(violations)


def test_dependency_graph_is_acyclic():
    visiting, done = set(), set()

    def visit(node, chain):
        if node in done:
            return
        assert node not in visiting, f"Cycle de dépendances : {' -> '.join([*chain, node])}"
        visiting.add(node)
        for dep in MODULE_DEPENDENCIES[node]:
            assert dep in MODULE_DEPENDENCIES, f"Module inconnu : {dep}"
            visit(dep, [*chain, node])
        visiting.discard(node)
        done.add(node)

    for module in MODULES:
        visit(module, [])


REQUIRED = (
    "apps.py", "public.py", "composition.py", "models.py", "MODULE.md",
    "domain/__init__.py", "application/__init__.py", "infrastructure/__init__.py",
    "infrastructure/models.py", "api/__init__.py", "api/serializers.py", "api/views.py",
    "api/urls.py", "migrations/__init__.py", "tests/__init__.py",
)  # fmt: skip

LEGACY_DIRS = ("services", "selectors", "models")  # anciennes couches supprimées


@pytest.mark.parametrize("module", MODULES)
def test_module_has_standard_structure_and_is_installed(module):
    missing = [name for name in REQUIRED if not (APPS_DIR / module / name).exists()]
    assert not missing, f"{module}: fichiers manquants {missing}"
    legacy = [d for d in LEGACY_DIRS if (APPS_DIR / module / d).is_dir()]
    assert not legacy, f"{module}: dossiers obsolètes (ancienne architecture) {legacy}"
    assert f"apps.{module}" in settings.INSTALLED_APPS


def test_every_module_directory_is_declared():
    on_disk = {p.name for p in APPS_DIR.iterdir() if (p / "apps.py").exists()}
    assert on_disk == set(MODULE_DEPENDENCIES)
