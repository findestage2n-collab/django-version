# Conventions de l'API (web et mobile)

Ces règles s'appliquent à **tous** les endpoints, pour que Vue et Flutter les traitent de la même façon.

| Sujet | Règle |
|---|---|
| Base | `/api/v1/<module>/...`. Un changement incompatible crée `/api/v2/` ; `v1` reste servie pendant la migration des clients |
| Format | JSON UTF-8 ; clés en `snake_case` |
| Identifiants | `public_id` UUID uniquement ; jamais la clé entière interne |
| Dates | ISO 8601 ; `datetime` en UTC avec décalage (`2026-10-24T05:25:00Z`) ; `date` en `YYYY-MM-DD` |
| Authentification | `Authorization: Bearer <access>` ; `POST /auth/login/`, `/auth/refresh/` (rotation), `/auth/logout/`, `GET /auth/me/` |
| Droits | Permissions Django `<app>.<action>_<modèle>` ; `/auth/me/` les renvoie pour l'affichage (le serveur reste l'autorité) |
| Pagination | `?page=1&page_size=20` (max 100) → `{count, next, previous, results}` |
| Filtres / tri | Paramètres nommés (`q`, `sexe`, `created_after`…) ; `?ordering=nom` ou `-created_at` sur les champs autorisés |
| Création | `201` + ressource complète. Modification partielle : `PATCH`. Suppression : `204` (archivage logique) |
| Erreurs | Enveloppe unique, voir ci-dessous |
| Limitation de débit | `429` ; la connexion est limitée plus strictement |
| Corrélation | `X-Request-ID` accepté en entrée, toujours renvoyé ; repris dans `request_id` des erreurs |
| Langue | `Accept-Language: fr` |

## Enveloppe d'erreur

```json
{
  "error": {
    "code": "validation_error",
    "message": "Les données envoyées sont invalides.",
    "details": { "prenom": ["Ce champ est obligatoire."] }
  },
  "request_id": "3f2c9a0e4b7d4c1e9d1a6a7b8c9d0e1f"
}
```

| Statut | `code` typiques |
|---|---|
| 400 | `validation_error` |
| 401 | `not_authenticated`, `authentication_failed`, `token_not_valid` |
| 403 | `permission_denied` |
| 404 | `not_found` |
| 409 | `conflict`, `duplicate_patient` (règle métier) |
| 429 | `throttled` |

Les clients se basent sur `error.code` (stable), jamais sur le texte de `message`.

## Exemple : patients

| Méthode | URL | Permission | Résultat |
|---|---|---|---|
| GET | `/api/v1/patients/?q=mbarga&page=1` | `patients.view_patient` | 200 liste paginée |
| POST | `/api/v1/patients/` | `patients.add_patient` | 201 ; 409 si doublon (sauf `allow_duplicate: true`) |
| GET | `/api/v1/patients/{public_id}/` | `patients.view_patient` | 200 |
| PATCH | `/api/v1/patients/{public_id}/` | `patients.change_patient` | 200 |
| DELETE | `/api/v1/patients/{public_id}/` | `patients.delete_patient` | 204 (archivage) |

Documentation interactive en développement : `http://localhost:8000/api/docs/`.
