-- Mise à jour des permissions rôles (juin 2026)
-- Exécuter si la base existait avant le correctif RBAC :
-- sqlite3 data/cybercafe.db < database/migrate_permissions.sql

UPDATE roles SET permissions = '["*","admin","sessions","pos","reports","clients","vouchers","remote","chat"]'
WHERE code = 'admin';

UPDATE roles SET permissions = '["sessions","pos","reports","clients","vouchers","remote","chat"]'
WHERE code = 'manager';

UPDATE roles SET permissions = '["sessions","pos","chat","clients"]'
WHERE code = 'employe';
