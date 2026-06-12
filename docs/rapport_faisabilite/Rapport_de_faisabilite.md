# RAPPORT DE FAISABILITÉ

## CyberCafé Manager

---

| | |
|---|---|
| **Version** | 1.0 |
| **Date** | Juin 2026 |
| **Auteur** | Équipe projet Génie Logiciel N3 |

---

## 1. Introduction

Ce rapport évalue la faisabilité globale du projet CyberCafé Manager avant et après réalisation : dimension économique, technique, organisationnelle et bénéfices attendus.

---

## 2. Faisabilité économique

### 2.1 Coûts de développement (estimation)

| Poste | Coût |
|-------|------|
| Licences logicielles | 0 FCFA (stack open source) |
| Matériel (PC existant) | 0 FCFA marginal |
| Temps étudiant (174 h) | Coût d'opportunité académique |
| Déploiement | 0 FCFA (installation locale) |

**Total monétaire direct :** négligeable pour un prototype académique.

### 2.2 Coûts d'exploitation

- Maintenance : sauvegarde BDD, mises à jour Python/Node occasionnelles.
- Électricité : impact marginal vs consommation des postes clients.

### 2.3 Retour sur investissement (cybercafé type 8 postes)

| Indicateur | Sans logiciel | Avec logiciel |
|------------|---------------|---------------|
| Erreurs de caisse estimées | 5–10 % recettes | < 2 % |
| Temps de clôture session | 2–3 min | < 30 s |
| Traçabilité | Faible | Complète |

**Hypothèse :** recette journalière 25 000 XAF, perte évitée 5 % → **1 250 XAF/jour**, soit ~37 500 XAF/mois. Le seuil de rentabilité est atteint dès la première semaine d'utilisation si le temps de développement est acquis (projet étudiant).

### 2.4 Conclusion économique

**Faisable et rentable** pour un établissement même modeste, sous réserve d'adoption par le gérant.

---

## 3. Faisabilité technique

### 3.1 Disponibilité des compétences

| Compétence | Niveau requis | Disponibilité |
|------------|---------------|---------------|
| Python | Intermédiaire | Oui (formation ENSP) |
| Web / JS | Intermédiaire | Oui |
| SQL | Base | Oui |
| Electron | Initiation | Documentation abondante |

### 3.2 Risques techniques

| Risque | Faisabilité mitigation |
|--------|------------------------|
| Stack hybride Electron+Python | Oui — API REST simple |
| SQLite corruption | Oui — sauvegardes |
| Calcul tarifaire incorrect | Oui — tests unitaires domaine |

### 3.3 Infrastructure

- Pas de serveur distant requis.
- Compatible Windows 10+, 4 Go RAM minimum recommandés.

### 3.4 Conclusion technique

**Faisable** dans le délai de 4 semaines avec méthodologie itérative.

---

## 4. Faisabilité organisationnelle

### 4.1 Acteurs impliqués

- Étudiant développeur.
- Encadreur pour validation jalons.
- Gérant pilote (idéal : cybercafé de quartier).

### 4.2 Changement organisationnel

- Formation gérant : **1 à 2 heures** (démarrer/arrêter session, lire ticket).
- Résistance au changement : faible si démo montre gain de temps.

### 4.3 Planning

174 heures sur 4 semaines — charge élevée mais réaliste en période dédiée projet de fin d'année.

### 4.4 Conclusion organisationnelle

**Faisable** avec un utilisateur pilote et suivi hebdomadaire.

---

## 5. Bénéfices attendus

| Bénéfice | Type | Horizon |
|----------|------|---------|
| Réduction pertes de recettes | Financier | Court terme |
| Transparence client (ticket) | Social | Court terme |
| Données pour décision (stats) | Stratégique | Moyen terme |
| Compétences développeur | Académique | Immédiat |
| Digitalisation TPE locale | National (SND30) | Moyen terme |

---

## 6. Synthèse décisionnelle

| Dimension | Verdict |
|-----------|---------|
| Économique | **Favorable** |
| Technique | **Favorable** |
| Organisationnelle | **Favorable** avec formation |
| Global | **Projet viable — poursuite recommandée** |

---

## 7. Recommandations

1. Déployer en pilote sur un cybercafé réel pendant 1 semaine.
2. Sauvegarder `data/cybercafe.db` quotidiennement.
3. Planifier v2 pour authentification et export comptable.

---

*Fin du rapport de faisabilité.*
