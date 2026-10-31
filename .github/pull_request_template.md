## Objet
<!-- Quelle tâche ? Quelle décision d'architecture ? -->

## Liste de contrôle
- [ ] Tests ajoutés/mis à jour (règles métier, permissions, API)
- [ ] `make check` passe (ruff, tests d'architecture, typecheck)
- [ ] Contrat OpenAPI régénéré si l'API change (`make schema`)
- [ ] Aucune donnée médicale réelle ni secret dans le diff
- [ ] Import entre modules uniquement via `apps.<module>.public`
