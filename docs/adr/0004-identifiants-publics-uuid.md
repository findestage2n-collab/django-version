# ADR 0004 - Identifiants publics UUID

**Statut** : accepté

**Contexte** : des identifiants entiers séquentiels dans les URL permettent d'énumérer des
dossiers de patients (faille IDOR si une permission est oubliée). Des UUID comme clés primaires
fragmentent les index InnoDB.

**Décision** : clé primaire entière interne + colonne `public_id` (UUID, unique) seule exposée
par l'API (`core.infrastructure.models.PublicIdModel`).

**Conséquences** : bonnes performances MySQL et pas d'énumération ; les clés étrangères restent
entières en base ; l'API et les clients n'utilisent que `public_id`.
