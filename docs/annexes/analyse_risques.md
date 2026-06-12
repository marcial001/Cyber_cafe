# Annexe D — Analyse des risques

| ID | Risque | Probabilité | Impact | Score | Mitigation |
|----|--------|-------------|--------|-------|------------|
| R01 | Retard sur le backend bloque l'UI | Moyenne | Élevé | 12 | Prioriser API + mocks ; chemin critique |
| R02 | Panne SQLite (corruption fichier) | Faible | Élevé | 8 | Sauvegardes `data/` ; transactions COMMIT |
| R03 | Entrées utilisateur malveillantes | Moyenne | Moyen | 9 | Pydantic, pas de SQL brut dynamique, ORM léger |
| R04 | API indisponible au démarrage Electron | Moyenne | Moyen | 9 | Message clair ; script de lancement ordonné |
| R05 | Incompatibilité versions Python/Node | Faible | Moyen | 6 | README avec versions testées |
| R06 | Erreur de calcul tarif nuit | Moyenne | Moyen | 9 | Tests unitaires `Pricing` ; règles documentées |
| R07 | Perte de recettes si crash pendant session | Faible | Élevé | 8 | Session reste `en_cours` ; reprise manuelle |
| R08 | Plagiat / non-originalité | Faible | Critique | 10 | Code commenté, compréhension oral |
| R09 | Coupure électrique (contexte local) | Moyenne | Moyen | 9 | SQLite local ; pas de dépendance cloud |
| R10 | Surcharge cognitive stack Electron+Python | Moyenne | Moyen | 9 | Architecture documentée ; formation ciblée |

**Matrice :** Probabilité (1-3) × Impact (1-4) = Score. Seuil d'action : ≥ 9.
