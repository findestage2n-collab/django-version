# Architecture Flutter conseillée

```text
mobile/
└── lib/
    ├── core/                  # transversal
    │   ├── api/               # client HTTP (Dio), intercepteurs (jeton, refresh), ApiException
    │   ├── auth/              # jetons (flutter_secure_storage), session
    │   ├── config/            # environnements (dev, prod), URL de l'API
    │   ├── error/             # traduction de l'enveloppe d'erreur {error:{code,message,details}}
    │   └── routing/           # navigation (go_router) et gardes de droits
    ├── features/              # miroir des modules backend
    │   └── patients/
    │       ├── data/          # sources distantes, DTO générés, repositories (implémentation)
    │       ├── domain/        # entités, interfaces de repository, cas d'usage
    │       └── presentation/  # écrans, widgets, état (Riverpod ou Bloc)
    ├── shared/                # widgets et thèmes réutilisables
    └── main.dart
```

## Règles

- **Client généré** depuis `contracts/openapi/schema.yaml` (ex. `openapi-generator`, générateur
  `dart-dio`) : on ne réécrit pas les DTO à la main.
- **Dépendances dirigées vers le domaine** : `presentation → domain ← data` (mêmes principes
  SOLID que le backend).
- **Droits** : lire `permissions` renvoyées par `/auth/me/` pour afficher/masquer des actions ;
  le serveur reste l'autorité.
- **Erreurs** : se baser sur `error.code`, jamais sur le texte du message.
- **Jetons** : stockage sécurisé du système ; rafraîchissement via `/auth/refresh/` (le refresh
  est à rotation : conserver le nouveau jeton à chaque appel).
- **Dates** : analyser l'ISO 8601 en UTC et afficher en heure locale.
- **En-têtes** : `X-Client: mobile`, `Accept-Language`, `X-Request-ID` (corrélation).
