# Guide du backend pour débutant (Clean Architecture)

Ce guide explique **comment** le backend est organisé, **pourquoi**, et **sur quoi je me suis basé**.
Le mobile n'est pas concerné : le dossier `mobile/` ne contient que des notes, on l'ignore.

## 0. Les quatre idées à retenir

1. **Django impose très peu de choses** : un *projet* (la configuration) et des *applications* (des dossiers de code). Tout le reste (`domain/`, `application/`, `composition.py`…) est **ma convention**, pas une règle de Django.
2. **Une application Django = un module métier** (patients, facturation…). Tous les modules ont la même forme : comprenez-en un, vous les comprenez tous.
3. **Clean Architecture = des cercles, et une seule règle** : le code *intérieur* (les règles du métier) ne connaît jamais le code *extérieur* (Django, la base de données, HTTP). Les flèches d'import vont toujours vers l'intérieur.
4. **Pour débuter, ne lisez que `apps/patients/`**, dans l'ordre du §3.

## 1. Sur quoi je me suis basé

| Source | Ce que j'en ai retenu |
|---|---|
| **Votre README** | Liste des modules, technologies (Django, DRF, MySQL, Vue), « monolithe modulaire respectant SOLID », web + mobile via API |
| **Vos 67 modèles Laravel** | Le vrai domaine : `Patient` relié à une trentaine de tables, factures, suppression logique, numéros de dossier |
| **Vos croquis** | Rôles Admin/Secrétaire, Patient ↔ Dossier ↔ Visite, cas d'utilisation |
| **Vos demandes** | SOLID, évolutivité, **Clean Architecture**, **fonctionnement sans Internet**, backend d'abord |
| **Documentation officielle et ouvrages publics** | Voir §11 |
| **Mon jugement d'architecte** | Le découpage exact (`domain` / `application` / `infrastructure` / `api` / `composition`), `public.py` et les tests d'architecture sont **mes choix** : ils s'inspirent de pratiques connues, ce n'est pas un standard officiel de Django |

Limite honnête : aucune règle ne dit que c'est la seule bonne structure. Une architecture plus simple (modèles + vues Django classiques) est valable pour un petit projet ; ici on a choisi la Clean Architecture parce que vous l'avez demandée et que le projet est appelé à grandir.

## 2. La Clean Architecture en 5 minutes

Imaginez un restaurant :

- **Domaine** = *la recette* : les règles (« un patient doit avoir un nom, une date de naissance ne peut pas être dans le futur »). Elle reste vraie quelle que soit la cuisine.
- **Cas d'usage** = *le plat commandé* : « enregistrer un patient » = valider, numéroter, vérifier les doublons, sauvegarder, tracer.
- **Infrastructure** = *les ustensiles et le frigo* : Django ORM et un moteur relationnel (SQLite, MySQL ou PostgreSQL). On peut les changer sans changer la recette.
- **API** = *le serveur en salle* : il prend la commande en HTTP/JSON, la transmet, rapporte le plat.

```text
              ┌──────────── api/ (HTTP, DRF) ────────────┐
              │   ┌── infrastructure/ (ORM, base SQL) ──┐   │
              │   │   ┌──── application/ ────────┐   │   │
              │   │   │   ┌── domain/ ──┐        │   │   │
              │   │   │   │ entités     │        │   │   │      → : « a le droit
              │   │   │   │ règles      │        │   │   │         d'importer »
              │   │   │   │ ports       │        │   │   │
              │   │   │   └─────────────┘        │   │   │      Les flèches vont
              │   │   │    cas d'usage           │   │   │      toujours vers le centre.
              │   │   └──────────────────────────┘   │   │
              │   └──────────────────────────────────┘   │
              └───────────────────────────────────────────┘
```

**Les ports** (la notion clé) : le cas d'usage dit « il me faut un dépôt de patients », sous la forme d'une *interface* Python (`Protocol`) définie dans le domaine. L'infrastructure utilise Django ORM ; `DATABASE_URL` choisit SQLite, MySQL ou PostgreSQL. Les tests métier fournissent une simple liste en mémoire. MongoDB n'est pas pris en charge par cette configuration Django.

**`composition.py`** : l'unique fichier qui sait « quel dépôt concret branché à quel cas d'usage ». Si demain on change de base, on ne modifie que lui et l'adaptateur.

## 3. Le backend commenté

```text
backend/
├── manage.py
├── config/                 ← LE PROJET Django : réglages et routes générales
│   ├── settings/           ← base · dev · test · prod
│   ├── urls.py             ← /admin, /health, /api/v1/..., /api/docs
│   └── api_v1.py           ← une ligne par module
├── core/                   ← outils communs, en trois couches
│   ├── kernel/             ← PYTHON PUR : erreurs, ports (AuditTrail, UnitOfWork…), horloge
│   ├── infrastructure/     ← Django : classes de base ORM, bus d'événements, transactions
│   └── interface/          ← DRF : format des erreurs, droits par rôle, pagination
├── apps/                   ← LES MODULES MÉTIER
│   ├── accounts/  audit/  patients/      ← implémentés (modèles de référence)
│   └── (12 autres)                        ← squelettes vides
├── tests/architecture/     ← vérifie automatiquement les règles de dépendance
└── requirements/
```

**Lecture conseillée de `apps/patients/`** (de l'intérieur vers l'extérieur) :

| Ordre | Fichier | Ce qu'on y apprend |
|---|---|---|
| 1 | `domain/entities.py` | La classe `Patient` et **toutes** les règles métier (validation, âge, archivage) |
| 2 | `domain/repositories.py` | Les **ports** : ce dont le métier a besoin |
| 3 | `application/use_cases.py` | `RegisterPatient`, `UpdatePatient`… : le scénario complet |
| 4 | `tests/test_domain_patient.py`, `test_use_cases.py` | Comment on teste **sans base** (avec `fakes.py`) |
| 5 | `infrastructure/models.py`, `repositories.py` | La table MySQL et l'implémentation du port |
| 6 | `composition.py` | Le câblage |
| 7 | `api/serializers.py`, `views.py`, `urls.py` | La couche HTTP, très mince |
| 8 | `public.py` | Ce que les autres modules ont le droit d'utiliser |

## 4. Le trajet d'une requête (`POST /api/v1/patients/`)

1. `config/urls.py` → `config/api_v1.py` → `apps/patients/api/urls.py` : Django trouve la vue.
2. `core/interface/permissions.py` : l'utilisateur a-t-il `patients.add_patient` ? Sinon **403**.
3. `api/serializers.py` : la **forme** des données est-elle correcte (types, champs requis) ? Sinon **400**.
4. `api/views.py` : appelle `use_cases().register.execute(...)`. Aucune règle métier dans la vue.
5. `application/use_cases.py` (`RegisterPatient`) : ouvre une transaction, demande un numéro de dossier, crée l'entité.
6. `domain/entities.py` (`Patient.register`) : **valide les règles** (date non future, téléphone, taux 0-100…). Sinon **400** `validation_error`.
7. Le cas d'usage refuse un doublon (**409**), enregistre via le dépôt, écrit l'audit, publie l'événement `PatientRegistered` (après le commit).
8. `api/serializers.py` renvoie le patient : **201**.

Pour changer une règle (« le taux max devient 90 »), vous modifiez **un seul fichier** : `domain/entities.py`.

## 5. Où sont passés `services/`, `selectors/` et `models/` ?

Dans la première version, les règles métier étaient dans `services/` et manipulaient directement les modèles Django : le métier dépendait donc du framework. **Ces dossiers ont été supprimés** :

| Avant | Maintenant |
|---|---|
| `services/patient_service.py` | `application/use_cases.py` (scénarios) + `domain/entities.py` (règles) |
| `selectors/patient_selectors.py` | Port `PatientRepository.search` + implémentation dans `infrastructure/repositories.py` |
| `models/patient.py` (règles + table) | Règles → `domain/entities.py` ; table seule → `infrastructure/models.py` |
| `errors.py`, `events.py` | `domain/errors.py`, `domain/events.py` |
| `PatientFilter` (django-filter sur QuerySet) | Critères du domaine (`PatientSearch`) ; `django-filter` retiré |
| `core/events.py` (avec Django) | Port dans `core/kernel`, bus en mémoire dans `core/infrastructure/events.py` |
| Celery + Redis | Supprimés (inutiles et dépendants du réseau) |

## 6. Pourquoi ces choix, en questions simples

- **Pourquoi un « monolithe modulaire » et pas des microservices ?** Petite équipe, une seule base, opérations qui touchent plusieurs domaines à la fois. Les modules gardent la possibilité de séparer plus tard.
- **Pourquoi `public.py` ?** Sans règle, `facturation` irait lire les tables de `patients` : changer un champ casserait tout. Un test échoue si on contourne `public.py`.
- **Pourquoi un UUID dans les adresses ?** Avec `/patients/1/`, `/patients/2/`…, on pourrait deviner les dossiers voisins ([OWASP API1](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/)).
- **Pourquoi pas de clé étrangère entre modules ?** Les modules se référencent par UUID : ils restent indépendants (on pourra les séparer).
- **Pourquoi l'archivage logique ?** Un dossier médical ne se supprime pas ; on le masque (`deleted_at`).
- **Pourquoi des réglages séparés ?** Pour qu'une configuration de développement n'atteigne jamais la production.
- **Pourquoi plus de fichiers qu'avant ?** C'est le prix de la Clean Architecture. En échange : tests du métier instantanés, framework remplaçable, règles vérifiées par la CI.
- **L'authentification fait-elle exception ?** Oui, assumée : la connexion JWT reste adossée à Django et SimpleJWT dans `accounts/api` (ADR 0007).

## 7. Ce qui est vérifié automatiquement

`pytest` exécute 164 tests. Exemples de règles qui font échouer la CI :

- « `domain/` importe Django » ou « `application/` importe `infrastructure/` » ;
- « `api/` utilise directement l'ORM » ;
- « un module importe un autre sans passer par `public.py` » ou crée un cycle ;
- « un ancien dossier `services/` réapparaît » ;
- « Celery, Redis ou un SDK cloud revient dans `requirements/base.txt` » (mode hors ligne).

## 8. Reconstruire le backend étape par étape

> **Transparence** : le contenu des fichiers livrés a été **généré par script puis testé** ; les commandes `startproject`/`startapp` ci-dessous ont été essayées séparément dans un dossier vierge. Elles expliquent la logique de construction.

**Étape 1 : dossier, environnement virtuel, dépendances**

```bash
mkdir hospital-management && cd hospital-management && git init
mkdir backend && cd backend
python3 -m venv .venv                 # Windows : py -m venv .venv
source .venv/bin/activate             # Windows : .venv\Scripts\activate
pip install "Django>=6.0.9,<6.1" djangorestframework djangorestframework-simplejwt \
            drf-spectacular drf-spectacular-sidecar django-cors-headers django-environ \
            argon2-cffi whitenoise tzdata
```

**Étape 2 : le projet Django et la séparation des réglages**

```bash
django-admin startproject config .
mkdir config/settings && mv config/settings.py config/settings/base.py && touch config/settings/__init__.py
# Dans base.py : BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Créer dev.py, test.py, prod.py ; mettre config.settings.dev dans manage.py
```

**Étape 3 : le noyau `core` (pur → framework)**

```bash
mkdir -p core/kernel core/infrastructure core/interface
touch core/__init__.py core/kernel/__init__.py core/infrastructure/__init__.py core/interface/__init__.py
# kernel : errors.py, events.py, ports.py (Protocols), clock.py   → AUCUN import Django
```

**Étape 4 : un module (ici `patients`) avec ses couches**

```bash
mkdir -p apps && touch apps/__init__.py
mkdir apps/patients
python manage.py startapp patients apps/patients
cd apps/patients
rm views.py tests.py models.py
mkdir domain application infrastructure api tests
touch domain/__init__.py application/__init__.py infrastructure/__init__.py api/__init__.py tests/__init__.py
cd ../..
```

Puis : dans `apps/patients/apps.py`, `name = "apps.patients"` et `label = "patients"` ; ajouter `"apps.patients"` à `INSTALLED_APPS`.

**Étape 5 : écrire le module DANS CET ORDRE (de l'intérieur vers l'extérieur)**

1. `domain/entities.py`, `errors.py`, `events.py`, `repositories.py` (ports) + `tests/test_domain_*.py`
2. `application/use_cases.py` + `tests/test_use_cases.py` avec des faux en mémoire
3. `infrastructure/models.py` (table), `repositories.py` (adaptateur), et `models.py` à la racine : `from .infrastructure.models import *`
4. `composition.py`
5. `api/serializers.py` → `views.py` → `urls.py`, une ligne dans `config/api_v1.py`
6. `public.py`
7. `python manage.py makemigrations patients` puis `migrate`

**Étape 6 : l'utilisateur personnalisé AVANT toute migration** (`accounts`) : `AUTH_USER_MODEL = "accounts.User"`, car Django déconseille de le changer ensuite.

**Étape 7 : rôles, administrateur, serveur, tests**

```bash
python manage.py seed_roles
python manage.py createsuperuser
python manage.py runserver            # http://127.0.0.1:8000/api/docs/
pip install pytest pytest-django pytest-cov ruff
pytest && ruff check .
```

## 9. Lancer le projet livré (le plus simple)

Prérequis : Python 3.12 ou plus (testé avec 3.13). On démarre avec **SQLite** ; MySQL viendra ensuite.

```bash
cd hospital-management
cp .env.example .env
# Dans .env : DATABASE_URL=sqlite:///db.sqlite3  et une longue DJANGO_SECRET_KEY aléatoire

cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py seed_roles
python manage.py createsuperuser
python manage.py runserver
```

Ouvrir `http://127.0.0.1:8000/api/docs/` (documentation interactive, **servie localement**) et `/admin/`.

Vérifié avant livraison (SQLite) : migrations, rôles, connexion, création d'un patient (`P2026-000001`), doublon refusé (409), téléphone invalide refusé (400 `validation_error`), accès sans jeton (401), documentation Swagger servie sans CDN.

Passer à MySQL : `docker compose up -d db`, `pip install -r requirements/mysql.txt` (sous Linux : `libmysqlclient-dev` et `pkg-config` d'abord), puis régler `DATABASE_URL`. Pour PostgreSQL, installer `requirements/postgres.txt` et régler l'URL `postgres://...`. La CI exécute les tests d'intégration sur les deux moteurs. Changer l'URL ne transfère pas les données : voir le README avant toute bascule.

## 10. Sans Internet

Aucune dépendance réseau à l'exécution : voir [`06-fonctionnement-hors-ligne.md`](06-fonctionnement-hors-ligne.md) (installation par *wheelhouse*, Swagger embarqué, fichiers statiques servis par WhiteNoise).

## 11. Glossaire

| Mot | Sens simple |
|---|---|
| Entité | Objet métier avec ses règles (`Patient`), en Python pur |
| Cas d'usage | Une action complète de l'application (`RegisterPatient`) |
| Port | Interface Python (`Protocol`) décrivant ce dont le métier a besoin |
| Adaptateur | Classe qui implémente un port avec une technologie (ORM, e-mail…) |
| Repository | Adaptateur de stockage : « ajouter, retrouver, chercher des patients » |
| Composition (racine de) | Fichier qui assemble cas d'usage et adaptateurs (injection de dépendances) |
| Unit of Work | Transaction : tout réussit ou rien n'est enregistré |
| Modèle (Django) | Classe qui devient une table ; ici un détail d'`infrastructure/` |
| Migration | Fichier décrivant l'évolution des tables |
| Serializer (DRF) | Traducteur objets Python ⇄ JSON (la forme, pas les règles) |
| JWT | Jeton signé prouvant la connexion |
| Rôle | Groupe de permissions (ex. SECRETAIRE) |
| OpenAPI | Description officielle de l'API |
| Archivage logique | Marquer comme supprimé sans effacer |

## 12. Sources

Liens dont j'ai **confirmé l'existence** par recherche web ; je n'ai pas relu toutes les pages dans cette session : relisez-les pour valider les détails.

**Clean Architecture et patrons**
- Robert C. Martin, [*Clean Architecture: A Craftsman's Guide to Software Structure and Design*](https://www.pearson.com/store/en-us/p/clean-architecture-a-craftsman-s-guide-to-software-structure-and-design/P200000009528/9780134494166) (livre de référence ; la « règle de dépendance »). L'article d'origine « The Clean Architecture » (2012, blog de l'auteur) est aussi à lire ; je n'ai pas pu confirmer son adresse exacte, cherchez son titre.
- Percival & Gregory, [*Architecture Patterns with Python*, chap. 6 « Unit of Work »](https://www.oreilly.com/library/view/architecture-patterns-with/9781492052197/ch06.html) (repository, unit of work, injection de dépendances en Python)
- Python, [`typing.Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol) (interfaces structurelles utilisées pour les ports)

**Django, DRF et outils**
- Django, [Customizing authentication](https://docs.djangoproject.com/en/6.1/topics/auth/customizing/) (utilisateur personnalisé)
- Django, [Deployment checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/)
- Django, [Bases de données prises en charge par version](https://code.djangoproject.com/wiki/SupportedDatabaseVersions) (MySQL 8.4)
- Django REST framework, [Permissions](https://www.django-rest-framework.org/api-guide/permissions/) et [Settings](https://www.django-rest-framework.org/api-guide/settings/)
- Simple JWT, [Settings](https://django-rest-framework-simplejwt.readthedocs.io/en/stable/settings.html)
- drf-spectacular, [PyPI](https://pypi.org/project/drf-spectacular/) et [drf-spectacular-sidecar](https://pypi.org/project/drf-spectacular-sidecar/) (Swagger embarqué : mode hors ligne)
- WhiteNoise, [documentation](https://whitenoise.readthedocs.io/en/latest/) (fichiers statiques sans CDN)
- OWASP, [API Security Top 10 (2023)](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
- The Twelve-Factor App, [Config](https://12factor.net/config)
