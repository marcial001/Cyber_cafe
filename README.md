# CyberCafé Manager

Application de gestion de cybercafé — Projet Génie Logiciel N3, ENSP Douala (Services Numériques n°03).

**Stack :** Electron (poste de contrôle) + Python FastAPI (serveur) + SQLite.

**Suite type CyberCafePro** : authentification, plan de salle, sessions (pause/transfert/prolongation), vouchers, POS, stocks, journal d'audit, messagerie, tarification dynamique, vue client simulée.

## Prérequis

- Python 3.10+
- Node.js 18+ et npm
- Windows / Linux / macOS

## Installation

### 1. Backend Python

**Option A — Environnement virtuel `.venv` (sans activer le script PowerShell)**

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Option B — Conda (Anaconda / Miniconda), si vous l'utilisez d'habitude**

```powershell
cd backend
conda create -n cybercafe python=3.11 -y
conda activate cybercafe
pip install -r requirements.txt
```

### 2. Frontend Electron

```powershell
cd frontend
npm install
```

## Lancement

**Terminal 1 — API**

Avec `.venv` (recommandé si `Activate.ps1` est bloqué) :

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Avec Conda :

```powershell
cd backend
conda activate cybercafe
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

> **PowerShell :** si `Activate.ps1` affiche *running scripts is disabled*, utilisez les commandes ci-dessus **sans** activer le venv, ou exécutez une fois :  
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Terminal 2 — Interface :**

```powershell
cd frontend
npm start
```

L'API est disponible sur `http://127.0.0.1:8010/docs` (Swagger) si vous utilisez le port par défaut du script ci-dessous.

### Dépannage Windows — port 8000

Si vous voyez `WinError 10013` ou `10048` sur le port 8000 :

1. **Voir qui utilise le port :**
   ```powershell
   netstat -ano | findstr ":8000"
   ```
2. **Arrêter l'ancien processus** (remplacez `9824` par le PID affiché) :
   ```powershell
   taskkill /PID 9824 /F
   ```
3. **Ou utiliser le port 8010** (recommandé) :
   ```powershell
   cd backend
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload
   ```
   Puis pour Electron :
   ```powershell
   $env:CYBERCAFE_API = "http://127.0.0.1:8010/api/v1"
   cd ..\frontend
   npm start
   ```

**Script rapide :** `backend\start-api.ps1` (port 8010 par défaut).

## Configuration des tarifs

Fichier : `config/tarifs.json` (synchronisé avec la table `tarifs` via `database/seed.sql`).

## Base de données

- Schéma : `database/schema.sql`
- Données initiales : `database/seed.sql`
- Fichier SQLite généré : `data/cybercafe.db` (créé au premier démarrage)

## Documentation

| Document | Emplacement |
|----------|-------------|
| Cahier des charges | `docs/cahier_des_charges/` |
| Documentation technique | `docs/documentation_technique/` |
| Rapport technique | `docs/rapport_technique/` |
| Rapport de faisabilité | `docs/rapport_faisabilite/` |
| Annexes (UML, Gantt, MoSCoW) | `docs/annexes/` |

## Principes appliqués

- POO (services, repositories, domain)
- POO, DRY, SOLID (couches), validation stricte des entrées
- Validation stricte des entrées (Pydantic + contrôles frontend)
- Architecture multicouche client/serveur

## Auteur

Projet de fin d'année — Génie Logiciel N3.
