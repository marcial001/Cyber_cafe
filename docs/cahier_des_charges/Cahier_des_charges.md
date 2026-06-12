# CAHIER DES CHARGES

## Application de gestion de cybercafé — CyberCafé Manager

---

| | |
|---|---|
| **Établissement** | École Nationale Supérieure Polytechnique de Douala |
| **Filière** | Génie Logiciel — Niveau 3 |
| **Encadrement** | Dr. MALONG Yannick |
| **Projet** | Services Numériques n°03 — Gestion d'un Cybercafé |
| **Version** | 1.0 |
| **Date** | Juin 2026 |
| **Statut** | Document de référence contractuel interne |

---

## Table des matières

1. [Introduction](#1-introduction)
2. [Étude comparative des méthodologies](#2-étude-comparative-des-méthodologies)
3. [Collecte des besoins](#3-collecte-des-besoins)
4. [Référentiel des exigences MoSCoW](#4-référentiel-des-exigences-moscow)
5. [Description et objectifs du projet](#5-description-et-objectifs-du-projet)
6. [Acteurs cibles](#6-acteurs-cibles)
7. [Périmètre fonctionnel](#7-périmètre-fonctionnel)
8. [Contraintes d'environnement et prérequis](#8-contraintes-denvironnement-et-prérequis)
9. [Analyse comparative des technologies](#9-analyse-comparative-des-technologies)
10. [Architecture retenue et comparatif](#10-architecture-retenue-et-comparatif)
11. [Planning et jalons](#11-planning-et-jalons)
12. [Analyse des risques](#12-analyse-des-risques)
13. [Livrables et critères d'acceptation](#13-livrables-et-critères-dacceptation)
14. [Références](#14-références)

---

## 1. Introduction

### 1.1 Contexte

Les cybercafés constituent un maillon essentiel de l'accès au numérique au Cameroun, notamment pour les étudiants, les demandeurs d'emploi et les micro-entrepreneurs. Dans de nombreux établissements de Douala et d'autres villes, la gestion des postes reste artisanale : feuilles de papier, calcul mental ou tableur non synchronisé. Cette situation engendre des erreurs de facturation, des litiges avec les clients et des pertes de recettes difficilement quantifiables.

Le présent cahier des charges formalise les exigences du système **CyberCafé Manager**, application desktop destinée à automatiser le suivi des sessions, le calcul tarifaire et la production de statistiques journalières.

### 1.2 Objectif du document

Ce document constitue le **contrat fonctionnel et technique** entre les parties prenantes et l'équipe de réalisation. Il est distinct du rapport technique et de la documentation d'exploitation, conformément aux consignes du projet.

### 1.3 Documents associés

| Document | Rôle |
|----------|------|
| Documentation technique | Architecture, UML détaillé, implémentation |
| Rapport technique | Synthèse académique pour soutenance |
| Rapport de faisabilité | Économique, technique, organisationnel |
| Annexes | MoSCoW, UML, Gantt, risques, collecte besoins |

---

## 2. Étude comparative des méthodologies

### 2.1 Méthode en cascade

**Principe :** Enchaînement séquentiel strict — spécifications, conception, développement, tests, déploiement. Chaque phase doit être terminée et validée avant la suivante.

| Critère | Évaluation |
|---------|------------|
| Prévisibilité | Excellente si besoins figés |
| Flexibilité | Faible — retour arrière coûteux |
| Documentation | Abondante, structurée |
| Risque sur besoins évolutifs | Élevé pour un contexte terrain |

### 2.2 Méthode Agile (Scrum)

**Principe :** Développement itératif par sprints de 1 à 4 semaines, livraison incrémentale, rétrospectives, priorisation du backlog.

| Critère | Évaluation |
|---------|------------|
| Adaptation au changement | Excellente |
| Implication utilisateur | Forte (Product Owner, démos) |
| Charge documentaire | Allégée (valorise le logiciel) |
| Risque en contexte solo/étudiant | Cérémonies Scrum lourdes pour un développeur unique |

### 2.3 Méthode itérative (RUP allégé / cycle en V itératif)

**Principe :** Répétition de mini-cycles analyse → conception → construction → test, avec consolidation progressive des livrables documentaires et du code.

| Critère | Évaluation |
|---------|------------|
| Équilibre doc/code | Bon compromis académique |
| Maîtrise des risques techniques | Validation précoce du backend et de la BDD |
| Délai 4 semaines | Compatible avec 4 itérations hebdomadaires |

### 2.4 Grille de sélection et décision

| Critère de sélection | Poids | Cascade | Agile | Itérative | Commentaire |
|---------------------|-------|---------|-------|-----------|-------------|
| Délai fixe 4 semaines | 20% | 3 | 4 | 5 | Itérative cadre bien 4 jalons |
| Exigences documentaires ENSP | 25% | 5 | 2 | 4 | Cascade favorise docs ; itérative les produit par paliers |
| Besoins partiellement connus | 15% | 2 | 5 | 4 | Tarifs et UX affinables en cours |
| Équipe réduite (1-2 dev) | 15% | 4 | 3 | 5 | Itérative sans surcharge Scrum |
| Besoin de MVP démo rapide | 15% | 2 | 5 | 4 | Backend testable dès semaine 2 |
| Qualité / tests par palier | 10% | 3 | 4 | 5 | Tests à chaque itération |

**Scores pondérés (sur 5) :** Cascade ≈ 3,1 | Agile ≈ 3,6 | **Itérative ≈ 4,5**

### 2.5 Justification du choix : méthodologie itérative

La méthodologie **itérative** est retenue car elle :

1. **Respecte le calendrier académique** en alignant chaque semaine sur un jalon (analyse, conception, développement, clôture).
2. **Satisfait les livrables documentaires** sans attendre la fin du projet pour produire UML et rapports.
3. **Réduit le risque technique** en validant tôt l'API Python et le schéma SQLite avant l'intégration Electron.
4. **Reste réaliste** pour une équipe étudiante sans coach Scrum dédié.

Les principes Agile (priorisation MoSCoW, démo fonctionnelle) sont **intégrés** sans appliquer l'intégralité du cadre Scrum.

---

## 3. Collecte des besoins

La collecte détaillée (parties prenantes, attentes, contraintes) est fournie en **Annexe E** (`docs/annexes/collecte_besoins.md`).

**Synthèse :** le besoin central exprimé par le gérant est de **ne plus perdre de revenus** par manque de traçabilité du temps de connexion. Les contraintes locales incluent matériel modeste, aléas électriques et niveau variable de littératie numérique des opérateurs.

---

## 4. Référentiel des exigences MoSCoW

Le référentiel complet avec identifiants, sources et critères de validation figure en **Annexe A** (`docs/annexes/referentiel_exigences_moscow.md`).

**Résumé quantitatif :** 12 Must have, 7 Should have, 5 Could have, 5 Won't have (v1).

---

## 5. Description et objectifs du projet

### 5.1 Description

CyberCafé Manager est une solution **client lourd** composée d'une interface **Electron** et d'une API **Python (FastAPI)** persistée en **SQLite**. Elle permet au gérant de visualiser l'état des postes, d'ouvrir et clôturer des sessions avec chronomètre, d'appliquer des tarifs différenciés et d'obtenir tickets et statistiques.

### 5.2 Objectifs généraux

| Objectif | Indicateur de réussite |
|----------|------------------------|
| OG1 — Fiabiliser la facturation | 100 % des sessions terminées ont un montant et un ticket |
| OG2 — Visibilité temps réel | État des postes mis à jour automatiquement |
| OG3 — Aide à la décision | Statistiques journalières exploitables |
| OG4 — Conformité académique | Tous livrables ENSP + consignes supplémentaires |
| OG5 — Maintenabilité | Architecture multicouche documentée |

### 5.3 Objectifs spécifiques

- Réduire les litiges client liés au temps facturé.
- Paramétrer les tarifs sans recompilation.
- Fournir une base pour extension future (Mobile Money, multi-site).

---

## 6. Acteurs cibles

| Acteur | Description | Interaction système |
|--------|-------------|---------------------|
| **Gérant** | Responsable du cybercafé | Utilisateur principal de l'IHM |
| **Caissier** | Employé en shift | Même IHM, droits identiques en v1 |
| **Client final** | Usager d'un poste | Pas d'accès direct — reçoit le ticket |
| **Administrateur technique** | Développeur / mainteneur | Installation, sauvegarde BDD, config JSON |

---

## 7. Périmètre fonctionnel

### 7.1 Fonctions obligatoires (cahier ENSP)

1. Tableau de bord postes (libre / occupé).
2. Démarrage / arrêt session + chronomètre temps réel.
3. Calcul automatique du prix (tarif/heure configurable).
4. Enregistrement sessions + tickets de caisse.
5. Statistiques journalières (recettes, postes les plus utilisés).
6. Gestion tarifs étudiant, normal, nuit.

### 7.2 Hors périmètre v1

Paiement Mobile Money, application mobile, multi-établissements (cf. Won't have Annexe A).

---

## 8. Contraintes d'environnement et prérequis

### 8.1 Contraintes environnementales

- Déploiement **local** (pas de cloud obligatoire).
- Fonctionnement **hors ligne** après installation.
- Contexte **camerounais** : devise XAF, interface française, tarification adaptée aux réalités locales.

### 8.2 Contraintes techniques

- OS : Windows 10/11 (prioritaire).
- Python 3.10+, Node.js 18+, Electron 33+.
- SQLite 3 embarqué.

### 8.3 Prérequis organisationnels

- Accès à un poste de démonstration pour la soutenance.
- Validation encadreur au jalon conception (MCD/MLD).

### 8.4 Contraintes réglementaires et éthiques

- Respect de la propriété intellectuelle (anti-plagiat ENSP).
- Protection des données limitées (pas de données personnelles sensibles en v1).

---

## 9. Analyse comparative des technologies

### 9.1 Options frontend

| Technologie | Avantages | Contraintes | Coût dev/maintenance | Courbe apprentissage |
|-------------|-----------|-------------|------------------------|----------------------|
| **Electron** (retenu) | UI riche, HTML/CSS, multi-OS | Taille binaire, RAM | Moyen / Moyen | Moyenne si web connu |
| Tkinter | Natif Python, léger | UI limitée, peu moderne | Faible / Faible | Faible |
| JavaFX | Entreprise, typé | Verbeux, packaging lourd | Élevé / Moyen | Élevée |

### 9.2 Options backend

| Technologie | Avantages | Contraintes | Coût | Apprentissage |
|-------------|-----------|-------------|------|---------------|
| **FastAPI** (retenu) | Rapide, typé, Swagger auto | Nécessite serveur local | Faible | Moyenne |
| Flask | Simple, populaire | Moins de validation native | Faible | Faible |
| Django | Complet, ORM | Lourd pour petite API | Moyen | Élevée |

### 9.3 Stockage

| SGBD | Avantages | Contraintes | Retenu |
|------|-----------|-------------|--------|
| **SQLite** | Zéro config, fichier unique | Concurrence écriture limitée | Oui |
| PostgreSQL | Robuste, concurrent | Installation serveur | Non (v1) |
| MySQL | Répandu | Infrastructure | Non (v1) |

### 9.4 Outils retenus

| Outil | Usage |
|-------|-------|
| Python 3.11 + FastAPI + Pydantic | API, validation |
| Uvicorn | Serveur ASGI |
| Electron + IPC preload | IHM desktop sécurisée |
| SQLite + SQL scripts | Persistance |
| Git / GitHub | Versionnement |
| Draw.io / Mermaid | UML et Gantt |
| Pandoc ou Word | Export PDF professionnel |

---

## 10. Architecture retenue et comparatif

### 10.1 Architecture retenue : **Client-Serveur local multicouche (3-tiers allégé)**

```
[Présentation - Electron] --HTTP JSON--> [API - FastAPI] --> [Services] --> [Repositories] --> [SQLite]
```

**Justification :** séparation claire IHM / logique métier ; tests API indépendants ; respect du choix Electron + Python.

### 10.2 Comparatif avec autres styles

| Architecture | Adéquation projet | Raison |
|--------------|-------------------|--------|
| **Monolithique desktop seul (Tkinter tout-en-un)** | Moyenne | Mélange UI et métier, tests difficiles |
| **Microservices** | Faible | Sur-ingénierie pour un cybercafé local |
| **Client-serveur local (retenu)** | **Élevée** | Équilibre POO, testabilité, démo |
| **Serverless cloud** | Faible | Dépendance réseau, coût, hors SND30 local |

### 10.3 Patrons de conception retenus

| Patron | Application |
|--------|-------------|
| **Repository** | Accès SQLite encapsulé |
| **Service Layer** | `SessionService`, `DashboardService` |
| **DTO / Schema** | Pydantic `SessionStartIn`, `SessionOut` |
| **Domain Model** | `Pricing` (calcul pur, sans I/O) |

---

## 11. Planning et jalons

Voir **Annexe C** — planning 4 semaines, 174 heures estimées, chemin critique T01→T05→T08→T09→T11→T13.

---

## 12. Analyse des risques

Voir **Annexe D** — 10 risques identifiés, mitigations associées.

---

## 13. Livrables et critères d'acceptation

| Livrable | Critère d'acceptation |
|----------|----------------------|
| Code source | Compile, démo session complète, GitHub |
| SQL | Exécution sans erreur, 3NF |
| CDC (ce document) | Complet, format professionnel, PDF |
| IHM | 6 fonctionnalités ENSP opérationnelles |
| Config tarifs | Fichier JSON + cohérence BDD |
| README | Installation reproductible |

---

## 14. Références

- Cahier des projets ENSP Douala 2025/2026 — Dr. MALONG Yannick.
- Stratégie Nationale de Développement 2030 (SND30), République du Cameroun.
- Documentation FastAPI : https://fastapi.tiangolo.com/
- Documentation Electron : https://www.electronjs.org/docs

---

*Fin du cahier des charges — Document séparé de la documentation technique et du rapport technique.*
