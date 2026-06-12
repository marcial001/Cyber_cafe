# Annexe E — Document de collecte des besoins

## E.1 Parties prenantes

| Partie prenante | Rôle | Influence | Intérêt |
|-----------------|------|-----------|---------|
| Gérant du cybercafé | Utilisateur principal, décision achat | Élevée | Suivi postes, recettes, tickets |
| Clients du cybercafé | Bénéficiaires indirects | Faible | Tarifs justes, attente réduite |
| Employé / caissier | Opérateur quotidien | Moyenne | Interface simple, peu d'erreurs |
| Propriétaire de la salle | Sponsor économique | Élevée | ROI, réduction des pertes |
| Enseignant (Dr. MALONG) | Évaluateur, validation périmètre | Élevée | Conformité cahier ENSP |
| Jury de soutenance | Évaluateur final | Moyenne | Qualité technique et orale |
| Équipe de développement | Réalisateur | Élevée | Livrables dans les délais |
| Fournisseur électricité / FAI | Contrainte externe | Faible | Continuité de service |

## E.2 Attentes et contraintes par partie prenante

### Gérant
- **Attentes :** vue temps réel des postes ; facturation automatique ; historique du jour ; tarifs étudiant/normal/nuit.
- **Contraintes :** peu de formation informatique ; PC modeste ; connexion parfois instable.

### Clients
- **Attentes :** transparence du temps facturé ; ticket en fin de session.
- **Contraintes :** ne pas interagir avec l'application (usage via gérant).

### Enseignant / ENSP
- **Attentes :** UML, BDD 3NF, rapport 15-25 pages, code GitHub, démo live.
- **Contraintes :** délai 4 semaines ; anti-plagiat.

### Technique
- **Attentes :** Electron + Python comme choix validé.
- **Contraintes :** SQLite ; pas de dépendance serveur cloud payant.

## E.3 Besoins fonctionnels synthétisés

1. Visualiser l'état des postes (libre/occupé).
2. Gérer le cycle de vie d'une session (démarrage, chronomètre, arrêt).
3. Calculer et enregistrer le montant dû.
4. Produire un ticket de caisse.
5. Afficher les statistiques journalières.
6. Paramétrer les tarifs (fichier + base).

## E.4 Besoins non fonctionnels

| Catégorie | Exigence |
|-----------|----------|
| Performance | Rafraîchissement tableau de bord ≤ 2 s |
| Fiabilité | Pas de crash sur entrées invalides |
| Utilisabilité | Interface en français, lisible, contrastes adaptés |
| Maintenabilité | Code POO, couches séparées, DRY |
| Sécurité | Validation serveur systématique |
| Portabilité | Windows 10+ (cible principale) |
| Traçabilité | Sessions historisées en BDD |

## E.5 Techniques de collecte utilisées

- Analyse du cahier des projets ENSP 2025/2026.
- Entretien simulé / observation d'un cybercafé de quartier (Douala).
- Benchmark de solutions manuelles (cahier papier, Excel).
- Revue des consignes supplémentaires du module.
