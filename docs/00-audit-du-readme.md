# Audit du README initial et corrections

Chaque faille est associée à sa correction et à l'endroit du projet où elle est appliquée.
Légende : **Critique** (sécurité / irréversible), **Majeur** (dette structurelle), **Mineur**.

## 1. Architecture et SOLID

| # | Gravité | Faille dans le README | Correction | Où |
|---|---|---|---|---|
| A1 | Majeur | « Monolithe modulaire » nominal : rien n'empêche un module d'importer les modèles d'un autre (couplage en spaghetti) | Chaque module expose `public.py` ; seuls ces imports sont autorisés, et seulement vers les dépendances déclarées. **Vérifié par des tests automatiques** | `apps/*/public.py`, `apps/dependencies.py`, `tests/architecture/` |
| A2 | Majeur | 14 apps « prévisionnelles » sans graphe de dépendances | Graphe explicite et sans cycle (testé) | `apps/dependencies.py`, `docs/01-architecture.md` |
| A3 | Majeur | Dossier `shared/` : risque de fourre-tout dont tout dépend | `core/` borné (modèles de base, permissions, erreurs, événements) et **interdit de dépendre de `apps/`** (testé) | `backend/core/` |
| A4 | Majeur | Exemple de service avec `@staticmethod` : pas d'injection de dépendances, difficile à tester, viole le principe d'inversion (D) | Services en classes à dépendances injectées (port d'audit, générateur de numéro) | `apps/patients/services/patient_service.py` |
| A5 | Majeur | Deux structures de module (« simple » ou « sous-packages ») : incohérence entre modules | **Une seule structure standard** pour tous (`models/ services/ selectors/ api/ events.py public.py tests/`), contrôlée par test | `MODULE.md`, test de structure |
| A6 | Mineur | Selectors « facultatifs », repositories « si besoin » : frontière lecture/écriture floue | Séparation écriture (`services`) / lecture (`selectors`) ; pas de repository (l'ORM suffit) mais des **ports** là où l'inversion apporte de la valeur (audit) | `apps/audit/public.py` |
| A7 | Majeur | Signaux Django évoqués : couplage implicite, ordre non maîtrisé | Bus d'événements de domaine explicite, publié après commit | `core/events.py`, `apps/patients/events.py` |
| A8 | Mineur | `caisse` séparé de `paiements` : même domaine, forte dépendance mutuelle | Fusion : la caisse est un sous-domaine de `paiements` | `apps/paiements/MODULE.md` |
| A9 | Majeur | Aucune règle de routage ni de **versionnement** d'API | Préfixe `/api/v1/` pour tous les clients | `config/api_v1.py` |
| A10 | Majeur | Pas de **contrat d'API** : web et mobile risquent de diverger | OpenAPI généré (drf-spectacular), versionné, validé en CI ; types TypeScript générés ; client Dart générable | `contracts/openapi/schema.yaml` |

## 2. Sécurité et données médicales

| # | Gravité | Faille | Correction | Où |
|---|---|---|---|---|
| S1 | Critique | Exemple `fields = "__all__"` (le README le signale mais l'exemple reste) : fuite de champs et *mass assignment* | Serializers à champs explicites + **liste blanche** dans le service (testé : `numero_dossier` forcé par le client est ignoré) | `patients/api/serializers.py`, `WRITABLE_FIELDS` |
| S2 | Critique | Authentification non définie. DRF autorise **tout le monde par défaut** | `IsAuthenticated` global + permissions par action (`view/add/change/delete`) ; la lecture exige aussi `view_*` | `core/permissions.py`, `settings/base.py` |
| S3 | Critique | Modèle utilisateur par défaut : changer plus tard est quasi impossible une fois migré | `AUTH_USER_MODEL = accounts.User` dès la première migration | `apps/accounts/` |
| S4 | Critique | Identifiants entiers séquentiels exposés dans l'URL (énumération des patients) | `public_id` UUID exposé ; clé entière interne seulement (testé : `/patients/1/` introuvable) | `core/models.py` |
| S5 | Majeur | Pas de stratégie de jetons (durée, rotation, révocation) | JWT d'accès 15 min, refresh avec **rotation + liste noire**, limitation de débit sur la connexion | `settings/base.py`, `accounts/api/` |
| S6 | Majeur | « Journalisation et audit » sans conception | `AuditLog` **immuable**, sans données médicales (noms de champs, jamais les valeurs) ; identifiant de requête pour corréler | `apps/audit/`, `core/middleware.py` |
| S7 | Majeur | Suppression physique de données médicales | Archivage logique (`SoftDeleteModel`) | `core/models.py` |
| S8 | Critique | Pas de séparation des réglages ; risque de `SECRET_KEY` en dur | `settings/{base,dev,test,prod}`, `DJANGO_SECRET_KEY` obligatoire, production accepte uniquement les moteurs SQL pris en charge (ADR 0009), HTTPS/HSTS/cookies sécurisés | `config/settings/` |
| S9 | Majeur | Stockage des jetons côté navigateur non défini | Accès en mémoire, refresh en `sessionStorage`, CSP ; évolution documentée vers cookie `httpOnly` | `frontend/src/core/auth/`, ADR 0003 |
| S10 | Mineur | Aucun en-tête de sécurité côté frontend | CSP, `X-Frame-Options`, `nosniff` dans la configuration nginx | `frontend/nginx.conf` |
| S11 | Majeur | Format d'erreur libre : risque de fuite d'informations internes | Enveloppe d'erreur unique ; les erreurs 500 ne détaillent rien | `core/exceptions.py` |

## 3. Versions et compatibilité

| # | Gravité | Faille | Correction |
|---|---|---|---|
| V1 | Majeur | « MySQL 8.x » trop vague. Django 6.0 accepte encore MySQL 8.0, mais **Django 6.1 le retire et ne liste que MySQL 8.4** | Cibler **MySQL 8.4 LTS** dès maintenant (Docker, CI, doc) - [source](https://code.djangoproject.com/wiki/SupportedDatabaseVersions) |
| V2 | Mineur | Versions non verrouillées | Plages compatibles dans `requirements/` et `package.json`, `package-lock.json` versionné ; verrouillage strict conseillé via pip-tools |
| V3 | Mineur | JavaScript seul | **TypeScript** : types générés depuis OpenAPI, erreurs détectées à la compilation. TypeScript 5.9 retenu par prudence de compatibilité avec `vue-tsc` |

## 4. Scalabilité et évolutivité

| # | Gravité | Faille | Correction |
|---|---|---|---|
| E1 | Majeur | Pas de tâches asynchrones (PDF de factures, exports, notifications) | Événements de domaine en mémoire (`core/infrastructure/events.py`) ; file de tâches optionnelle plus tard, SANS dépendre d'Internet (voir ADR 0008) |
| E2 | Majeur | Pagination et filtrage non définis (les listes de patients grossissent) | Pagination commune, filtres `django-filter`, tri whitelisté, index en base |
| E3 | Majeur | Numéro de dossier : risque de doublons en accès concurrent | Compteur annuel avec verrou de ligne (`select_for_update`) (testé) |
| E4 | Majeur | Fichiers joints sur le disque du serveur | Stockage abstrait ; `django-storages` (objet) prévu pour la production |
| E5 | Mineur | Pas de conteneurs, ni de sondes de santé | `Dockerfile`, `docker-compose.yml`, `/health/` et `/health/ready/` |
| E6 | Majeur | Montants financiers : risque d'arrondis et de modifications de factures soldées | Règle : `Decimal` (jamais `float`), factures soldées immuables, paiements en journal (à appliquer dans `facturation`/`paiements`) |

## 5. Maintenabilité et qualité

| # | Faille | Correction |
|---|---|---|
| M1 | Aucune vérification automatique des conventions | `ruff`, tests d'architecture, couverture minimale, CI GitHub Actions, `pre-commit` |
| M2 | Routeur frontend central à modifier à chaque module | Routes auto-découvertes (`modules/*/routes.ts`) : ajouter un module ne modifie pas le routeur |
| M3 | Pas de gabarit de PR | Liste de contrôle dans `.github/pull_request_template.md` |
| M4 | Chaîne de décisions non tracée | ADR dans `docs/adr/` |

## 6. Préparation du mobile (Flutter)

Voir [`03-preparation-flutter.md`](03-preparation-flutter.md). Points traités : API sans état et
versionnée, contrat OpenAPI, authentification par jetons indépendante du navigateur, erreurs
et pagination uniformes, dates ISO 8601 UTC, identifiants UUID, module `notifications`
réservé aux jetons push.

## Ce qui reste à faire (non couvert par ce squelette)

- Spécifier le périmètre de chaque module « squelette » avant de coder.
- Valider la configuration **MySQL en production** (non testée dans ce squelette : seul SQLite a été utilisé en local ; la CI contient un job MySQL 8.4 à exécuter).
- Définir la réglementation applicable (conservation, accès, hébergement des données de santé).
- Choisir l'hébergement du stockage objet, la sauvegarde et la supervision (ex. Sentry).
