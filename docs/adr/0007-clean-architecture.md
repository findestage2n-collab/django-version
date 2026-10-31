# ADR 0007 - Clean Architecture

**Statut** : accepté (remplace l'ADR 0005)

**Contexte** : la première version posait les règles métier dans des `services/` qui manipulaient
directement les modèles Django. Le métier dépendait donc du framework et de la base de données :
impossible de le tester sans base, difficile de changer de technologie, et le moindre changement
d'un modèle ORM traversait tout le code.

**Décision** : chaque module est organisé en couches concentriques ; **les dépendances vont
uniquement vers l'intérieur**.

| Couche | Dossier | Contenu | Peut importer |
|---|---|---|---|
| 1. Domaine | `domain/` | Entités, règles métier, erreurs, événements, ports (interfaces) | Python standard, `core.kernel` |
| 2. Cas d'usage | `application/` | Actions de l'application (`RegisterPatient`…) | `domain`, `core.kernel` |
| 3. Adaptateurs | `infrastructure/` (sortie) · `api/` (entrée) | ORM, repositories · serializers, vues DRF | tout ce qui est plus intérieur ; `api` n'importe jamais `infrastructure` |
| Câblage | `composition.py` | Choisit les implémentations concrètes (injection de dépendances) | tout |

- Les **ports** (`PatientRepository`, `AuditTrail`, `UnitOfWork`, `EventPublisher`, `Clock`) sont
  des `Protocol` appartenant au côté intérieur ; l'infrastructure les implémente (inversion des
  dépendances, le « D » de SOLID).
- Le **noyau** `core/kernel/` est du Python pur (erreurs, port, horloge, événement).
  `core/infrastructure/` et `core/interface/` contiennent ce qui dépend de Django/DRF.
- Les anciens dossiers `services/`, `selectors/` et `models/` sont **supprimés** ; `models.py`
  n'est plus qu'un relais exigé par Django vers `infrastructure/models.py`.
- La règle est **exécutée** par `backend/tests/architecture/test_clean_architecture.py` (analyse
  des imports). Une violation fait échouer les tests et la CI.

**Exception assumée** : l'authentification (connexion, jetons JWT, `request.user`) reste adossée à
Django auth et SimpleJWT dans la couche `api` du module `accounts`. L'envelopper dans des ports
serait de la sur-ingénierie ; la création de compte, elle, suit l'architecture (`CreateUser`).

**Conséquences** : +1 fichier de câblage par module et un peu plus de code (entité + ORM +
mapper) ; en échange, des tests du métier instantanés sans base, un framework remplaçable, et des
frontières vérifiées automatiquement.
