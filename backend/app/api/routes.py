from datetime import date, datetime

from fastapi import APIRouter, Depends

from app.api.deps import (
    build_auth_service,
    build_dashboard_service,
    build_journal,
    build_pos_service,
    build_session_service,
    get_current_user,
    get_db,
    require_permission,
)
from app.repositories.auth_repository import AuthRepository
from app.exceptions import AppError, ConflictError, NotFoundError, ValidationError
from app.repositories.voucher_repository import VoucherRepository
from app.repositories.base import BaseRepository
from app.schemas import (
    HealthOut,
    LoginIn,
    LoginOut,
    MessageIn,
    PosVenteIn,
    PosteEtatMaterielIn,
    PosteEtatOut,
    SessionActionIn,
    SessionExtendIn,
    SessionOut,
    SessionStartIn,
    SessionStopIn,
    SessionTransferIn,
    StatsJournalieresOut,
    TarifOut,
    TicketOut,
)
router = APIRouter()


def _handle_app_error(exc: AppError):
    from fastapi import HTTPException

    status = 400
    if exc.code == "NOT_FOUND":
        status = 404
    elif exc.code == "CONFLICT":
        status = 409
    raise HTTPException(status_code=status, detail={"code": exc.code, "message": exc.message})


def _map_session(row: dict) -> SessionOut:
    return SessionOut(
        id=row["id"],
        poste_id=row["poste_id"],
        poste_numero=row["poste_numero"],
        tarif_code=row["tarif_code"],
        tarif_libelle=row["tarif_libelle"],
        debut=row["debut"],
        fin=row.get("fin"),
        duree_secondes=row.get("duree_secondes"),
        montant_pc=row.get("montant_pc"),
        montant_pos=row.get("montant_pos"),
        montant_taxes=row.get("montant_taxes"),
        montant=row.get("montant"),
        statut=row["statut"],
        mode_facturation=row.get("mode_facturation"),
        numero_ticket=row.get("numero_ticket"),
    )


@router.get("/health", response_model=HealthOut)
def health():
    return HealthOut(status="ok", timestamp=datetime.utcnow())


@router.post("/auth/login", response_model=LoginOut)
def login(payload: LoginIn, conn=Depends(get_db)):
    svc = build_auth_service(conn)
    try:
        result = svc.login(payload.login, payload.password)
        build_journal(conn).log("LOGIN", result["employe"]["id"], payload.login)
        conn.commit()
        return LoginOut(token=result["token"], employe=result["employe"])
    except AppError as exc:
        conn.rollback()
        _handle_app_error(exc)


@router.get("/postes", response_model=list[PosteEtatOut])
def list_postes(_=Depends(get_current_user), conn=Depends(get_db)):
    return build_dashboard_service(conn).postes()


@router.get("/tarifs", response_model=list[TarifOut])
def list_tarifs(_=Depends(get_current_user), conn=Depends(get_db)):
    return build_dashboard_service(conn).tarifs()


@router.get("/stats/journalieres", response_model=StatsJournalieresOut)
def stats_journalieres(_=Depends(require_permission("reports")), conn=Depends(get_db)):
    return build_dashboard_service(conn).stats_aujourd_hui()


@router.get("/dashboard")
def dashboard(user=Depends(get_current_user), conn=Depends(get_db)):
    dash = build_dashboard_service(conn)
    postes = dash.postes()
    return {
        "date": date.today().isoformat(),
        "stats": dash.stats_aujourd_hui(),
        "postes": postes,
        "occupes": sum(1 for p in postes if p["etat"] in ("occupe", "pause")),
        "libres": sum(1 for p in postes if p["etat"] == "libre"),
        "utilisateur": user,
    }


@router.get("/vouchers")
def list_vouchers(_=Depends(require_permission("vouchers")), conn=Depends(get_db)):
    return VoucherRepository(conn).list_all()


@router.post("/vouchers")
def create_voucher(
    payload: dict,
    user=Depends(require_permission("vouchers")),
    conn=Depends(get_db),
):
    repo = VoucherRepository(conn)
    try:
        row = repo.create(
            payload.get("code", ""),
            int(payload.get("duree_minutes", 30)),
            int(payload.get("expire_heures", 24)),
        )
        build_journal(conn).log("VOUCHER_CREATE", user["id"], row["code"])
        conn.commit()
        return row
    except AppError as exc:
        conn.rollback()
        _handle_app_error(exc)


@router.get("/clients")
def list_clients(_=Depends(require_permission("clients")), conn=Depends(get_db)):
    return BaseRepository(conn)._all(
        "SELECT id, code, nom, solde_xaf, points_fidelite FROM clients WHERE actif = 1 ORDER BY nom"
    )


@router.get("/produits")
def list_produits(_=Depends(require_permission("pos")), conn=Depends(get_db)):
    return build_pos_service(conn).list_produits()


@router.get("/produits/alertes")
def stock_alertes(_=Depends(require_permission("pos")), conn=Depends(get_db)):
    return build_pos_service(conn).stock_alerts()


@router.post("/pos/vente")
def pos_vente(payload: PosVenteIn, user=Depends(require_permission("pos")), conn=Depends(get_db)):
    svc = build_pos_service(conn)
    try:
        result = svc.vendre(
            [i.model_dump() for i in payload.items],
            payload.session_id,
            payload.poste_id,
            user["id"],
        )
        build_journal(conn).log("POS_VENTE", user["id"], str(result["total"]), payload.poste_id)
        conn.commit()
        return result
    except AppError as exc:
        conn.rollback()
        _handle_app_error(exc)


@router.post("/sessions/start", response_model=SessionOut)
def start_session(payload: SessionStartIn, user=Depends(require_permission("sessions")), conn=Depends(get_db)):
    svc = build_session_service(conn)
    try:
        row = svc.demarrer(payload, user["id"])
        build_journal(conn).log("SESSION_START", user["id"], f"poste={payload.poste_id}", payload.poste_id)
        conn.commit()
        return _map_session(row)
    except AppError as exc:
        conn.rollback()
        _handle_app_error(exc)


@router.post("/sessions/stop", response_model=SessionOut)
def stop_session(payload: SessionStopIn, user=Depends(require_permission("sessions")), conn=Depends(get_db)):
    svc = build_session_service(conn)
    try:
        row = svc.arreter(payload)
        build_journal(conn).log("SESSION_STOP", user["id"], f"session={payload.session_id}")
        conn.commit()
        return _map_session(row)
    except AppError as exc:
        conn.rollback()
        _handle_app_error(exc)


@router.post("/sessions/pause", response_model=SessionOut)
def pause_session(payload: SessionActionIn, user=Depends(require_permission("sessions")), conn=Depends(get_db)):
    svc = build_session_service(conn)
    try:
        row = svc.pause(payload.session_id)
        conn.commit()
        return _map_session(row)
    except AppError as exc:
        conn.rollback()
        _handle_app_error(exc)


@router.post("/sessions/reprendre", response_model=SessionOut)
def resume_session(payload: SessionActionIn, user=Depends(require_permission("sessions")), conn=Depends(get_db)):
    svc = build_session_service(conn)
    try:
        row = svc.reprendre(payload.session_id)
        conn.commit()
        return _map_session(row)
    except AppError as exc:
        conn.rollback()
        _handle_app_error(exc)


@router.post("/sessions/prolonger", response_model=SessionOut)
def extend_session(payload: SessionExtendIn, user=Depends(require_permission("sessions")), conn=Depends(get_db)):
    svc = build_session_service(conn)
    try:
        row = svc.prolonger(payload.session_id, payload.minutes)
        build_journal(conn).log("SESSION_EXTEND", user["id"], f"+{payload.minutes}min")
        conn.commit()
        return _map_session(row)
    except AppError as exc:
        conn.rollback()
        _handle_app_error(exc)


@router.post("/sessions/transferer", response_model=SessionOut)
def transfer_session(payload: SessionTransferIn, user=Depends(require_permission("sessions")), conn=Depends(get_db)):
    svc = build_session_service(conn)
    try:
        row = svc.transferer(payload.session_id, payload.new_poste_id)
        build_journal(conn).log("SESSION_TRANSFER", user["id"], f"->{payload.new_poste_id}")
        conn.commit()
        return _map_session(row)
    except AppError as exc:
        conn.rollback()
        _handle_app_error(exc)


@router.get("/sessions/{session_id}/ticket", response_model=TicketOut)
def get_ticket(session_id: int, _=Depends(get_current_user), conn=Depends(get_db)):
    svc = build_session_service(conn)
    try:
        return svc.ticket(session_id)
    except AppError as exc:
        _handle_app_error(exc)


@router.post("/postes/{poste_id}/etat")
def set_poste_etat(poste_id: int, payload: PosteEtatMaterielIn, user=Depends(get_current_user), conn=Depends(get_db)):
    from app.repositories.poste_repository import PosteRepository

    PosteRepository(conn).set_etat_materiel(poste_id, payload.etat_materiel)
    build_journal(conn).log("POSTE_ETAT", user["id"], payload.etat_materiel, poste_id)
    conn.commit()
    return {"ok": True}


@router.post("/postes/{poste_id}/message")
def send_message(poste_id: int, payload: MessageIn, user=Depends(require_permission("chat")), conn=Depends(get_db)):
    conn.execute(
        "INSERT INTO messages (poste_id, expediteur, contenu) VALUES (?, ?, ?)",
        (poste_id, user["nom"], payload.contenu[:500]),
    )
    conn.commit()
    return {"ok": True}


@router.get("/messages")
def list_messages(_=Depends(require_permission("chat")), conn=Depends(get_db)):
    return BaseRepository(conn)._all(
        "SELECT m.*, p.libelle AS poste_libelle FROM messages m LEFT JOIN postes p ON p.id = m.poste_id ORDER BY m.id DESC LIMIT 30"
    )


@router.get("/journaux")
def list_journaux(_=Depends(require_permission("reports")), conn=Depends(get_db)):
    return build_journal(conn).list_recent()


@router.get("/services-manuels")
def services_manuels(_=Depends(get_current_user), conn=Depends(get_db)):
    return BaseRepository(conn)._all("SELECT * FROM types_service_manuel")


@router.post("/infrastructure/wol")
def wake_on_lan(user=Depends(require_permission("remote")), conn=Depends(get_db)):
    build_journal(conn).log("WOL_SIMULATION", user["id"], "Wake all PCs (simulated)")
    conn.commit()
    return {"message": "Wake-on-LAN simulé — commande enregistrée dans le journal"}


@router.post("/postes/verrouiller-libres")
def verrouiller_libres(user=Depends(require_permission("remote")), conn=Depends(get_db)):
    from app.repositories.poste_repository import PosteRepository

    repo = PosteRepository(conn)
    count = 0
    for p in repo.list_etat():
        if p["etat"] == "libre" and p["etat_materiel"] == "ok":
            repo.set_etat_materiel(p["id"], "maintenance")
            count += 1
    build_journal(conn).log("LOCK_FREE_POSTES", user["id"], f"{count} postes")
    conn.commit()
    return {"verrouilles": count, "message": f"{count} poste(s) libre(s) verrouillé(s)"}


@router.post("/postes/deverrouiller-libres")
def deverrouiller_libres(user=Depends(require_permission("remote")), conn=Depends(get_db)):
    from app.repositories.poste_repository import PosteRepository

    repo = PosteRepository(conn)
    count = 0
    for p in repo.list_etat():
        if p["etat"] == "libre" and p["etat_materiel"] == "maintenance":
            repo.set_etat_materiel(p["id"], "ok")
            count += 1
    build_journal(conn).log("UNLOCK_FREE_POSTES", user["id"], f"{count} postes")
    conn.commit()
    return {"deverrouilles": count}


@router.get("/admin/employes")
def admin_employes(_=Depends(require_permission("admin")), conn=Depends(get_db)):
    return BaseRepository(conn)._all(
        """
        SELECT e.id, e.login, e.nom, r.code AS role, r.libelle AS role_libelle
        FROM employes e JOIN roles r ON r.id = e.role_id
        WHERE e.actif = 1 ORDER BY e.id
        """
    )


@router.get("/admin/roles")
def admin_roles(_=Depends(require_permission("admin")), conn=Depends(get_db)):
    return BaseRepository(conn)._all("SELECT code, libelle, permissions FROM roles ORDER BY id")


@router.get("/client/poste/{numero}/status")
def client_poste_status(numero: int, conn=Depends(get_db)):
    from app.repositories.poste_repository import PosteRepository

    row = PosteRepository(conn)._one(
        "SELECT * FROM v_postes_etat WHERE numero = ? AND actif = 1",
        (numero,),
    )
    if not row:
        _handle_app_error(NotFoundError("Poste introuvable"))
    if row.get("tarif_code"):
        t = BaseRepository(conn)._one(
            "SELECT prix_par_heure FROM tarifs WHERE code = ? AND actif = 1",
            (row["tarif_code"],),
        )
        row["tarif_prix_heure"] = float(t["prix_par_heure"]) if t else row.get("groupe_prix_heure")
    else:
        row["tarif_prix_heure"] = row.get("groupe_prix_heure")
    produits = build_pos_service(conn).list_produits()
    return {"poste": row, "produits": produits}


@router.post("/client/poste/{numero}/commande")
def client_commande(numero: int, payload: dict, conn=Depends(get_db)):
    from app.repositories.poste_repository import PosteRepository

    poste = PosteRepository(conn)._one(
        "SELECT id FROM postes WHERE numero = ? AND actif = 1",
        (numero,),
    )
    if not poste:
        _handle_app_error(NotFoundError("Poste introuvable"))
    produit_id = int(payload.get("produit_id", 0))
    if not produit_id:
        _handle_app_error(ValidationError("produit_id requis"))
    row = PosteRepository(conn)._one(
        """
        SELECT s.id AS session_id FROM sessions s
        WHERE s.poste_id = ? AND s.statut IN ('en_cours', 'pause')
        ORDER BY s.id DESC LIMIT 1
        """,
        (poste["id"],),
    )
    if not row:
        _handle_app_error(ConflictError("Aucune session active sur ce poste"))
    svc = build_pos_service(conn)
    try:
        result = svc.vendre(
            [{"produit_id": produit_id, "quantite": 1}],
            row["session_id"],
            poste["id"],
            None,
        )
        conn.execute(
            "INSERT INTO messages (poste_id, expediteur, contenu) VALUES (?, ?, ?)",
            (poste["id"], "Client", f"Commande snack — {result.get('total', 0)} XAF"),
        )
        conn.commit()
        return result
    except AppError as exc:
        conn.rollback()
        _handle_app_error(exc)


@router.post("/client/poste/{numero}/demande-fin")
def client_demande_fin(numero: int, conn=Depends(get_db)):
    from app.repositories.poste_repository import PosteRepository

    poste = PosteRepository(conn)._one("SELECT id FROM postes WHERE numero = ? AND actif = 1", (numero,))
    if not poste:
        _handle_app_error(NotFoundError("Poste introuvable"))
    conn.execute(
        "INSERT INTO messages (poste_id, expediteur, contenu) VALUES (?, ?, ?)",
        (poste["id"], "Client", "Demande de fin de session — merci de passer à la caisse"),
    )
    conn.commit()
    return {"ok": True, "message": "Demande envoyée au personnel"}


from pydantic import BaseModel

class ClientAuthVoucherIn(BaseModel):
    voucher_code: str
    tarif_code: str

class ClientAuthCompteIn(BaseModel):
    client_code: str


@router.get("/client/poste/{numero}/tarifs", response_model=list[TarifOut])
def client_list_tarifs(numero: int, conn=Depends(get_db)):
    from app.repositories.poste_repository import PosteRepository
    poste = PosteRepository(conn)._one("SELECT id FROM postes WHERE numero = ? AND actif = 1", (numero,))
    if not poste:
        _handle_app_error(NotFoundError("Poste introuvable"))
    return build_dashboard_service(conn).tarifs()


@router.post("/client/poste/{numero}/auth/voucher")
def client_auth_voucher(numero: int, payload: ClientAuthVoucherIn, conn=Depends(get_db)):
    from app.repositories.poste_repository import PosteRepository
    from app.repositories.voucher_repository import VoucherRepository

    # 1. Find the poste by numero (must be actif=1, etat_materiel='ok')
    poste = PosteRepository(conn)._one(
        "SELECT id, etat_materiel FROM postes WHERE numero = ? AND actif = 1",
        (numero,),
    )
    if not poste:
        _handle_app_error(NotFoundError("Poste introuvable"))
    if poste.get("etat_materiel") in ("panne", "eteint", "maintenance"):
        _handle_app_error(ConflictError(f"Poste en état : {poste['etat_materiel']}"))

    # 2. Check no active session on this poste
    if PosteRepository(conn).has_active_session(poste["id"]):
        _handle_app_error(ConflictError("Ce poste est déjà occupé"))

    # 3. Find the voucher by code (must exist, utilise=0)
    v_repo = VoucherRepository(conn)
    v = v_repo.get_by_code(payload.voucher_code)
    if not v or v.get("utilise"):
        _handle_app_error(NotFoundError("Voucher invalide ou déjà utilisé"))

    # 4. Start the session using SessionStartIn
    from app.schemas import SessionStartIn
    session_start_payload = SessionStartIn(
        poste_id=poste["id"],
        tarif_code=payload.tarif_code,
        mode_facturation="voucher",
        voucher_code=payload.voucher_code,
        client_id=None,
        notes="Session démarrée par voucher client"
    )

    svc = build_session_service(conn)
    try:
        row = svc.demarrer(session_start_payload, employe_id=None)
        build_journal(conn).log("SESSION_START_CLIENT_VOUCHER", None, f"poste={poste['id']} voucher={payload.voucher_code}", poste["id"])
        conn.commit()
        return {"ok": True, "message": "Session démarrée avec voucher", "session": _map_session(row)}
    except AppError as exc:
        conn.rollback()
        _handle_app_error(exc)


@router.post("/client/poste/{numero}/auth/compte")
def client_auth_compte(numero: int, payload: ClientAuthCompteIn, conn=Depends(get_db)):
    from app.repositories.poste_repository import PosteRepository

    # 1. Find the poste by numero (must be actif=1, etat_materiel='ok')
    poste = PosteRepository(conn)._one(
        "SELECT id, etat_materiel FROM postes WHERE numero = ? AND actif = 1",
        (numero,),
    )
    if not poste:
        _handle_app_error(NotFoundError("Poste introuvable"))
    if poste.get("etat_materiel") in ("panne", "eteint", "maintenance"):
        _handle_app_error(ConflictError(f"Poste en état : {poste['etat_materiel']}"))

    # 2. Check no active session on this poste
    if PosteRepository(conn).has_active_session(poste["id"]):
        _handle_app_error(ConflictError("Ce poste est déjà occupé"))

    # 3. Find the client by code (must exist, actif=1)
    client = BaseRepository(conn)._one(
        "SELECT id, nom, solde_xaf FROM clients WHERE code = ? AND actif = 1",
        (payload.client_code.strip(),),
    )
    if not client:
        _handle_app_error(NotFoundError("Compte client introuvable ou inactif"))
    if float(client["solde_xaf"]) <= 0:
        _handle_app_error(ValidationError("Solde client insuffisant"))

    # 4. Start the session using SessionStartIn
    from app.schemas import SessionStartIn
    session_start_payload = SessionStartIn(
        poste_id=poste["id"],
        tarif_code="normal",  # Default tariff for client account login
        mode_facturation="compte",
        voucher_code=None,
        client_id=client["id"],
        notes="Session démarrée par compte client"
    )

    svc = build_session_service(conn)
    try:
        row = svc.demarrer(session_start_payload, employe_id=None)
        build_journal(conn).log("SESSION_START_CLIENT_COMPTE", None, f"poste={poste['id']} client_id={client['id']}", poste["id"])
        conn.commit()
        return {
            "ok": True,
            "message": f"Bienvenue {client['nom']}! Session démarrée.",
            "session": _map_session(row),
            "client_nom": client["nom"],
            "solde": client["solde_xaf"]
        }
    except AppError as exc:
        conn.rollback()
        _handle_app_error(exc)

