from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class LoginIn(BaseModel):
    login: str = Field(..., min_length=2, max_length=32)
    password: str = Field(..., min_length=3, max_length=128)

    @field_validator("login")
    @classmethod
    def norm_login(cls, v: str) -> str:
        return v.strip().lower()


class EmployeOut(BaseModel):
    id: int
    login: str
    nom: str
    role: str
    permissions: list[str]


class LoginOut(BaseModel):
    token: str
    employe: EmployeOut


class TarifOut(BaseModel):
    id: int
    code: str
    libelle: str
    prix_par_heure: float


class PosteEtatOut(BaseModel):
    id: int
    numero: int
    libelle: str
    groupe_code: str
    groupe_libelle: str
    groupe_prix_heure: float
    pos_x: int
    pos_y: int
    etat_materiel: str
    etat: str
    session_id: int | None = None
    session_debut: str | None = None
    session_statut: str | None = None
    mode_facturation: str | None = None
    montant_pos: float | None = None
    tarif_code: str | None = None
    tarif_libelle: str | None = None
    client_nom: str | None = None
    notes: str | None = None


class SessionStartIn(BaseModel):
    poste_id: int = Field(..., gt=0)
    tarif_code: str = Field(..., min_length=2, max_length=32)
    mode_facturation: Literal["postpay", "prepay", "voucher", "compte"] = "postpay"
    voucher_code: str | None = None
    client_id: int | None = Field(None, gt=0)
    notes: str | None = Field(None, max_length=500)

    @field_validator("tarif_code")
    @classmethod
    def normalize_tarif(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if not cleaned.replace("_", "").isalnum():
            raise ValueError("Code tarif invalide")
        return cleaned

    @field_validator("voucher_code")
    @classmethod
    def normalize_voucher(cls, v: str | None) -> str | None:
        return v.strip().upper() if v else None


class SessionStopIn(BaseModel):
    session_id: int = Field(..., gt=0)


class SessionActionIn(BaseModel):
    session_id: int = Field(..., gt=0)


class SessionExtendIn(BaseModel):
    session_id: int = Field(..., gt=0)
    minutes: int = Field(..., gt=0, le=480)


class SessionTransferIn(BaseModel):
    session_id: int = Field(..., gt=0)
    new_poste_id: int = Field(..., gt=0)


class PosLineIn(BaseModel):
    produit_id: int = Field(..., gt=0)
    quantite: int = Field(..., gt=0, le=99)


class PosVenteIn(BaseModel):
    items: list[PosLineIn] = Field(..., min_length=1)
    session_id: int | None = Field(None, gt=0)
    poste_id: int | None = Field(None, gt=0)


class MessageIn(BaseModel):
    poste_id: int | None = None
    contenu: str = Field(..., min_length=1, max_length=500)


class PosteEtatMaterielIn(BaseModel):
    etat_materiel: Literal["ok", "panne", "eteint", "maintenance"]


class SessionOut(BaseModel):
    id: int
    poste_id: int
    poste_numero: int
    tarif_code: str
    tarif_libelle: str
    debut: str
    fin: str | None = None
    duree_secondes: int | None = None
    montant_pc: float | None = None
    montant_pos: float | None = None
    montant_taxes: float | None = None
    montant: float | None = None
    statut: str
    mode_facturation: str | None = None
    numero_ticket: str | None = None


class TicketOut(BaseModel):
    numero_ticket: str
    poste_numero: int
    tarif_libelle: str
    debut: str
    fin: str
    duree_minutes: int
    montant_pc: float | None = None
    montant_pos: float | None = None
    montant_taxes: float | None = None
    montant: float
    devise: str = "XAF"


class StatsJournalieresOut(BaseModel):
    date: str
    recettes_totales: float
    nombre_sessions: int
    postes_plus_utilises: list[dict]


class HealthOut(BaseModel):
    status: str
    timestamp: datetime
