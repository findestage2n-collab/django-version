# 🏥 Application de gestion des activités médicales

## 1. Présentation

**Hospital Management System** est une application web destinée à gérer les activités médicales et administratives d'un établissement de santé.

Les modules prévus comprennent :

- Patients et dossiers médicaux
- Consultations
- Rendez-vous
- Hospitalisations
- Laboratoire
- Imagerie médicale
- Pharmacie
- Gestion des stocks
- Facturation
- Paiements et caisse
- Utilisateurs, rôles et permissions
- Statistiques et rapports
- Journalisation et audit des actions

> **Périmètre à confirmer :** cette liste décrit les modules envisagés. Chaque module devra être précisé dans les spécifications fonctionnelles avant son développement.

## 2. Technologies retenues

| Partie | Technologie | Rôle |
|---|---|---|
| Backend | Python + Django 6.0.x | Logique serveur, modèles, règles métier et administration |
| API | Django REST Framework (DRF) | API REST consommée par le frontend |
| Frontend | Vue.js 3 | Interface utilisateur |
| Outil frontend | Vite | Serveur de développement et construction du frontend |
| CSS | Tailwind CSS, version stable 4.x | Mise en forme et interface responsive |
| Base de données | MySQL 8.x | Stockage des données applicatives |
| Gestion du code | Git + GitHub | Historique, branches et revues de code |


Les versions exactes devront être verrouillées dans les fichiers de dépendances du projet et mises à jour après vérification de leur compatibilité. Django 6.0 nécessite Python 3.12 ou supérieur. Pour la production, utiliser une version corrective prise en charge et maintenue, et non une version ancienne figée.

Références officielles :
- [Django — versions et téléchargements](https://www.djangoproject.com/download/)
- [Django REST Framework — notes de version](https://www.django-rest-framework.org/community/release-notes/)
- [Vue.js — documentation officielle](https://vuejs.org/guide/)
- [Tailwind CSS — installation](https://tailwindcss.com/docs/installation)
- [Vite — guide](https://vite.dev/guide/)
- [MySQL — documentation](https://dev.mysql.com/doc/)

## 3. Architecture générale

Le frontend Vue.js et le backend Django sont deux applications distinctes qui communiquent via l'API REST. MySQL est la base de données du backend.

```text
hospital-management/
├── frontend/                 # Vue.js 3 + Vite + Tailwind CSS
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── backend/                  # Django + Django REST Framework
│   ├── config/
│   ├── apps/
│   ├── shared/
│   ├── manage.py
│   └── requirements.txt
│
├── docs/                     # Spécifications, diagrammes et décisions
├── .gitignore
└── README.md
```

La base de données MySQL est un service séparé : il n'est pas nécessaire de créer un dossier `database/` contenant la base elle-même. Les scripts SQL éventuels, données de démonstration ou fichiers de configuration peuvent être rangés dans un dossier dédié si le projet en a réellement besoin. Les migrations Django restent la référence pour faire évoluer le schéma.

### 3.1 Structure du frontend

```text
frontend/
├── public/
└── src/
    ├── assets/
    ├── components/           # Composants réutilisables
    ├── layouts/              # Layouts de l'application
    ├── modules/
    │   ├── patients/
    │   ├── consultations/
    │   ├── rendezvous/
    │   ├── hospitalisations/
    │   ├── laboratoire/
    │   ├── imagerie/
    │   ├── pharmacie/
    │   ├── stock/
    │   ├── facturation/
    │   ├── paiements/
    │   ├── caisse/
    │   ├── rapports/
    │   └── administration/
    ├── router/               # Routes Vue Router
    ├── services/             # Appels HTTP vers l'API
    ├── stores/                # État partagé (Pinia si retenu)
    ├── composables/          # Fonctions réutilisables Vue
    ├── utils/
    ├── App.vue
    └── main.js
```

Cette organisation est une convention de départ, pas une obligation rigide. Si le projet est petit, éviter de multiplier les dossiers sans besoin concret. Vue Router et Pinia sont des choix recommandés pour la navigation et l'état partagé ; ils doivent être ajoutés explicitement aux dépendances.

### 3.2 Structure du backend

```text
backend/
├── config/                   # Paramètres et URLs du projet Django
├── apps/
│   ├── authentication/
│   ├── patients/
│   ├── consultations/
│   ├── rendezvous/
│   ├── hospitalisations/
│   ├── laboratoire/
│   ├── imagerie/
│   ├── pharmacie/
│   ├── stock/
│   ├── facturation/
│   ├── paiements/
│   ├── caisse/
│   ├── personnel/
│   ├── audittrail/
│   └── rapports/
├── shared/                   # Utilitaires réellement communs
├── manage.py
└── requirements.txt
```

Chaque application Django doit être ajoutée à la configuration Django (`INSTALLED_APPS`) et posséder ses migrations. Les applications listées sont prévisionnelles : créer uniquement celles dont le périmètre est validé.

## 4. Structure d'un module backend

Pour un module simple, la structure Django standard suffit :

```text
patients/
├── migrations/
├── tests/
├── admin.py
├── apps.py
├── models.py
├── serializers.py
├── services.py
├── urls.py
└── views.py
```

Si un module devient important, il peut être organisé en sous-packages :

```text
patients/
├── migrations/
├── models/
│   ├── __init__.py
│   └── patient.py
├── api/
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── services/
├── selectors/                # Requêtes de lecture complexes, si nécessaire
├── validators/
├── tests/
├── apps.py
└── admin.py
```

**Règles :**
- Les modèles décrivent les données, contraintes et relations.
- Les serializers DRF valident et transforment les données échangées par l'API.
- Les vues DRF gèrent la requête HTTP, les permissions et la réponse.
- Les services portent les règles métier lorsqu'elles sont suffisamment complexes ou réutilisées.
- Les repositories ne sont pas obligatoires : l'ORM Django suffit généralement. En ajouter uniquement si un besoin concret le justifie.
- Les selectors sont facultatifs et peuvent regrouper des requêtes de lecture complexes.
- Les signaux Django sont à utiliser avec discernement ; préférer un appel explicite dans le service lorsque cela rend le déroulement plus compréhensible.
- Les tests doivent couvrir les règles métier, permissions, validations et endpoints importants.

## 5. Structure d'un module frontend

```text
patients/
├── pages/
│   ├── PatientListView.vue
│   ├── PatientCreateView.vue
│   ├── PatientEditView.vue
│   └── PatientDetailView.vue
├── components/
│   ├── PatientForm.vue
│   ├── PatientInfoCard.vue
│   └── PatientTable.vue
├── services/
│   └── patient.service.js
├── stores/
│   └── patient.store.js
├── composables/
│   └── usePatient.js
└── routes.js
```

Les composants Vue utilisent l'extension **`.vue`** (et non `.jsx`, qui correspond à une autre manière d'écrire des composants). Les appels HTTP vers Django doivent être centralisés dans des services frontend, plutôt que dispersés dans chaque composant.

## 6. Conventions de développement

### 6.1 Séparation des responsabilités

Éviter de placer toute la logique métier dans une vue API ou un composant Vue. Les opérations simples peuvent rester simples ; les règles métier complexes, sensibles ou réutilisées doivent être isolées dans des services testables.

Exemple simplifié :

```python
# serializers.py
from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"
        # En production, préférer une liste explicite des champs exposés.
```

```python
# services.py
from .models import Patient


class PatientService:
    @staticmethod
    def create_patient(validated_data):
        # Ajouter ici les règles métier nécessaires.
        return Patient.objects.create(**validated_data)
```

```python
# views.py
from rest_framework import generics
from .models import Patient
from .serializers import PatientSerializer


class PatientListCreateAPIView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def perform_create(self, serializer):
        # Pour un exemple réel, appeler un service si des règles métier
        # doivent être appliquées. Ne jamais transmettre directement
        # request.data à la logique métier sans validation.
        serializer.save()
```

Cet exemple illustre la validation DRF, mais ne constitue pas une implémentation complète. En particulier, `fields = "__all__"` ne doit pas être utilisé sans examen dans une application médicale : choisir explicitement les champs accessibles et appliquer des permissions strictes. Lorsqu'un service crée le patient, il doit recevoir des données validées par le serializer et gérer les règles métier requises.

### 6.2 Principe de responsabilité unique

Une classe ou fonction doit avoir un rôle clairement délimité. Par exemple, `PatientService` ne devrait pas gérer en même temps les stocks, la facturation et les notifications. Une opération qui touche plusieurs domaines doit coordonner des services spécialisés et, si nécessaire, utiliser une transaction de base de données.

### 6.3 Nommage

- Applications Django et modules : `patients`, `consultations`, `facturation`.
- Classes Python : `PatientService`, `PatientSerializer`.
- Fonctions et variables Python : `create_patient`, `patient_id`.
- Composants Vue : `PatientListView.vue`, `PatientForm.vue`.
- Fichiers JavaScript : adopter une convention cohérente, par exemple `patient.service.js`.
- Les noms de routes API doivent suivre une convention cohérente, par exemple `/api/patients/` et `/api/patients/{id}/`.

## 7. Sécurité et données médicales

Les informations médicales sont sensibles. La sécurité doit être intégrée dès le début :

- Authentifier les utilisateurs et appliquer des permissions par rôle et par action.
- Vérifier les permissions côté serveur sur chaque endpoint ; masquer un bouton dans Vue ne constitue pas une protection.
- Limiter les champs que chaque rôle peut consulter ou modifier.
- Ne jamais enregistrer de mots de passe en clair, de secrets ou de clés dans Git.
- Utiliser des variables d'environnement pour les secrets et la configuration par environnement.
- Activer HTTPS en production, définir correctement les hôtes autorisés et configurer les cookies et les en-têtes de sécurité.
- Prévoir des sauvegardes testées, une procédure de restauration et une politique de conservation des données.
- Journaliser les actions sensibles sans recopier inutilement des informations médicales dans les journaux.
- Tester les accès croisés entre utilisateurs, patients et services.
- Utiliser uniquement des données fictives ou anonymisées dans les environnements de développement et de test.

Les règles applicables à la confidentialité, à la conservation et au partage des données doivent être vérifiées selon la réglementation applicable à l'établissement.

## 8. Gestion de Git et revue de code

### Branches recommandées

- `main` : version stable, protégée.
- `develop` : intégration des fonctionnalités, si l'équipe adopte ce modèle.
- `feature/<description>` : une fonctionnalité ou une tâche précise.
- `fix/<description>` : correction d'un défaut.
- `hotfix/<description>` : correction urgente à partir de la version stable.

Exemples :

```text
feature/patient-registration
feature/consultation-list
fix/patient-validation
```

### Workflow

```text
branche de travail
       ↓
commits ciblés
       ↓
Pull Request vers develop (si utilisé)
       ↓
revue + tests
       ↓
fusion dans develop
       ↓
validation de la version
       ↓
fusion dans main
```

Ne pas pousser directement sur `main` si la branche est protégée. Une Pull Request doit être examinée et les tests doivent réussir avant la fusion, selon les règles du dépôt.

**Important :** il n'est pas nécessaire de créer trois branches permanentes par module (`patients-model`, `patients-logic`, `patients-ui`). Cela multiplie les branches et complique les intégrations. Créer plutôt des branches temporaires correspondant à une tâche, même si celle-ci traverse plusieurs couches de l'application.

## 9. Qualité et tests

Avant une fusion, vérifier au minimum :

- Tests unitaires et tests API pour les règles métier.
- Tests des permissions et des rôles.
- Validations des entrées et gestion des erreurs.
- Tests des opérations sensibles (facturation, paiements, stock).
- Vérification du frontend et des parcours utilisateur concernés.
- Absence de secrets et de données médicales réelles dans le dépôt.
- Migrations testées sur une base de développement.

Les commandes exactes et les outils d'intégration continue seront définis lors de la mise en place du dépôt.

## 10. Mise en route

Les procédures d'installation seront ajoutées après la création des fichiers du projet. Elles devront couvrir séparément :

1. Les prérequis (Python compatible avec Django 6, Node.js compatible avec Vite, MySQL).
2. La création et l'activation de l'environnement virtuel Python.
3. L'installation des dépendances backend.
4. La configuration des variables d'environnement et de MySQL.
5. L'application des migrations et la création d'un compte administrateur.
6. L'installation des dépendances frontend.
7. Le lancement du serveur Django et du serveur Vite.
8. Les tests et la construction de production.

Ne pas publier de mots de passe, de clés secrètes ou de données réelles dans les exemples de configuration.

---

## Historique des décisions

- Backend : Django 6 + Django REST Framework.
- Frontend : Vue.js 3 + Vite.
- Styles : Tailwind CSS version stable.
- Base de données prévue : MySQL.
- Architecture : frontend séparé du backend, communication par API REST.
- Organisation : modules métier, avec une séparation des responsabilités adaptée à la complexité réelle.
