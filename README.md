# Hospital Management System

Application de gestion des activités médicales : **monolithe modulaire** Django (API REST) en
**Clean Architecture** + frontend Vue.js. Fonctionne **sans Internet** (réseau local).
Une application mobile Flutter consommera plus tard la même API (`/api/v1/`) : elle n'est pas
à développer maintenant.

| Partie | Technologie |
|---|---|
| Backend | Python 3.13, Django 6.0, Django REST Framework, SimpleJWT, drf-spectacular |
| Frontend web | Vue 3, TypeScript, Vite, Pinia, Vue Router, Tailwind CSS 4, vue-i18n |
| Mobile (plus tard) | Flutter : voir `mobile/` (notes seulement) |
| Données | MySQL 8.4 LTS, PostgreSQL ou SQLite (choix par `DATABASE_URL`). Aucun Redis, aucun Celery |

## Ordre de travail

1. **Backend** : lire [`docs/05-guide-backend-debutant.md`](docs/05-guide-backend-debutant.md), puis étudier le module `apps/patients/`.
2. **Frontend** : ensuite seulement.
3. **Mobile** : plus tard ; l'architecture est déjà compatible.

## Structure

```text
hospital-management/
├── backend/        # Django + DRF : config/, core/, apps/<module>/
├── frontend/       # Vue 3 + TS : src/{app,core,shared,modules}
├── mobile/         # Flutter (plus tard) : notes d'architecture
├── contracts/      # openapi/schema.yaml : contrat unique des clients
├── scripts/offline # installation sans Internet
├── docs/           # guide débutant, architecture, conventions API, ADR
├── .github/        # CI + modèle de Pull Request
└── docker-compose.yml  Makefile  .env.example
```

Chaque module backend suit la **Clean Architecture** (voir `docs/01-architecture.md`) :

```text
apps/patients/
├── domain/          # règles métier en Python pur (entités, erreurs, événements, ports)
├── application/     # cas d'usage (RegisterPatient, UpdatePatient…)
├── infrastructure/  # tables Django, repositories : implémentent les ports
├── api/             # serializers, vues, urls DRF
├── composition.py   # relie les cas d'usage aux implémentations
├── public.py        # ce que les autres modules ont le droit d'utiliser
└── tests/
```

## Démarrage avec Docker (Windows, macOS et Linux)

C'est le moyen recommandé pour retrouver le même environnement sur différents systèmes. Il
faut Docker Desktop avec Compose sous Windows/macOS, ou Docker Engine avec le plugin Compose
sous Linux. Aucun Python, Node.js ou serveur MySQL n'est nécessaire sur l'ordinateur hôte.

1. Clonez le dépôt et ouvrez un terminal à sa racine :

   ```bash
   git clone https://github.com/findestage2n-collab/django-version.git
   cd django-version
   ```

2. Créez `.env` à partir de l'exemple :

   **PowerShell**
   ```powershell
   Copy-Item .env.example .env
   notepad .env
   ```

   **macOS / Linux**
   ```bash
   cp .env.example .env
   ```

   Remplacez `DJANGO_SECRET_KEY`, `MYSQL_PASSWORD` et `MYSQL_ROOT_PASSWORD` par des valeurs
   fortes. Pour générer une clé Django sans installer Python sur l'hôte :

   ```bash
   docker run --rm python:3.13-slim python -c "import secrets; print(secrets.token_urlsafe(64))"
   ```

   Copiez la clé affichée dans `.env`. Gardez ce fichier privé : **ne le commitez pas**.

3. Construisez les images et démarrez l'application :

   ```bash
   docker compose up --build
   ```

   Au premier démarrage, Docker télécharge les images et dépendances. MySQL démarre, puis le
   backend attend que la base soit prête, applique automatiquement les migrations et crée les
   rôles avant de démarrer. Les journaux restent visibles dans ce terminal.

4. Ouvrez :
   - Frontend : [http://localhost:5173](http://localhost:5173)
   - Documentation API : [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
   - Administration Django : [http://localhost:8000/admin/](http://localhost:8000/admin/)

   Pour créer un compte administrateur, ouvrez un autre terminal à la racine du projet :

   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

5. Pour arrêter l'application, faites `Ctrl+C`, puis :

   ```bash
   docker compose down
   ```

   Les données MySQL sont conservées dans le volume Docker `db_data`. **Ne faites pas**
   `docker compose down -v` sauf si vous souhaitez supprimer les données. Le port MySQL de
   l'hôte est `3307` par défaut (modifiable avec `MYSQL_PORT` dans `.env`) pour limiter les
   conflits avec un MySQL déjà installé.

Cette configuration Compose est destinée au **développement**, pas au déploiement en production.
Elle monte le code source et lance le serveur de développement Vite/Django.

## Lancer l'application en local (Windows, macOS et Linux)

Le parcours ci-dessous utilise **SQLite** : vous n'avez pas besoin d'installer ou de démarrer
MySQL. Il faut Python **3.13** (recommandé) et Node.js **22 ou plus récent**. Git est nécessaire
pour cloner le dépôt. Si ces outils ne sont pas installés, utilisez les pages officielles :
[Python 3.13](https://www.python.org/downloads/) et [Node.js 22+](https://nodejs.org/).
Sur Linux, installez Python 3.13 avec le gestionnaire de paquets de votre distribution ou
`pyenv` si cette version n'est pas proposée. Vérifiez ensuite les commandes :

| Windows PowerShell | macOS / Linux |
|---|---|
| `py -3.13 --version` | `python3.13 --version` |
| `node --version` | `node --version` |
| `npm --version` | `npm --version` |

`node --version` doit afficher `v22` ou une version supérieure. Les commandes ci-dessous
s'exécutent depuis un terminal, sauf indication contraire.

### 1. Récupérer le projet et créer la configuration locale

Clonez le dépôt GitHub, puis entrez dans le dossier du projet :

```bash
git clone https://github.com/findestage2n-collab/django-version.git
cd django-version
```

Copiez le fichier d'exemple `.env.example` vers `.env` à la **racine** du projet (au même niveau
que `docker-compose.yml`).

**Windows PowerShell :**

```powershell
Copy-Item .env.example .env
notepad .env
```

**macOS / Linux :**

```bash
cp .env.example .env
nano .env
```

Dans `.env`, configurez SQLite :

```dotenv
DATABASE_URL=sqlite:///db.sqlite3
```

Remplacez aussi `DJANGO_SECRET_KEY=change-me-with-a-long-random-value` par une clé aléatoire.
Générez-en une avec la commande Python indiquée ci-dessous, puis collez le résultat dans `.env`.
Ne partagez pas cette clé et ne commitez jamais `.env` (il est ignoré par Git).

### 2. Installer et préparer le backend Django

Créez l'environnement Python dans `backend/`, activez-le, puis installez les dépendances.
Dans PowerShell, exécutez :

```powershell
cd backend
py -3.13 --version
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip
pip install -r requirements/dev.txt
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Si PowerShell bloque l'activation, autorisez les scripts uniquement dans ce terminal, puis
réessayez :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Dans **macOS / Linux**, exécutez :

```bash
cd backend
python3.13 --version
python3.13 -m venv .venv
source .venv/bin/activate
python --version
python -m pip install --upgrade pip
pip install -r requirements/dev.txt
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Dans les deux cas, vérifiez que `python --version` affiche `Python 3.13.x`. Copiez la clé
affichée par la dernière commande dans `DJANGO_SECRET_KEY` de `../.env`. Ensuite, toujours dans
`backend/` et avec l'environnement virtuel activé, préparez la base et les rôles :

```bash
python manage.py migrate
python manage.py seed_roles
python manage.py createsuperuser
```

La création du superutilisateur est facultative pour consulter l'API, mais nécessaire pour se
connecter à l'administration Django.

### 3. Démarrer le backend

Dans le même terminal, toujours depuis `backend/` :

```bash
python manage.py runserver
```

Le backend est disponible sur [http://127.0.0.1:8000](http://127.0.0.1:8000). La racine `/`
n'affiche pas de page ; ouvrez plutôt la documentation API :
[http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/).

### 4. Installer et démarrer le frontend

Ouvrez un **deuxième terminal** à la racine du projet.

**Windows PowerShell :**

```powershell
cd frontend
npm ci
npm run dev
```

**macOS / Linux :**

```bash
cd frontend
npm ci
npm run dev
```

Ouvrez [http://localhost:5173](http://localhost:5173). Gardez les deux terminaux ouverts :
un pour Django, l'autre pour Vite. Le frontend transmet les appels API au backend sur le port
8000.

### Utiliser MySQL ou PostgreSQL à la place de SQLite (facultatif)

Installez et démarrez le serveur de base de données choisi, créez-y une base et un utilisateur,
puis remplacez `DATABASE_URL` dans `.env` :

```dotenv
# MySQL
DATABASE_URL=mysql://utilisateur:mot-de-passe@127.0.0.1:3306/hospital

# PostgreSQL
DATABASE_URL=postgres://utilisateur:mot-de-passe@127.0.0.1:5432/hospital
```

Depuis `backend/`, avec `.venv` activé, installez le pilote correspondant :

```bash
pip install -r requirements/mysql.txt
# ou
pip install -r requirements/postgres.txt
```

Puis appliquez les migrations et créez les rôles comme à l'étape 2. Le fichier `docker-compose.yml`
peut démarrer MySQL avec `docker compose up -d db` (Docker Desktop sur Windows/macOS, Docker Engine
sur Linux). Changer `DATABASE_URL` ne transfère pas automatiquement les données d'une base à une
autre.

## Commandes utiles

| Commande | Effet |
|---|---|
| `make check` | lint + tests (backend, architecture, frontend) : à lancer avant chaque PR |
| `make test` | tests backend et frontend |
| `make schema` | régénère `contracts/openapi/schema.yaml` puis les types TypeScript |
| `make offline-bundle` | prépare l'installation sur un serveur sans Internet |

## Documentation

1. [`docs/05-guide-backend-debutant.md`](docs/05-guide-backend-debutant.md) : **commencer ici**
2. [`docs/01-architecture.md`](docs/01-architecture.md) : Clean Architecture, règles, SOLID, évolutivité
3. [`docs/06-fonctionnement-hors-ligne.md`](docs/06-fonctionnement-hors-ligne.md) : installer sans Internet
4. [`docs/00-audit-du-readme.md`](docs/00-audit-du-readme.md) : failles de l'ancien README corrigées
5. [`docs/02-conventions-api.md`](docs/02-conventions-api.md) : contrat HTTP web + mobile
6. [`docs/03-preparation-flutter.md`](docs/03-preparation-flutter.md) : ce qui est prêt pour le mobile
7. [`docs/adr/`](docs/adr/) : décisions d'architecture

## Modules

| Module | Préfixe API | Rôle | Dépend de | État |
|---|---|---|---|---|
| `accounts` | `/api/v1/auth/` | Comptes, authentification et rôles | - | Implémenté |
| `audit` | `/api/v1/audit/` | Journalisation et audit | - | Implémenté |
| `personnel` | `/api/v1/personnel/` | Personnel soignant et administratif | accounts | Squelette |
| `patients` | `/api/v1/patients/` | Patients et dossiers administratifs | audit | Implémenté |
| `rendezvous` | `/api/v1/rendez-vous/` | Rendez-vous et planification | patients, personnel | Squelette |
| `consultations` | `/api/v1/consultations/` | Consultations | patients, personnel, rendezvous, audit | Squelette |
| `hospitalisations` | `/api/v1/hospitalisations/` | Hospitalisations | patients, personnel, audit | Squelette |
| `laboratoire` | `/api/v1/laboratoire/` | Laboratoire | patients, consultations, personnel | Squelette |
| `pharmacie` | `/api/v1/pharmacie/` | Pharmacie | patients, consultations, audit | Squelette |
| `facturation` | `/api/v1/facturation/` | Facturation | patients, audit | Squelette |
| `paiements` | `/api/v1/paiements/` | Paiements et caisse | facturation, audit | Squelette |
| `rapports` | `/api/v1/rapports/` | Statistiques et rapports | patients, consultations, facturation, paiements | Squelette |
| `notifications` | `/api/v1/notifications/` | Notifications (e-mail, SMS, push mobile) | accounts | Squelette |

Trois modules sont **implémentés comme modèles de référence** (`accounts`, `audit`, `patients`,
avec tests). Les autres sont des squelettes conformes à la structure standard : leur périmètre
doit être validé dans les spécifications avant de coder.
