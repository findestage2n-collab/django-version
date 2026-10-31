# ADR 0008 - Fonctionnement sans Internet

**Statut** : accepté

**Contexte** : le système peut être installé dans un établissement dont la connexion à Internet
est absente ou instable. Il doit fonctionner sur le réseau local (LAN).

**Décision** : à l'exécution, **aucune dépendance obligatoire à Internet**.

- Plus de Celery ni de Redis : événements en mémoire (`core/infrastructure/events.py`), cache en
  mémoire (dev) ou fichiers (prod). Une file de tâches pourra être ajoutée plus tard derrière le
  port `EventPublisher`, en base de données plutôt qu'avec un service réseau.
- Documentation d'API (Swagger) servie localement (`drf-spectacular-sidecar`), fichiers statiques
  servis par WhiteNoise, aucune police, script ni image chargés depuis un CDN (frontend vérifié).
- E-mail écrit dans un fichier par défaut ; SMS/e-mail réels = adaptateurs **optionnels** derrière un port.
- Installation hors ligne : `scripts/offline/prepare-bundle.sh` (avec Internet, une fois) puis
  `scripts/offline/install-offline.sh` (sans Internet).
- Test d'architecture : `base.txt` ne doit contenir ni broker ni SDK cloud.

**Hors périmètre (à décider séparément)** : un poste client qui continue à saisir pendant une
coupure du **réseau local** (application web installable avec file d'attente locale puis
synchronisation) ; c'est un projet à part entière (résolution de conflits sur des données médicales).

**Conséquences** : un seul serveur applicatif + MySQL suffisent ; la montée en charge passe par la
base de données et plusieurs processus gunicorn avant d'envisager un broker.
