#!/usr/bin/env bash
# À lancer sur le serveur SANS Internet, après copie du projet et du dossier `offline-bundle/`.
#   ./scripts/offline/install-offline.sh
# Aucune connexion réseau n'est utilisée (pip --no-index).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUNDLE="$ROOT/offline-bundle"
[ -d "$BUNDLE/wheelhouse" ] || { echo "offline-bundle/wheelhouse introuvable" >&2; exit 1; }

echo "==> Vérification des empreintes"
(cd "$BUNDLE" && sha256sum --check --quiet SHA256SUMS)

echo "==> Environnement Python"
cd "$ROOT/backend"
python3 -m venv .venv
.venv/bin/pip install --no-index --find-links "$BUNDLE/wheelhouse" -r requirements/base.txt gunicorn
if ls "$BUNDLE"/wheelhouse/mysqlclient-*.whl >/dev/null 2>&1; then
  .venv/bin/pip install --no-index --find-links "$BUNDLE/wheelhouse" -r requirements/mysql.txt
fi
if ls "$BUNDLE"/wheelhouse/psycopg* >/dev/null 2>&1; then
  .venv/bin/pip install --no-index --find-links "$BUNDLE/wheelhouse" -r requirements/postgres.txt
fi

echo "==> Base de données, rôles, fichiers statiques"
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.prod}"
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py seed_roles
.venv/bin/python manage.py collectstatic --noinput

cat <<MSG

Installation terminée.
  1. Créer l'administrateur :  backend/.venv/bin/python backend/manage.py createsuperuser
  2. Lancer l'API :            backend/.venv/bin/gunicorn config.wsgi:application --chdir backend --bind 0.0.0.0:8000
  3. Interface web : servir offline-bundle/frontend-dist avec nginx (voir frontend/nginx.conf).
MSG
