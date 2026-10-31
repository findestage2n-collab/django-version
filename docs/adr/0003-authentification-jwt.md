# ADR 0003 - Authentification JWT pour web et mobile

**Statut** : accepté (à réévaluer avant la mise en production)

**Décision** : SimpleJWT. Jeton d'accès de 15 minutes ; jeton de rafraîchissement de 7 jours,
**à rotation** avec mise en liste noire de l'ancien ; limitation de débit sur la connexion.
Les rôles sont des groupes Django, les droits des permissions Django.

**Web (v1)** : jeton d'accès en mémoire, jeton de rafraîchissement en `sessionStorage`, CSP
stricte. **Risque** : un XSS pourrait lire le jeton de rafraîchissement.
**Évolution recommandée** : cookie `httpOnly; Secure; SameSite=Strict` pour le refresh du web
(le mobile continue d'utiliser le corps JSON et le stockage sécurisé du système).

**Mobile** : Keychain / Keystore.

**Conséquences** : API sans état (scalable) ; la révocation immédiate d'un jeton d'accès n'est
pas possible avant son expiration (courte durée volontaire).
