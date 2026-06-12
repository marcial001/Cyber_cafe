# Annexe G — MCD et MLD

## MCD (représentation textuelle)

```
POSTE (id, numero, libelle, actif)
TARIF (id, code, libelle, prix_par_heure, heure_debut_nuit, heure_fin_nuit, actif)
SESSION (id, debut, fin, duree_secondes, montant, statut, numero_ticket)

POSTE 1———N SESSION
TARIF 1———N SESSION
```

## MLD

| Table | Clé primaire | Clé étrangère | Contraintes |
|-------|-------------|--------------|-------------|
| postes | id | — | numero UNIQUE |
| tarifs | id | — | code UNIQUE |
| sessions | id | poste_id → postes.id, tarif_id → tarifs.id | statut ∈ {en_cours, terminee, annulee} |

## Dépendances fonctionnelles (3NF)

- `postes` : id → numero, libelle, actif
- `tarifs` : id → code, libelle, prix_par_heure, ...
- `sessions` : id → poste_id, tarif_id, debut, fin, ...

Aucun attribut non-clé ne dépend d'une autre clé candidate.
