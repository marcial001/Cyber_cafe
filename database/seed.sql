INSERT OR IGNORE INTO roles (code, libelle, permissions) VALUES
('admin', 'Administrateur', '["*","admin","sessions","pos","reports","clients","vouchers","remote","chat"]'),
('manager', 'Manager', '["sessions","pos","reports","clients","vouchers","remote","chat"]'),
('employe', 'Employé (caisse)', '["sessions","pos","chat","clients"]');

INSERT OR IGNORE INTO employes (login, mot_de_passe, nom, role_id) VALUES
('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'Administrateur', 1),
('manager', '6ee4a469cd4e91053847f5d3fcb61dbcc91e8f0ef10be7748da4c4a1ba382d17', 'Manager Café', 2),
('employe', '11c27ae42d9214f220eb0918855cbfcde8767d43d0db9efcfc21f018770d2fd6', 'Caissier', 3);

INSERT OR IGNORE INTO groupes_pc (code, libelle, prix_par_heure) VALUES
('standard', 'PC Standard Internet', 200),
('gaming', 'PC Gaming Esport', 400);

INSERT OR IGNORE INTO tarifs (code, libelle, prix_par_heure, heure_debut_nuit, heure_fin_nuit, periode_grace_sec, deduction_min_sec) VALUES
('etudiant', 'Tarif Étudiant', 150, NULL, NULL, 60, 300),
('normal', 'Tarif Normal', 250, NULL, NULL, 60, 300),
('nuit', 'Tarif Nuit', 300, 22, 6, 0, 300);

INSERT OR IGNORE INTO grille_horaire (libelle, jour_semaine, heure_debut, heure_fin, multiplicateur, groupe_id) VALUES
('Happy Hour Lun-Ven', NULL, 14, 17, 0.8, 1),
('Week-end Premium', 6, 0, 23, 1.2, 2);

INSERT OR IGNORE INTO taxes (code, libelle, taux) VALUES
('tva', 'TVA 19.25%', 0.1925);

INSERT OR IGNORE INTO config_systeme (cle, valeur) VALUES
('devise', 'XAF'),
('nom_etablissement', 'CyberCafé Manager Pro'),
('deduction_min_defaut_sec', '300');

INSERT OR IGNORE INTO postes (numero, libelle, groupe_id, pos_x, pos_y, ip_address) VALUES
(1, 'PC-01', 1, 0, 0, '192.168.1.101'),
(2, 'PC-02', 1, 1, 0, '192.168.1.102'),
(3, 'PC-03', 1, 2, 0, '192.168.1.103'),
(4, 'PC-04', 2, 0, 1, '192.168.1.104'),
(5, 'PC-05', 2, 1, 1, '192.168.1.105'),
(6, 'PC-06', 2, 2, 1, '192.168.1.106'),
(7, 'PC-07', 1, 0, 2, '192.168.1.107'),
(8, 'PC-08', 2, 1, 2, '192.168.1.108');

INSERT OR IGNORE INTO clients (code, nom, solde_xaf, points_fidelite) VALUES
('CLI001', 'Jean Dupont', 5000, 120),
('CLI002', 'Marie Nguema', 2500, 45);

INSERT OR IGNORE INTO vouchers (code, duree_secondes, expire_heures, cumul_autorise) VALUES
('VC-30MIN-001', 1800, 24, 0),
('VC-1H-002', 3600, 48, 1),
('VC-2H-003', 7200, 72, 0);

INSERT OR IGNORE INTO types_service_manuel (code, libelle, prix_par_heure) VALUES
('ps5', 'PlayStation 5', 1500),
('billard', 'Table Billard', 2000),
('laptop', 'Location Laptop', 1000);

INSERT OR IGNORE INTO produits (code, libelle, prix, stock, seuil_alerte, cout_unitaire, categorie) VALUES
('EAU', 'Eau 50cl', 200, 50, 10, 100, 'boisson'),
('COCA', 'Coca-Cola', 350, 40, 10, 200, 'boisson'),
('CHIPS', 'Chips', 300, 30, 5, 150, 'snack'),
('CAFE', 'Café', 250, 100, 20, 80, 'boisson'),
('USB', 'Clé USB 8Go', 2500, 15, 3, 1500, 'accessoire');
