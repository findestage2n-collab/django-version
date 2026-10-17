# 🏥 Hospital Management System

## Description

Hospital Management System est une plateforme web destinée à la gestion complète des activités hospitalières.

Le système permet la gestion :

- Des patients
- Des consultations
- Des rendez-vous
- Des hospitalisations
- Du laboratoire
- De l'imagerie médicale
- De la pharmacie
- Du stock
- De la facturation
- Des paiements
- De la caisse
- Des utilisateurs et permissions
- Des statistiques et rapports
- De l'audit des actions

L'application repose sur une architecture découplée :

- Frontend : React
- Backend : Django + Django REST Framework
- Base de données : PostgreSQL

---

# Architecture globale

```text
hospital_management/
│
├── frontend/
│
├── backend/
│
├── docs/
│
└── database/
```

## Frontend

```text
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
```

## Backend

```text
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
```

---

# Structure standard d'un module Backend

Chaque module doit respecter la structure suivante :

```text
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
```

---

# Structure standard d'un module Frontend

```text
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
```

---

# Conventions de développement

## 1. Architecture

### ✅ Obligatoire

Toute logique métier doit être placée dans les services.

### ❌ Interdit

Mettre la logique métier directement dans :

- les vues Django
- les contrôleurs API
- les composants React

Exemple :

```python
# Mauvais

class PatientView(APIView):
    def post(self, request):
        # 300 lignes de logique métier
```

```python
# Bon

class PatientView(APIView):
    def post(self, request):
        return PatientService.create_patient(request.data)
```

---

## 2. Principe de responsabilité unique

Une classe = une responsabilité.

### ✅ Correct

```text
PatientService
```

Responsable uniquement des patients.

### ❌ Incorrect

```text
PatientService
```

Qui :

- crée un patient
- calcule une facture
- gère le stock
- envoie des notifications

---

## 3. Nommage

### Applications Django

```text
patients
consultations
laboratoire
facturation
```

Toujours en minuscules.

### Services

```text
PatientService
FacturationService
ConsultationService
```

### Composants React

```text
PatientList.jsx
PatientForm.jsx
PatientDetail.jsx
```

---

# Gestion Git

## Branche protégée

### ❌ Interdit

Faire un push direct vers :

```text
main
```

ou

```text
master
```

---

### ✅ Obligatoire

Toute modification doit passer par une Pull Request.

Workflow :

```text
feature branch
↓
pull request
↓
review
↓
merge develop
↓
merge main
```

---

# Organisation des branches

Chaque module doit posséder au minimum 3 branches de développement.

Exemple pour le module Patients :

## 1. Branche Modèle

```text
patients-model
```

Contient :

- models
- migrations
- relations

---

## 2. Branche Métier

```text
patients-logic
```

Contient :

- services
- repositories
- validations
- règles métier

---

## 3. Branche Interface

```text
patients-ui
```

Contient :

- pages React
- composants React
- design
- navigation

---

Exemple :

```text
patients-model
patients-logic
patients-ui
```

```text
consultations-model
consultations-
