"""Graphe des dépendances AUTORISÉES entre modules (vérifié par tests/architecture).

Un module ne peut importer que `apps.<autre>.public` et seulement si <autre> figure ici.
Le graphe doit rester sans cycle.
"""

MODULE_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "accounts": (),
    "audit": (),
    "personnel": ("accounts",),
    "patients": ("audit",),
    "rendezvous": ("patients", "personnel"),
    "consultations": ("patients", "personnel", "rendezvous", "audit"),
    "hospitalisations": ("patients", "personnel", "audit"),
    "laboratoire": ("patients", "consultations", "personnel"),
    "pharmacie": ("patients", "consultations", "audit"),
    "facturation": ("patients", "audit"),
    "paiements": ("facturation", "audit"),
    "rapports": ("patients", "consultations", "facturation", "paiements"),
    "notifications": ("accounts",),
}
