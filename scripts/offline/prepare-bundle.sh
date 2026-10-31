#!/usr/bin/env bash
# À lancer UNE FOIS sur une machine AVEC Internet.
# Produit le dossier `offline-bundle/` à copier (clé USB, disque) sur le serveur SANS Internet.
#
#   ./scripts/offline/prepare-bundle.sh            # Python + frontend
#   ./scripts/offline/prepare-bundle.sh --mysql    # + pilotes SQL (pilote MySQL compilé pour CETTE machine)
#   ./scripts/offline/prepare-bundle.sh --postgres # + pilote PostgreSQL
#   ./scripts/offline/prepare-bundle.sh --skip-frontend
#
# Important : préparer le bundle sur le MÊME système et la MÊME version de Python que le serveur cible
# (ex. Ubuntu 24.04 + Python 3.13), car certaines bibliothèques sont des binaires.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/offline-bundle"
WITH_MYSQL=0
WITH_POSTGRES=0
WITH_FRONTEND=1
for arg in "$@"; do
  case "$arg" in
    --mysql) WITH_MYSQL=1 ;;
    --postgres) WITH_POSTGRES=1 ;;
    --skip-frontend) WITH_FRONTEND=0 ;;
    *) echo "Option inconnue : $arg" >&2; exit 2 ;;
  esac
done

rm -rf "$OUT"
mkdir -p "$OUT/wheelhouse"

echo "==> 1/3  Bibliothèques Python (wheelhouse)"
(
  cd "$ROOT/backend"
  python3 -m pip download --dest "$OUT/wheelhouse" -r requirements/base.txt gunicorn
  # Sous Linux, mysqlclient se compile : on fabrique son wheel ici (libmysqlclient-dev requis).
  if [ "$WITH_MYSQL" = 1 ]; then
    python3 -m pip wheel --wheel-dir "$OUT/wheelhouse" -r requirements/mysql.txt
  fi
  if [ "$WITH_POSTGRES" = 1 ]; then
    python3 -m pip download --dest "$OUT/wheelhouse" -r requirements/postgres.txt
  fi
)

if [ "$WITH_FRONTEND" = 1 ]; then
  echo "==> 2/3  Interface web compilée (fichiers statiques)"
  (cd "$ROOT/frontend" && npm ci --no-audit --no-fund && npm run build)
  cp -r "$ROOT/frontend/dist" "$OUT/frontend-dist"
else
  echo "==> 2/3  Interface web : ignorée (--skip-frontend)"
fi

echo "==> 3/3  Empreintes (détection d'une copie corrompue)"
(cd "$OUT" && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS)

echo "Terminé : $OUT"
echo "Copiez ce dossier avec le projet sur le serveur, puis lancez scripts/offline/install-offline.sh"
