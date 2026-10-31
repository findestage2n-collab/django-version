# ADR 0009 - Bases relationnelles interchangeables

**Statut** : accepté

**Remplace** : ADR 0006 pour le choix du moteur en production ; MySQL 8.4 reste pris en charge,
mais n'est plus le seul moteur autorisé.

**Contexte** : l'application devait permettre de choisir une base selon l'environnement. Django
prend en charge plusieurs moteurs relationnels via son ORM, mais la production imposait MySQL.
Cette configuration ne rendait pas PostgreSQL sélectionnable et ne permettait pas de valider
l'interchangeabilité dans la CI.

**Décision** : accepter SQLite, MySQL et PostgreSQL comme moteurs configurables par
`DATABASE_URL`, y compris en production. Les pilotes MySQL et PostgreSQL sont déclarés
séparément ; l'image de production les installe tous les deux. La CI exécute les tests avec
SQLite, MySQL et PostgreSQL. SQLite en production est réservé aux déploiements légers à faible
concurrence. MongoDB est hors périmètre : il nécessitera un adaptateur et une stratégie de
persistance dédiés, ce n'est pas une URL Django interchangeable.

**Conséquences** : changer de moteur ne transfère pas automatiquement les données. Il faut
appliquer les migrations et organiser explicitement l'export/import des données. Les
différences de comportement sont couvertes par les tests sur chaque moteur SQL.
