# ADR 0001 - Monolithe modulaire avec frontières testées

**Statut** : accepté

**Contexte** : une équipe réduite, un domaine médical aux nombreuses interactions (patient,
consultation, facturation, pharmacie). Des microservices coûteraient en exploitation et en cohérence
des données ; un monolithe sans règles dérive en couplage généralisé.

**Décision** : un seul déploiement Django, découpé en modules (`apps/*`) qui ne communiquent
que par `public.py` et des événements de domaine. Les règles (dépendances déclarées, sans cycle,
`core` indépendant) sont vérifiées par des tests.

**Conséquences** : déploiement et transactions simples ; extraction ultérieure d'un module
possible (frontières déjà tracées) ; coût : discipline d'écriture de `public.py` et des tests
d'architecture à maintenir.
