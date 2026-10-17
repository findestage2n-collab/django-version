# django-version
la version django de l'application de gestion hospitaliere concut avec php/laravel
nous allons adopter une architecture modulaire par domaine métier. On organise le code autour des fonctionnalités médicales et non autour des types de fichiers.
sturcture  : Monolithe 

hospital_management/
│
├── backend/
│
│   ├── config/
│   │   ├── settings/
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── apps/
│   │
│   │   ├── authentication/
│   │   ├── patients/
│   │   ├── consultations/
│   │   ├── rendezvous/
│   │   ├── hospitalisations/
│   │   ├── laboratoire/
│   │   ├── pharmacie/
│   │   ├── stocks/
│   │   ├── facturation/
│   │   ├── paiements/
│   │   ├── caisse/
│   │   ├── personnel/
│   │   ├── rapports/
│   │   ├── notifications/
│   │   └── audittrail/
│   │
│   ├── shared/
│   │
│   │   ├── services/
│   │   ├── permissions/
│   │   ├── exceptions/
│   │   ├── mixins/
│   │   ├── utils/
│   │   └── constants/
│   │
│   ├── media/
│   ├── static/
│   └── manage.py
│
├── frontend/
│
│   ├── src/
│   │
│   ├── modules/
│   │   ├── patients/
│   │   ├── consultations/
│   │   ├── laboratoire/
│   │   ├── pharmacie/
│   │   ├── facturation/
│   │   ├── caisse/
│   │   ├── rapports/
│   │   └── administration/
│   │
│   ├── components/
│   ├── pages/
│   ├── layouts/
│   ├── services/
│   ├── router/
│   ├── store/
│   └── assets/
├── database/
└── docs/

structure : d'un module 
patients/
│
├── migrations/
│
├── api/
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── services/
│   ├── patient_service.py
│   └── patient_export_service.py
│
├── repositories/
│   └── patient_repository.py
│
├── models/
│   ├── patient.py
│   ├── contact.py
│   └── assurance.py
│
├── selectors/
│   └── patient_selector.py
│
├── permissions/
│
├── validators/
│
├── tests/
│
├── admin.py
├── apps.py
└── signals.py

struture frontend : 
frontend/src/
│
├── modules/
│
│   ├── patients/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── routes.jsx
│   │
│   ├── consultations/
│   ├── laboratoire/
│   ├── pharmacie/
│   ├── facturation/
│   └── personnel/
│
├── shared/
│   ├── components/
│   ├── hooks/
│   ├── services/
│   └── utils/
│
└── layouts/
