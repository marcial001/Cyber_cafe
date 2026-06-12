-- CyberCafé Manager Pro - Schéma relationnel (3NF)
PRAGMA foreign_keys = ON;

-- === Organisation ===
CREATE TABLE IF NOT EXISTS roles (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT NOT NULL UNIQUE,
    libelle     TEXT NOT NULL,
    permissions TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS employes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    login         TEXT NOT NULL UNIQUE,
    mot_de_passe  TEXT NOT NULL,
    nom           TEXT NOT NULL,
    role_id       INTEGER NOT NULL REFERENCES roles(id),
    actif         INTEGER NOT NULL DEFAULT 1 CHECK (actif IN (0, 1)),
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tokens_auth (
    token       TEXT PRIMARY KEY,
    employe_id  INTEGER NOT NULL REFERENCES employes(id),
    expire_at   TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- === Infrastructure PC ===
CREATE TABLE IF NOT EXISTS groupes_pc (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    code            TEXT NOT NULL UNIQUE,
    libelle         TEXT NOT NULL,
    prix_par_heure  REAL NOT NULL CHECK (prix_par_heure >= 0)
);

CREATE TABLE IF NOT EXISTS postes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    numero          INTEGER NOT NULL UNIQUE CHECK (numero > 0),
    libelle         TEXT NOT NULL,
    groupe_id       INTEGER NOT NULL REFERENCES groupes_pc(id),
    pos_x           INTEGER NOT NULL DEFAULT 0,
    pos_y           INTEGER NOT NULL DEFAULT 0,
    etat_materiel   TEXT NOT NULL DEFAULT 'ok'
                    CHECK (etat_materiel IN ('ok', 'panne', 'eteint', 'maintenance')),
    ip_address      TEXT,
    actif           INTEGER NOT NULL DEFAULT 1 CHECK (actif IN (0, 1)),
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- === Tarification ===
CREATE TABLE IF NOT EXISTS tarifs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    code            TEXT NOT NULL UNIQUE,
    libelle         TEXT NOT NULL,
    prix_par_heure  REAL NOT NULL CHECK (prix_par_heure >= 0),
    heure_debut_nuit INTEGER,
    heure_fin_nuit   INTEGER,
    periode_grace_sec INTEGER NOT NULL DEFAULT 0,
    deduction_min_sec INTEGER NOT NULL DEFAULT 0,
    actif           INTEGER NOT NULL DEFAULT 1 CHECK (actif IN (0, 1))
);

CREATE TABLE IF NOT EXISTS grille_horaire (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    libelle         TEXT NOT NULL,
    jour_semaine    INTEGER CHECK (jour_semaine BETWEEN 0 AND 6),
    heure_debut     INTEGER NOT NULL CHECK (heure_debut BETWEEN 0 AND 23),
    heure_fin       INTEGER NOT NULL CHECK (heure_fin BETWEEN 0 AND 23),
    multiplicateur  REAL NOT NULL DEFAULT 1.0 CHECK (multiplicateur > 0),
    groupe_id       INTEGER REFERENCES groupes_pc(id),
    actif           INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS taxes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT NOT NULL UNIQUE,
    libelle     TEXT NOT NULL,
    taux        REAL NOT NULL CHECK (taux >= 0 AND taux <= 1),
    actif       INTEGER NOT NULL DEFAULT 1
);

-- === Clients & prépayé ===
CREATE TABLE IF NOT EXISTS clients (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    code            TEXT NOT NULL UNIQUE,
    nom             TEXT NOT NULL,
    solde_xaf       REAL NOT NULL DEFAULT 0,
    points_fidelite INTEGER NOT NULL DEFAULT 0,
    actif           INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS vouchers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    code            TEXT NOT NULL UNIQUE,
    duree_secondes  INTEGER NOT NULL CHECK (duree_secondes > 0),
    expire_heures   INTEGER,
    cumul_autorise  INTEGER NOT NULL DEFAULT 0,
    utilise         INTEGER NOT NULL DEFAULT 0,
    client_id       INTEGER REFERENCES clients(id),
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    utilise_at      TEXT
);

-- === Sessions PC ===
CREATE TABLE IF NOT EXISTS sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    poste_id        INTEGER NOT NULL REFERENCES postes(id),
    tarif_id        INTEGER NOT NULL REFERENCES tarifs(id),
    client_id       INTEGER REFERENCES clients(id),
    voucher_id      INTEGER REFERENCES vouchers(id),
    employe_id      INTEGER REFERENCES employes(id),
    mode_facturation TEXT NOT NULL DEFAULT 'postpay'
                     CHECK (mode_facturation IN ('postpay', 'prepay', 'voucher', 'compte')),
    debut           TEXT NOT NULL,
    fin             TEXT,
    duree_secondes  INTEGER,
    montant_pc      REAL DEFAULT 0,
    montant_pos     REAL DEFAULT 0,
    montant_taxes   REAL DEFAULT 0,
    montant         REAL,
    statut          TEXT NOT NULL DEFAULT 'en_cours'
                    CHECK (statut IN ('en_cours', 'pause', 'terminee', 'annulee')),
    extra_secondes  INTEGER NOT NULL DEFAULT 0,
    numero_ticket   TEXT UNIQUE,
    notes           TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- === Services manuels (billard, console…) ===
CREATE TABLE IF NOT EXISTS types_service_manuel (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    code            TEXT NOT NULL UNIQUE,
    libelle         TEXT NOT NULL,
    prix_par_heure  REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions_manuelles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    type_id         INTEGER NOT NULL REFERENCES types_service_manuel(id),
    libelle         TEXT NOT NULL,
    debut           TEXT NOT NULL,
    fin             TEXT,
    duree_secondes  INTEGER,
    montant         REAL,
    statut          TEXT NOT NULL DEFAULT 'en_cours',
    employe_id      INTEGER REFERENCES employes(id)
);

-- === POS & stocks ===
CREATE TABLE IF NOT EXISTS produits (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT NOT NULL UNIQUE,
    libelle     TEXT NOT NULL,
    prix        REAL NOT NULL CHECK (prix >= 0),
    stock       INTEGER NOT NULL DEFAULT 0,
    seuil_alerte INTEGER NOT NULL DEFAULT 5,
    cout_unitaire REAL NOT NULL DEFAULT 0,
    categorie   TEXT NOT NULL DEFAULT 'snack',
    actif       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS ventes_pos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  INTEGER REFERENCES sessions(id),
    poste_id    INTEGER REFERENCES postes(id),
    employe_id  INTEGER REFERENCES employes(id),
    total       REAL NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS lignes_vente (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    vente_id    INTEGER NOT NULL REFERENCES ventes_pos(id),
    produit_id  INTEGER NOT NULL REFERENCES produits(id),
    quantite    INTEGER NOT NULL CHECK (quantite > 0),
    prix_unitaire REAL NOT NULL,
    sous_total  REAL NOT NULL
);

-- === Communication & audit ===
CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    poste_id    INTEGER REFERENCES postes(id),
    expediteur  TEXT NOT NULL,
    contenu     TEXT NOT NULL,
    lu          INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS journaux (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    employe_id  INTEGER REFERENCES employes(id),
    action      TEXT NOT NULL,
    details     TEXT,
    poste_id    INTEGER REFERENCES postes(id),
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS config_systeme (
    cle     TEXT PRIMARY KEY,
    valeur  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sessions_poste ON sessions(poste_id);
CREATE INDEX IF NOT EXISTS idx_sessions_statut ON sessions(statut);
CREATE INDEX IF NOT EXISTS idx_journaux_date ON journaux(created_at);
CREATE INDEX IF NOT EXISTS idx_vouchers_code ON vouchers(code);

DROP VIEW IF EXISTS v_postes_etat;
CREATE VIEW v_postes_etat AS
SELECT
    p.id, p.numero, p.libelle, p.groupe_id, g.code AS groupe_code, g.libelle AS groupe_libelle,
    g.prix_par_heure AS groupe_prix_heure, p.pos_x, p.pos_y, p.etat_materiel, p.ip_address, p.actif,
    CASE
        WHEN p.etat_materiel IN ('panne', 'eteint', 'maintenance') THEN p.etat_materiel
        WHEN s.statut = 'pause' THEN 'pause'
        WHEN s.id IS NOT NULL THEN 'occupe'
        ELSE 'libre'
    END AS etat,
    s.id AS session_id, s.debut AS session_debut, s.statut AS session_statut,
    s.mode_facturation, s.montant_pos, s.extra_secondes,
    t.code AS tarif_code, t.libelle AS tarif_libelle,
    c.nom AS client_nom, s.notes
FROM postes p
JOIN groupes_pc g ON g.id = p.groupe_id
LEFT JOIN sessions s ON s.poste_id = p.id AND s.statut IN ('en_cours', 'pause')
LEFT JOIN tarifs t ON t.id = s.tarif_id
LEFT JOIN clients c ON c.id = s.client_id
WHERE p.actif = 1;
