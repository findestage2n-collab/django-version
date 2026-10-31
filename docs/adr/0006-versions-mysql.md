# ADR 0006 - Cibler MySQL 8.4 LTS

**Statut** : accepté

**Contexte** : le README indiquait « MySQL 8.x ». D'après la page officielle des bases de
données prises en charge, Django 6.0 accepte MySQL 8.0, mais Django 6.1 retire 8.0 et ne liste
que MySQL 8.4.

**Décision** : développement, CI et production sur **MySQL 8.4 LTS**, jeu de caractères
`utf8mb4`, mode SQL strict. La production refuse de démarrer sur un autre moteur.

**Conséquences** : passage à Django 6.1 sans migration de base ; les tests locaux rapides
utilisent SQLite, d'où un job de CI MySQL pour détecter les écarts de comportement.

Source : https://code.djangoproject.com/wiki/SupportedDatabaseVersions
