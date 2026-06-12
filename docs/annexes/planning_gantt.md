# Annexe C — Planning projet (4 semaines)

## C.1 Diagramme de Gantt

```mermaid
gantt
    title CyberCafé Manager — Planning 4 semaines
    dateFormat  YYYY-MM-DD
    axisFormat  %d/%m

    section Analyse
    Étude méthodologique           :a1, 2026-06-01, 2d
    Collecte besoins + MoSCoW      :a2, after a1, 3d
    Cahier des charges             :a3, after a2, 2d
    Jalons J1 livrables analyse    :milestone, m1, 2026-06-08, 0d

    section Conception
    MCD/MLD + SQL                  :b1, 2026-06-09, 3d
    UML complet                    :b2, after b1, 3d
    Architecture + choix techno    :b3, after b2, 2d
    Jalons J2 conception validée   :milestone, m2, 2026-06-15, 0d

    section Développement
    Backend API Python             :c1, 2026-06-16, 4d
    Frontend Electron              :c2, after c1, 4d
    Intégration + tests            :c3, after c2, 3d
    Jalons J3 MVP fonctionnel      :milestone, m3, 2026-06-27, 0d

    section Clôture
    Rapports + faisabilité SND30   :d1, 2026-06-28, 3d
    Préparation soutenance         :d2, after d1, 2d
    Jalons J4 livraison finale     :milestone, m4, 2026-07-02, 0d
```

## C.2 Décomposition des tâches et charges

| ID | Tâche | Charge (h) | Responsable | Livrable |
|----|-------|------------|-------------|----------|
| T01 | Comparatif Cascade/Agile/Itérative | 8 | Étudiant | Section CDC §1 |
| T02 | Parties prenantes et besoins | 12 | Étudiant | Doc collecte besoins |
| T03 | Référentiel MoSCoW | 10 | Étudiant | Annexe A |
| T04 | Cahier des charges | 16 | Étudiant | PDF CDC |
| T05 | MCD/MLD + scripts SQL | 14 | Étudiant | schema.sql, seed.sql |
| T06 | Diagrammes UML | 12 | Étudiant | Annexe B |
| T07 | Architecture multicouche | 10 | Étudiant | Doc technique §5 |
| T08 | Backend FastAPI | 24 | Étudiant | Dossier backend/ |
| T09 | Frontend Electron | 20 | Étudiant | Dossier frontend/ |
| T10 | Tests et corrections | 12 | Étudiant | Jeu d'essais |
| T11 | Rapport technique | 18 | Étudiant | PDF rapport |
| T12 | Rapport faisabilité + SND30 | 10 | Étudiant | PDF faisabilité |
| T13 | Soutenance (slides) | 8 | Étudiant | PPTX |
| **Total** | | **174 h** | | |

## C.3 Chemin critique

**T01 → T02 → T03 → T05 → T08 → T09 → T10 → T11 → T13**

Toute retard sur la modélisation BDD (T05) ou le backend (T08) impacte directement l'intégration Electron et la rédaction finale. La conception UML (T06) peut partiellement chevaucher T05 si le MCD est validé en amont.

## C.4 Jalons

| Jalon | Date | Critère de succès |
|-------|------|-------------------|
| J1 | Semaine 1 | Besoins validés, MoSCoW signé, CDC v0.9 |
| J2 | Semaine 2 | MCD/MLD + UML + architecture approuvés |
| J3 | Semaine 3 | Démo live : session complète + ticket + stats |
| J4 | Semaine 4 | Dossier complet PDF + code GitHub + soutenance prête |
