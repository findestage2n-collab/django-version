# ADR 0002 - API versionnée et contrat OpenAPI

**Statut** : accepté

**Contexte** : deux clients (Vue puis Flutter) évoluent à des rythmes différents ; une application
mobile publiée ne peut pas être mise à jour instantanément.

**Décision** : préfixe `/api/v1/` ; schéma OpenAPI généré par drf-spectacular et versionné dans
`contracts/openapi/`. La CI vérifie que le fichier correspond au code et que les types
TypeScript sont à jour. Le client Dart sera généré depuis le même fichier.

**Conséquences** : tout changement d'API est visible en revue ; un changement incompatible exige
`/api/v2/`. Coût : régénérer le contrat à chaque modification de serializer.
