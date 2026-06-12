# Annexe A — Référentiel des exigences (MoSCoW)

**Projet :** CyberCafé Manager  
**Version :** 1.0  
**Date :** Juin 2026

---

## Must have (indispensables)

| ID | Description | Source | Critères de validation |
|----|-------------|--------|------------------------|
| EX-M01 | Afficher le tableau de bord avec l'état libre/occupé de chaque poste | Cahier ENSP + Gérant | Tous les postes actifs visibles ; état mis à jour en temps réel (≤ 2 s) |
| EX-M02 | Démarrer une session sur un poste libre avec sélection du tarif | Cahier ENSP | Impossible de démarrer si poste occupé ; tarif enregistré en BDD |
| EX-M03 | Arrêter une session et afficher le chronomètre en temps réel | Cahier ENSP | Chronomètre HH:MM:SS ; arrêt calcule durée et montant |
| EX-M04 | Calcul automatique du montant selon durée et tarif horaire | Cahier ENSP + Gérant | Formule : (secondes/3600) × prix/heure ; arrondi cohérent |
| EX-M05 | Enregistrer chaque session terminée en base SQLite | Cahier ENSP | Ligne `sessions` avec début, fin, durée, montant, statut |
| EX-M06 | Générer un ticket de caisse unique par session | Cahier ENSP | Numéro unique `TK-XXXXXX` ; affichage imprimable |
| EX-M07 | Gérer trois tarifs : étudiant, normal, nuit | Cahier ENSP | Tarifs configurables ; code validé côté serveur |
| EX-M08 | Statistiques journalières : recettes et postes les plus utilisés | Cahier ENSP | Agrégation par date du jour ; top postes par nombre de sessions |
| EX-M09 | Validation stricte des entrées (ne pas faire confiance au client) | Consigne projet | Pydantic + contrôles API ; messages d'erreur explicites |
| EX-M10 | Interface graphique desktop via Electron | Choix étudiant | Application lance sans erreur ; communication API sécurisée (preload) |
| EX-M11 | API REST Python documentée | Choix étudiant | Endpoints `/api/v1/*` ; Swagger `/docs` |
| EX-M12 | Scripts SQL schéma + peuplement | Cahier ENSP | `schema.sql` et `seed.sql` exécutables sans erreur |

## Should have (importantes)

| ID | Description | Source | Critères de validation |
|----|-------------|--------|------------------------|
| EX-S01 | Fichier JSON de configuration des tarifs | Livrable spécifique | `config/tarifs.json` documenté et aligné avec BDD |
| EX-S02 | Tableau de bord esthétique adapté au contexte local | Cahier ENSP | Charte couleurs lisible ; textes en français |
| EX-S03 | Synchronisation automatique du tableau de bord (polling 1 s) | UX | Rafraîchissement sans rechargement manuel |
| EX-S04 | README d'installation complet | Cahier ENSP | Procédure reproductible sur machine vierge |
| EX-S05 | Architecture en couches documentée | Consigne suppl. | Schéma présentation → API → services → repositories |
| EX-S06 | Diagrammes UML complets en annexe | Consigne suppl. | Cas d'utilisation, 2 séquences, classes, activités |
| EX-S07 | Rapport de faisabilité et alignement SND30 | Consigne suppl. | Documents séparés validés par encadreur |

## Could have (souhaitables)

| ID | Description | Source | Critères de validation |
|----|-------------|--------|------------------------|
| EX-C01 | Export PDF des tickets | Gérant | Bouton export (non bloquant soutenance) |
| EX-C02 | Historique des sessions sur période configurable | Gérant | Filtre date début/fin |
| EX-C03 | Mode sombre / clair | UX | Bascule thème |
| EX-C04 | Sauvegarde automatique de la BDD | Maintenance | Copie quotidienne `data/` |
| EX-C05 | Authentification gérant simple | Sécurité | Login mot de passe local |

## Won't have (hors périmètre v1)

| ID | Description | Source | Justification |
|----|-------------|--------|---------------|
| EX-W01 | Paiement Mobile Money intégré | Évolution | Complexité réglementaire ; hors délai 4 semaines |
| EX-W02 | Application mobile Android/iOS | Évolution | Périmètre desktop cybercafé |
| EX-W03 | Gestion multi-établissements | Évolution | Un seul site pilote |
| EX-W04 | Facturation électronique certifiée DGI | Légal | Hors scope académique |
| EX-W05 | Monitoring réseau des PC clients | Technique | Nécessite agents système sur chaque poste |
