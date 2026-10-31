# Préparation de l'application mobile Flutter

La version 1.0 livre l'API et le frontend web. Pour que le mobile se branche **sans modifier le
backend**, les choix suivants sont déjà faits.

## Prêt dans cette version

| Exigence mobile | Mise en œuvre |
|---|---|
| Backend sans état | JWT : aucune session serveur ni cookie obligatoire |
| Contrat stable et générable | `contracts/openapi/schema.yaml` (client Dart générable) |
| Évolution sans casser les anciennes versions de l'app | Préfixe `/api/v1/` ; versions parallèles possibles |
| Gestion fine des erreurs | Enveloppe avec `code` stable, `details` par champ |
| Listes sur réseau lent | Pagination bornée (max 100) |
| Dates sans ambiguïté de fuseau | ISO 8601 UTC |
| Pas de fuite d'identifiants | UUID publics |
| Débogage terrain | `X-Request-ID` de bout en bout |
| Notifications push | Module `notifications` réservé (enregistrement des appareils FCM/APNs) |

## À prévoir lors du développement du mobile (non implémenté)

- **Idempotence** des opérations critiques (paiements) : en-tête `Idempotency-Key` côté API, car
  un mobile peut rejouer une requête après une coupure réseau.
- **Version minimale de l'application** : endpoint `GET /api/v1/meta/` indiquant la version
  minimale acceptée (forcer la mise à jour si nécessaire).
- **Synchronisation hors ligne** : seulement si le besoin est confirmé (champs `updated_at`,
  résolution de conflits) ; ne pas l'anticiper sans besoin réel.
- **Fichiers** : envoi `multipart` ou URLs signées vers le stockage objet.
- **Stockage des jetons** : Keychain / Keystore (`flutter_secure_storage`).

## Architecture Flutter conseillée

Voir `mobile/ARCHITECTURE.md` : organisation par fonctionnalité (miroir des modules backend),
couches `data / domain / presentation`, client généré depuis OpenAPI.

## Règle de coordination

Toute modification de l'API passe par : code Django → `make schema` → PR (le diff du contrat est
relu) → mise à jour des clients (types TypeScript, client Dart). **Aucun client n'invente un
champ qui n'est pas dans le contrat.**
