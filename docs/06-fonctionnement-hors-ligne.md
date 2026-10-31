# Fonctionnement sans accès à Internet

« Hors ligne » signifie ici : **le serveur et les postes communiquent sur le réseau local
(LAN), sans Internet**. Rien à l'exécution ne contacte l'extérieur.

## Ce qui a été fait

| Risque de dépendance Internet | Solution dans le projet |
|---|---|
| Celery + Redis (file de tâches, cache) | Supprimés. Événements et cache en mémoire/fichiers (`core/infrastructure/`) |
| Swagger / Redoc chargés depuis un CDN | `drf-spectacular-sidecar` : fichiers embarqués dans `/static/` |
| Fichiers statiques (admin Django) | WhiteNoise + `collectstatic` : servis par Django lui-même |
| Polices et scripts web | Aucun CDN ; le build `frontend/dist` ne charge que ses propres fichiers (vérifié) |
| E-mail / SMS | E-mail écrit dans `backend/sent_emails/` ; passerelles réelles = adaptateurs optionnels (module `notifications`) |
| Stockage cloud (S3) | Fichiers sur disque (`MEDIA_ROOT`) |
| Installation des bibliothèques | `pip --no-index` depuis un *wheelhouse* préparé à l'avance |
| Fuseaux horaires | Paquet `tzdata` inclus |

## Installer sur un serveur sans Internet

**Étape A : sur une machine AVEC Internet** (même système et même version de Python que le serveur) :

```bash
./scripts/offline/prepare-bundle.sh --mysql     # ajoute les pilotes SQL (ou --postgres)
```

**Étape B : copier** le dossier du projet complet + `offline-bundle/` sur le serveur (clé USB).

**Étape C : sur le serveur SANS Internet** :

```bash
cp .env.example .env     # DATABASE_URL, DJANGO_SECRET_KEY, DJANGO_ALLOWED_HOSTS=<ip-du-serveur>
./scripts/offline/install-offline.sh
backend/.venv/bin/python backend/manage.py createsuperuser
backend/.venv/bin/gunicorn config.wsgi:application --chdir backend --bind 0.0.0.0:8000
```

`install-offline.sh` vérifie les empreintes SHA-256, installe sans réseau, applique les
migrations, crée les rôles et rassemble les fichiers statiques. Le script a été testé en
isolation (installation `--no-index` + migrations + rôles + statiques).

Interface web : servir `offline-bundle/frontend-dist` avec nginx (modèle : `frontend/nginx.conf`),
avec la même origine que l'API (`/api/v1/` relayé vers gunicorn).

## Docker sans Internet

Sur une machine connectée : `docker pull mysql:8.4 …` puis
`docker save -o images.tar mysql:8.4 <vos images>` ; sur le serveur : `docker load -i images.tar`.

## Limites à connaître

1. **MySQL ou PostgreSQL** doit être installé localement (ou SQLite pour de petites installations).
2. Aucune **sauvegarde cloud** : prévoir une sauvegarde locale (`mysqldump` planifié, copie sur disque externe).
3. L'**horloge** du serveur doit être juste (jetons JWT, journal d'audit) : serveur NTP local ou réglage manuel.
4. Le **mode déconnecté d'un poste client** (saisir malgré une coupure du réseau local) n'est pas
   inclus ; voir l'ADR 0008 pour la décision à prendre.
