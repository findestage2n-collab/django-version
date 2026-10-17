🏥 Hospital Management System
Description

Hospital Management System est une plateforme web destinée à la gestion complète des activités hospitalières.

Le système permet la gestion :

    Des patients
    Des consultations
    Des rendez-vous
    Des hospitalisations
    Du laboratoire
    De l'imagerie médicale
    De la pharmacie
    Du stock
    De la facturation
    Des paiements
    De la caisse
    Des utilisateurs et permissions
    Des statistiques et rapports
    De l'audit des actions

L'application repose sur une architecture découplée :

    Frontend : React
    Backend : Django + Django REST Framework
    Base de données : PostgreSQL

Architecture globale

hospital_management/
│
├── frontend/
│
├── backend/
│
├── docs/
│
└── database/

Frontend

frontend/
│
├── src/
│
├── modules/
│   ├── patients/
│   ├── consultations/
│   ├── hospitalisations/
│   ├── laboratoire/
│   ├── pharmacie/
│   ├── stock/
│   ├── facturation/
│   ├── rapports/
│   └── administration/
│
├── shared/
├── layouts/
├── router/
└── assets/

Backend

backend/
│
├── config/
│
├── apps/
│   ├── authentication/
│   ├── patients/
│   ├── consultations/
│   ├── rendezvous/
│   ├── hospitalisations/
│   ├── laboratoire/
│   ├── pharmacie/
│   ├── stock/
│   ├── facturation/
│   ├── paiements/
│   ├── caisse/
│   ├── personnel/
│   ├── audittrail/
│   └── rapports/
│
├── shared/
│
└── manage.py

Structure standard d'un module Backend

Chaque module doit respecter la structure suivante :

patients/
│
├── models/
│
├── api/
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── services/
│
├── repositories/
│
├── selectors/
│
├── validators/
│
├── tests/
│
├── signals.py
├── apps.py
└── admin.py

Structure standard d'un module Frontend

patients/
│
├── pages/
│
├── components/
│
├── services/
│
├── hooks/
│
├── store/
│
└── routes.jsx

Conventions de développement
1. Architecture
✅ Obligatoire

Toute logique métier doit être placée dans les services.
❌ Interdit

Mettre la logique métier directement dans :

    les vues Django
    les contrôleurs API
    les composants React

Exemple :

# Mauvais

class PatientView(APIView):
    def post(self, request):
        # 300 lignes de logique métier

# Bon

class PatientView(APIView):
    def post(self, request):
        return PatientService.create_patient(request.data)

2. Principe de responsabilité unique

Une classe = une responsabilité.
✅ Correct

PatientService

Responsable uniquement des patients.
❌ Incorrect

PatientService

Qui :

    crée un patient
    calcule une facture
    gère le stock
    envoie des notifications

3. Nommage
Applications Django

patients
consultations
laboratoire
facturation

Toujours en minuscules.
Services

PatientService
FacturationService
ConsultationService

Composants React

PatientList.jsx
PatientForm.jsx
PatientDetail.jsx

Gestion Git
Branche protégée
❌ Interdit

Faire un push direct vers :

main

ou

master

✅ Obligatoire

Toute modification doit passer par une Pull Request.

Workflow :

feature branch
↓
pull request
↓
review
↓
merge develop
↓
merge main

Organisation des branches

Chaque module doit posséder au minimum 3 branches de développement.

Exemple pour le module Patients :
1. Branche Modèle

patients-model

Contient :

    models
    migrations
    relations

2. Branche Métier

patients-logic

Contient :

    services
    repositories
    validations
    règles métier

3. Branche Interface

patients-ui

Contient :

    pages React
    composants React
    design
    navigation

Exemple :

patients-model
patients-logic
patients-ui

consultations-model
consultations-
