# RAPPORT TECHNIQUE

## Conception et réalisation de CyberCafé Manager

---

**Établissement :** ENSP Douala — Génie Logiciel N3  
**Encadreur :** Dr. MALONG Yannick  
**Étudiant(s) :** *[À compléter]*  
**Année académique :** 2025/2026  
**Date :** Juin 2026

---

## Résumé exécutif

Ce rapport présente la conception et l'implémentation d'une application de gestion de cybercafé répondant au sujet n°03 du cahier des projets ENSP. La solution combine une interface **Electron** et une API **Python FastAPI** avec persistance **SQLite**. Les objectifs — suivi des postes, facturation automatique, tickets et statistiques — sont atteints via une architecture multicouche respectant les principes POO, DRY, SOLID et une validation systématique des entrées utilisateur.

**Mots-clés :** cybercafé, Electron, FastAPI, SQLite, UML, facturation horaire, Cameroun.

---

## Table des matières

1. Introduction  
2. Analyse du problème et des besoins  
3. Conception du système  
4. Implémentation  
5. Tests et validation  
6. Résultats et limites  
7. Conclusion et perspectives  
8. Bibliographie  
9. Journal des modifications (incrément — juin 2026)  

---

## 1. Introduction

### 1.1 Contexte

Le secteur informel des cybercafés au Cameroun souffre d'un déficit d'outils numériques adaptés et abordables. Le cahier des projets de l'ENSP identifie cette problématique comme cas d'école pertinent pour le cycle complet de génie logiciel.

### 1.2 Problématique

Comment concevoir un système fiable permettant au gérant de suivre en temps réel l'occupation des postes, de calculer automatiquement les montants dus selon des tarifs multiples, et de produire des statistiques journalières sans perte de recettes ?

### 1.3 Objectifs du projet

- Répondre aux six fonctionnalités du cahier ENSP.
- Respecter les consignes supplémentaires (méthodologie, MoSCoW, UML étendu, architecture, faisabilité, SND30).
- Produire des livrables séparés : cahier des charges, documentation technique, rapport technique.

### 1.4 Méthodologie

Approche **itérative** sur 4 semaines (cf. cahier des charges §2) avec jalons hebdomadaires et intégration continue du backend avant l'UI.

---

## 2. Analyse du problème et des besoins

### 2.1 État de l'existant

Dans l'existant manuel, le gérant note l'heure de début sur papier, estime la durée à la fin, applique mentalement le tarif (étudiant ou normal) et encaisse. Les erreurs surviennent lors des pics d'affluence ou du changement de tarif de nuit.

### 2.2 Parties prenantes

Gérant, clients, encadreur, jury — détail en Annexe E.

### 2.3 Exigences

Le référentiel MoSCoW (Annexe A) recense 12 exigences Must have, dont la validation serveur (EX-M09) et les six modules fonctionnels ENSP.

### 2.4 Contraintes

Matériel local, offline, délai 4 semaines, stack Electron + Python imposée par l'étudiant et validée techniquement.

---

## 3. Conception du système

### 3.1 Modèle de données

Trois tables normalisées 3NF et une vue `v_postes_etat`. Le MLD est implémenté dans `database/schema.sql`. Les tarifs sont référencés par code (`etudiant`, `normal`, `nuit`).

### 3.2 Modélisation UML

- **Cas d'utilisation :** gérant — consulter tableau de bord, démarrer/arrêter session, ticket, statistiques.
- **Séquences :** démarrage et arrêt (Annexe B).
- **Classes :** entités + services + repositories + domaine Pricing.
- **Activités :** flux session complet.

### 3.3 Architecture

Architecture **client-serveur local** en cinq couches (présentation, API, services, repositories, SQLite). Patrons Repository et Service Layer.

**Comparaison :** le monolithe Tkinter aurait accéléré un prototype mais nuirait à la séparation des responsabilités exigée en génie logiciel. Les microservices sont exclus au profit d'une architecture client-serveur locale maîtrisée.

### 3.4 Choix technologiques

Electron pour l'IHM moderne ; FastAPI pour la validation native et la documentation Swagger ; SQLite pour zéro administration.

---

## 4. Implémentation

### 4.1 Backend Python

- **Point d'entrée :** `app/main.py` avec lifespan initialisant la BDD.
- **SessionService :** règles « poste libre », « session en cours », calcul et ticket.
- **Pricing :** fonction pure testable `calculer_montant`.

Extrait de logique métier :

```python
def calculer_montant(duree_secondes: int, prix_par_heure: float) -> float:
    heures = duree_secondes / 3600.0
    return round(heures * prix_par_heure, 0)
```

### 4.2 Frontend Electron

- IPC via `preload.js` exposant `window.cybercafe`.
- `app.js` : rendu grille, chronomètres, gestion erreurs API.
- Pas de `nodeIntegration` dans le renderer.

### 4.3 Configuration

`config/tarifs.json` documente les tarifs métier ; `seed.sql` les injecte en base.

### 4.4 Principes de qualité

| Principe | Application concrète |
|----------|---------------------|
| POO | Services et repositories instanciés |
| DRY | Calcul tarif unique dans `pricing.py` |
| Ergonomie | UI 2025 inspirée CyberCafePro, navigation par zones |
| Don't trust input | Pydantic + vérifications IPC |

---

## 5. Tests et validation

### 5.1 Tests manuels

| Scénario | Résultat attendu | Statut |
|----------|------------------|--------|
| Démarrer session poste libre | Session en_cours | OK |
| Démarrer sur poste occupé | Erreur 409 | OK |
| Arrêter session | Montant + ticket TK-XXXXXX | OK |
| Tarif code invalide | Erreur 400 | OK |
| Stats journalières | Recettes et top postes | OK |

### 5.2 Critères de validation MoSCoW

Les exigences EX-M01 à EX-M12 sont traçables vers modules code et captures d'écran de démo (à insérer avant impression PDF).

### 5.3 Non-régression

Script d'initialisation BDD reproductible ; README testé sur Windows 11.

---

## 6. Résultats et limites

### 6.1 Résultats

- Application fonctionnelle locale.
- Documentation séparée en trois volets + annexes.
- Alignement cahier ENSP et consignes supplémentaires.

### 6.2 Limites

- Tarif nuit : règle horaire avancée non automatisée en v1 (application manuelle du code `nuit`).
- Concurrence multi-caissiers : SQLite suffisant pour démo, PostgreSQL en évolution.
- Mode client : simulation locale (un numéro de poste par fenêtre), pas encore d'agent installé sur chaque PC.

---

## 7. Conclusion et perspectives

Le projet démontre la maîtrise du cycle de développement, de l'analyse à la livraison. La méthodologie itérative a permis de stabiliser l'API avant l'intégration Electron.

**Perspectives :** export PDF ticket, agent client par poste, pause exclue de la facturation, synchronisation multi-postes, intégration Mobile Money (hors Won't have v1).

**Alignement SND30 :** voir Annexe F — contribution à la transformation digitale des TPE/PME locales.

---

## 8. Bibliographie

1. Cahier des projets ENSP 2025/2026.  
2. Sommerville I., *Software Engineering*, 10th ed.  
3. FastAPI Documentation, 2024.  
4. Electron Security Guidelines.  
5. Stratégie Nationale de Développement 2030, Cameroun.

---

## 9. Journal des modifications (incrément — juin 2026)

Cette section documente chaque correction apportée suite aux retours utilisateur (onglets, POS, client, rôles).

### 9.1 Problèmes signalés

| # | Symptôme | Cause identifiée |
|---|----------|------------------|
| 1 | Onglets Codes temps, Comptes, Rapports, Admin sans effet | Boutons `data-panel` sans écouteurs JS ni panneaux HTML |
| 2 | Ventes POS impossibles | `AuthRepository` non importé dans `routes.py` → erreur serveur à chaque `POST /pos/vente` |
| 3 | Mode client vide / inutilisable | Pas d'API publique ; `state.postes` vide sans connexion staff |
| 4 | Tous les rôles voient la même interface | Permissions en base mais non appliquées (UI + API) |

### 9.2 Correctifs backend (`backend/app/`)

| Fichier | Modification détaillée |
|---------|------------------------|
| `api/routes.py` | Import `AuthRepository` ; dépendance `require_permission()` sur les routes sensibles ; endpoints `POST /vouchers`, `POST /postes/verrouiller-libres`, `GET /admin/employes`, `GET /admin/roles` ; API kiosk `GET/POST /client/poste/{numero}/*` (statut, commande snack, demande fin) |
| `api/deps.py` | Factory `require_permission(perm)` pour contrôle d'accès par route |
| `repositories/voucher_repository.py` | `list_all()`, `create()` pour gestion des codes temps |
| `services/session_service.py` | Facturation sur **prix du tarif** choisi (plus le groupe PC) ; validation compte client au démarrage ; débit `solde_xaf` à l'arrêt si mode `compte` |
| `database/seed.sql` | Permissions employé : `clients` pour compte en caisse ; manager : `chat` ; admin : liste explicite incluant `admin` |
| `database/migrate_permissions.sql` | Script SQL pour mettre à jour une base déjà créée |

**Matrice des permissions API (après correctif)**

| Permission | Routes protégées | Admin | Manager | Employé (caisse) |
|------------|------------------|:-----:|:-------:|:----------------:|
| `sessions` | start/stop/pause/… | ✓ | ✓ | ✓ |
| `pos` | produits, vente, alertes stock | ✓ | ✓ | ✓ |
| `chat` | messages | ✓ | ✓ | ✓ |
| `clients` | liste clients | ✓ | ✓ | ✓ |
| `vouchers` | liste / création codes | ✓ | ✓ | — |
| `reports` | stats, journal audit | ✓ | ✓ | — |
| `remote` | WOL, verrouiller libres | ✓ | ✓ | — |
| `admin` | employés, rôles | ✓ | — | — |

### 9.3 Correctifs frontend (`frontend/renderer/`)

| Fichier | Modification détaillée |
|---------|------------------------|
| `index.html` | Panneaux `#panel-main`, `#panel-timecodes`, `#panel-accounts`, `#panel-reports`, `#panel-admin` ; sélecteur compte client ; saisie n° poste (login client) ; `data-perm` sur la barre rapide |
| `js/app.js` | Navigation `showPanel()` ; `can()` / `applyRoleUi()` ; chargement onglets (vouchers, clients, rapports, admin) ; POS avec contrôle session + permission ; mode client via `/client/poste/{n}/status` ; commande snack et fin de session ; verrouillage postes libres |
| `css/admin.css` | Styles panneaux, tableaux, cartes rapports |
| `css/client.css`, `css/login.css` | Messages client, champ numéro poste |

**Interface par rôle (résumé)**

- **Employé (caisse)** : Bureau, POS, Chat, compte client en session — pas Rapports, Codes temps, Admin, WOL.
- **Manager** : + Codes temps, Comptes, Rapports, infrastructure (WOL / verrou).
- **Administrateur** : + onglet Admin (employés et rôles).

### 9.4 Procédure de test recommandée

1. Démarrer l'API : `backend/start-api.ps1` (port **8010**).
2. Lancer Electron : `npm start` dans `frontend/`.
3. **POS** : connexion `employe` / `employe` → démarrer session sur un poste → Ventes POS → ajouter un article → vérifier `billPos`.
4. **Rôles** : `employe` ne doit pas voir l'onglet Rapports ; `admin` voit tout.
5. **Client** : sans login, saisir n° poste **1**, Mode client → après session staff, timer et commande snack fonctionnels.

> **Note base existante** : supprimer `data/cybercafe.db` et relancer l'API, ou exécuter `database/migrate_permissions.sql` sur la base SQLite.

### 9.5 Fichiers touchés (liste complète)

`backend/app/api/routes.py`, `backend/app/api/deps.py`, `backend/app/repositories/voucher_repository.py`, `backend/app/services/session_service.py`, `database/seed.sql`, `database/migrate_permissions.sql`, `frontend/renderer/index.html`, `frontend/renderer/js/app.js`, `frontend/renderer/css/admin.css`, `frontend/renderer/css/client.css`, `frontend/renderer/css/login.css`, `docs/rapport_technique/Rapport_technique.md`.

---

## Annexes du rapport

- Annexe A : MoSCoW  
- Annexe B : UML  
- Annexe C : Gantt  
- Annexe D : Risques  
- Annexe E : Collecte besoins  
- Annexe F : SND30  

*Documents sources dans `docs/annexes/`.*

---

*Fin du rapport technique — 15 à 25 pages une fois exporté en PDF avec captures d'écran et page de garde institutionnelle.*
