# ADR 0005 - Services, selectors et ports

**Statut** : remplacé par l'[ADR 0007](0007-clean-architecture.md) (les `services/` et `selectors/` ont été supprimés)

**Décision** : les écritures et règles métier vivent dans des **services** (classes à
dépendances injectées, transactions explicites) ; les lectures dans des **selectors**. Pas de
couche « repository » générique (l'ORM Django suffit). Un **port** (interface `Protocol`) n'est
introduit que lorsqu'une dépendance doit être remplaçable ou isolée (ex. `AuditPort`).
Les signaux Django ne sont pas utilisés pour la logique métier ; on utilise des événements de
domaine explicites (`core/events.py`).

**Conséquences** : tests unitaires simples (faux injectés) ; moins d'abstractions inutiles ;
discipline requise pour ne pas mettre de règle métier dans les vues.
