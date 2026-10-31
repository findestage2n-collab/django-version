# Module `patients` - Patients et dossiers administratifs

- **Statut** : Implémenté (module de référence : copier ce patron)
- **Responsabilité** : Enregistrement, recherche et archivage des patients.
- **Données possédées** : Patient, numérotation des dossiers, dossier administratif
- **Dépendances autorisées** : audit (via `apps.<module>.public` uniquement)
- **Routes API** : `/api/v1/patients/`

## Structure (Clean Architecture)

La règle d'or : **les dépendances pointent toujours vers l'intérieur** (`api`/`infrastructure` → `application` → `domain`).
Le domaine ne connaît ni Django, ni la base, ni HTTP.

| Dossier / fichier | Couche | Rôle | Peut importer |
|---|---|---|---|
| `domain/` | 1 · Domaine | Entités, règles métier, erreurs, événements, **ports** (interfaces) | Python standard + `core.kernel` |
| `application/` | 2 · Cas d'usage | Ce que l'application sait faire (`RegisterPatient`…) ; orchestre le domaine via les ports | `domain` + `core.kernel` |
| `infrastructure/` | 3 · Adaptateurs de sortie | Tables Django (`models.py`), repositories, appels externes : **implémentent les ports** | tout, sauf `api` |
| `api/` | 3 · Adaptateurs d'entrée | Serializers, vues, urls DRF : traduisent HTTP ⇄ cas d'usage | `application`, `domain`, `composition`, `core.interface` |
| `composition.py` | Câblage | Seul fichier qui choisit les implémentations concrètes | tout |
| `public.py` | Frontière | Seule surface utilisable par les AUTRES modules | cas d'usage et domaine du module |
| `models.py` | Django | Simple relais vers `infrastructure/models.py` (Django le cherche ici) | `infrastructure.models` |
| `tests/` | | Domaine/cas d'usage sans base ; infrastructure et API avec base | tout |

