"""Moteur tarifaire dynamique — grilles horaires, groupes PC, taxes."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TarifContext:
    prix_base_heure: float
    multiplicateur_grille: float = 1.0
    periode_grace_sec: int = 0
    deduction_min_sec: int = 0


def calculer_montant(
    duree_secondes: int,
    prix_par_heure: float,
    multiplicateur: float = 1.0,
    deduction_min_sec: int = 0,
    periode_grace_sec: int = 0,
) -> float:
    if duree_secondes < 0:
        raise ValueError("Durée négative interdite")
    if prix_par_heure < 0:
        raise ValueError("Prix négatif interdit")
    facturable = max(0, duree_secondes - periode_grace_sec)
    if deduction_min_sec > 0 and facturable > 0:
        facturable = max(facturable, deduction_min_sec)
    heures = (facturable / 3600.0) * multiplicateur
    return round(heures * prix_par_heure, 0)


def multiplicateur_grille(grilles: list[dict], now: datetime | None = None, groupe_id: int | None = None) -> float:
    now = now or datetime.now()
    mult = 1.0
    for g in grilles:
        if not g.get("actif", 1):
            continue
        if g.get("groupe_id") and groupe_id and g["groupe_id"] != groupe_id:
            continue
        js = g.get("jour_semaine")
        if js is not None and js != now.weekday():
            continue
        h = now.hour
        if g["heure_debut"] <= g["heure_fin"]:
            in_range = g["heure_debut"] <= h < g["heure_fin"]
        else:
            in_range = h >= g["heure_debut"] or h < g["heure_fin"]
        if in_range:
            mult *= float(g["multiplicateur"])
    return mult


def appliquer_taxes(montant_ht: float, taxes: list[dict]) -> tuple[float, float]:
    total_tax = 0.0
    for t in taxes:
        if t.get("actif", 1):
            total_tax += montant_ht * float(t["taux"])
    return round(montant_ht + total_tax, 0), round(total_tax, 0)


def generer_numero_ticket(session_id: int, prefix: str = "TK") -> str:
    if session_id <= 0:
        raise ValueError("Identifiant session invalide")
    return f"{prefix}-{session_id:06d}"
