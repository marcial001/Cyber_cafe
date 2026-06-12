const REFRESH_MS = 1500;

const ROLE_LABELS = {
  admin: "Administrateur",
  manager: "Manager",
  employe: "Caissier",
};

const state = {
  token: null,
  user: null,
  postes: [],
  tarifs: [],
  clients: [],
  selected: null,
  clientPoste: null,
  clientPosteNum: 1,
  activePanel: "main",
  pollStarted: false,
};

function can(perm) {
  const p = state.user?.permissions || [];
  if (p.includes("*")) return true;
  return p.includes(perm);
}

function showView(id) {
  document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
  document.getElementById(id).classList.add("active");
}

function showPanel(panelId) {
  state.activePanel = panelId;
  document.querySelectorAll(".admin-panel").forEach((p) => p.classList.remove("active"));
  document.getElementById(`panel-${panelId}`)?.classList.add("active");
  document.querySelectorAll(".menu-item[data-panel]").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.panel === panelId);
  });
  if (panelId === "timecodes") refreshVouchersPanel();
  if (panelId === "accounts") refreshClientsPanel();
  if (panelId === "reports") refreshReportsPanel();
  if (panelId === "admin") refreshAdminPanel();
}

function applyRoleUi() {
  const role = state.user?.role || "";
  document.getElementById("userRole").textContent = ROLE_LABELS[role] || role;

  const menuRules = {
    timecodes: "vouchers",
    accounts: "clients",
    reports: "reports",
    admin: "admin",
  };
  document.querySelectorAll(".menu-item[data-panel]").forEach((btn) => {
    const panel = btn.dataset.panel;
    if (panel === "main") {
      btn.classList.remove("hidden");
      return;
    }
    const need = menuRules[panel];
    const show = need ? can(need) : true;
    btn.classList.toggle("hidden", !show);
  });

  document.querySelectorAll(".quick-btn[data-perm]").forEach((btn) => {
    btn.classList.toggle("hidden", !can(btn.dataset.perm));
  });

  document.getElementById("btnWol")?.classList.toggle("hidden", !can("remote"));
  document.getElementById("btnLockUnused")?.classList.toggle("hidden", !can("remote"));
  document.getElementById("voucherCreateForm")?.classList.toggle("hidden", !can("vouchers"));
}

function toast(msg, type = "error") {
  const el = document.getElementById("adminToast");
  if (!el) return;
  el.textContent = msg;
  el.className = `toast ${type}`;
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 4000);
}

function showModal(title, html) {
  document.getElementById("modalTitle").textContent = title;
  document.getElementById("modalBody").innerHTML = html;
  document.getElementById("modalOverlay").classList.remove("hidden");
}

function hideModal() {
  document.getElementById("modalOverlay").classList.add("hidden");
}

function hourlyRate(poste) {
  if (poste?.tarif_prix_heure != null) return Number(poste.tarif_prix_heure);
  const tarif = state.tarifs.find((t) => t.code === poste?.tarif_code);
  if (tarif) return Number(tarif.prix_par_heure);
  return Number(poste?.groupe_prix_heure || 0);
}

async function refreshDashboard() {
  const dash = await Api.get("/dashboard");
  state.postes = dash.postes || [];
  const s = dash.stats || {};
  document.getElementById("statRecettes").textContent = formatXaf(s.recettes_totales);
  document.getElementById("statSessions").textContent = String(s.nombre_sessions ?? 0);
  document.getElementById("statOccupes").textContent = String(dash.occupes ?? 0);
  document.getElementById("statLibres").textContent = String(dash.libres ?? 0);
  renderFloorPlan();
  updateTransferList();
  if (state.selected) {
    const p = state.postes.find((x) => x.id === state.selected.id);
    if (p) selectPoste(p);
  }
}

function renderFloorPlan() {
  const plan = document.getElementById("floorPlan");
  const filter = document.getElementById("filterGroupe")?.value || "";
  const list = filter ? state.postes.filter((p) => p.groupe_code === filter) : state.postes;
  plan.innerHTML = list
    .map((p) => {
      const cls = p.etat;
      const icon = p.groupe_code === "gaming" ? "🎮" : "💻";
      return `
        <article class="pc-node ${cls} ${state.selected?.id === p.id ? "selected" : ""}"
          data-id="${p.id}" tabindex="0" role="gridcell">
          <span class="icon">${icon}</span>
          <span class="name">${escapeHtml(p.libelle)}</span>
          <span class="grp">${escapeHtml(p.groupe_libelle)}</span>
          <span class="state">${escapeHtml(p.etat)}</span>
        </article>`;
    })
    .join("");
  plan.querySelectorAll(".pc-node").forEach((node) => {
    node.onclick = () => {
      const p = state.postes.find((x) => x.id === Number(node.dataset.id));
      if (p) selectPoste(p);
    };
  });
}

function selectPoste(p) {
  state.selected = p;
  document.getElementById("selectedLabel").textContent = `${p.libelle} — ${p.groupe_libelle}`;
  const active = p.etat === "occupe" || p.etat === "pause";
  document.getElementById("btnStart").disabled = active || p.etat_materiel !== "ok";
  document.getElementById("btnStop").disabled = !active;
  document.getElementById("btnPause").disabled = p.etat !== "occupe";
  document.getElementById("btnResume").disabled = p.etat !== "pause";
  document.getElementById("btnExtend").disabled = !active;
  document.getElementById("btnTransfer").disabled = !active;
  document.getElementById("billPos").textContent = formatXaf(p.montant_pos || 0);
  renderFloorPlan();
  updateChrono();
}

function updateChrono() {
  const el = document.getElementById("chronoDisplay");
  const p = state.selected;
  if (!p?.session_debut || !["occupe", "pause"].includes(p.etat)) {
    el.textContent = "00:00:00";
    document.getElementById("billPc").textContent = formatXaf(0);
    document.getElementById("billTotal").textContent = formatXaf(p?.montant_pos || 0);
    return;
  }
  el.textContent = formatTimer(elapsedSeconds(p.session_debut));
  const est = (elapsedSeconds(p.session_debut) / 3600) * hourlyRate(p);
  document.getElementById("billPc").textContent = formatXaf(est);
  document.getElementById("billTotal").textContent = formatXaf(est + Number(p.montant_pos || 0));
}

function updateTransferList() {
  const sel = document.getElementById("transferSelect");
  const p = state.selected;
  if (!sel) return;
  const libres = state.postes.filter((x) => x.etat === "libre" && x.etat_materiel === "ok" && x.id !== p?.id);
  sel.innerHTML = libres.map((x) => `<option value="${x.id}">${escapeHtml(x.libelle)}</option>`).join("");
  sel.disabled = libres.length === 0;
}

async function loadTarifs() {
  state.tarifs = await Api.get("/tarifs");
  const sel = document.getElementById("tarifSelect");
  sel.innerHTML = state.tarifs
    .map((t) => `<option value="${t.code}">${escapeHtml(t.libelle)} — ${formatXaf(t.prix_par_heure)}/h</option>`)
    .join("");
}

async function loadClients() {
  if (!can("clients")) return;
  try {
    state.clients = await Api.get("/clients");
    const sel = document.getElementById("clientSelect");
    sel.innerHTML =
      '<option value="">— Choisir un client —</option>' +
      state.clients
        .map(
          (c) =>
            `<option value="${c.id}">${escapeHtml(c.nom)} (${escapeHtml(c.code)}) — ${formatXaf(c.solde_xaf)}</option>`
        )
        .join("");
  } catch (ex) {
    toast(ex.message);
  }
}

async function refreshVouchersPanel() {
  if (!can("vouchers")) return;
  const list = await Api.get("/vouchers");
  document.getElementById("vouchersTable").innerHTML = `
    <table><tr><th>Code</th><th>Durée</th><th>Utilisé</th><th>Expire (h)</th></tr>
    ${list
      .map(
        (v) => `
      <tr class="${v.utilise ? "used" : ""}">
        <td>${escapeHtml(v.code)}</td>
        <td>${Math.round((v.duree_secondes || 0) / 60)} min</td>
        <td>${v.utilise ? "Oui" : "Non"}</td>
        <td>${v.expire_heures ?? "—"}</td>
      </tr>`
      )
      .join("")}
    </table>`;
}

async function refreshClientsPanel() {
  if (!can("clients")) return;
  await loadClients();
  document.getElementById("clientsTable").innerHTML = `
    <table><tr><th>Code</th><th>Nom</th><th>Solde</th><th>Points</th></tr>
    ${state.clients
      .map(
        (c) => `
      <tr>
        <td>${escapeHtml(c.code)}</td>
        <td>${escapeHtml(c.nom)}</td>
        <td>${formatXaf(c.solde_xaf)}</td>
        <td>${c.points_fidelite ?? 0}</td>
      </tr>`
      )
      .join("")}
    </table>`;
}

async function refreshReportsPanel() {
  if (!can("reports")) return;
  const s = await Api.get("/stats/journalieres");
  const top = (s.postes_plus_utilises || [])
    .map((p) => `<li>${escapeHtml(p.libelle || p.poste)} — ${p.minutes ?? p.duree ?? 0} min</li>`)
    .join("");
  document.getElementById("reportsContent").innerHTML = `
    <div class="report-card"><span class="l">Date</span><span class="v">${escapeHtml(s.date)}</span></div>
    <div class="report-card"><span class="l">Recettes</span><span class="v">${formatXaf(s.recettes_totales)}</span></div>
    <div class="report-card"><span class="l">Sessions</span><span class="v">${s.nombre_sessions}</span></div>
    <div class="report-card" style="grid-column:1/-1"><span class="l">Postes les plus utilisés</span><ul>${top || "<li>—</li>"}</ul></div>`;
}

async function refreshAdminPanel() {
  if (!can("admin")) return;
  const [employes, roles] = await Promise.all([Api.get("/admin/employes"), Api.get("/admin/roles")]);
  document.getElementById("adminEmployes").innerHTML = `
    <table><tr><th>Login</th><th>Nom</th><th>Rôle</th></tr>
    ${employes.map((e) => `<tr><td>${escapeHtml(e.login)}</td><td>${escapeHtml(e.nom)}</td><td>${escapeHtml(e.role_libelle || e.role)}</td></tr>`).join("")}
    </table>`;
  document.getElementById("adminRoles").innerHTML = `
    <table><tr><th>Rôle</th><th>Permissions</th></tr>
    ${roles.map((r) => `<tr><td>${escapeHtml(r.libelle)}</td><td><code>${escapeHtml(r.permissions)}</code></td></tr>`).join("")}
    </table>`;
}

const PANEL_PERMS = { timecodes: "vouchers", accounts: "clients", reports: "reports", admin: "admin" };

document.querySelectorAll(".menu-item[data-panel]")?.forEach((btn) => {
  btn.addEventListener("click", () => {
    const panel = btn.dataset.panel;
    const need = PANEL_PERMS[panel];
    if (!need || can(need)) showPanel(panel);
    else toast("Accès refusé pour votre rôle");
  });
});

document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const err = document.getElementById("loginError");
  err.classList.add("hidden");
  try {
    const res = await Api.login(
      document.getElementById("loginUser").value,
      document.getElementById("loginPass").value
    );
    state.token = res.token;
    state.user = res.employe;
    await Api.setToken(res.token);
    document.getElementById("userName").textContent = res.employe.nom;
    applyRoleUi();
    await loadTarifs();
    await loadClients();
    showView("view-admin");
    showPanel("main");
    await refreshDashboard();
    if (!state.pollStarted) {
      state.pollStarted = true;
      setInterval(poll, REFRESH_MS);
    }
  } catch (ex) {
    err.textContent = ex.message || "Échec connexion";
    err.classList.remove("hidden");
  }
});

document.getElementById("btnLogout")?.addEventListener("click", async () => {
  state.token = null;
  await Api.setToken(null);
  location.reload();
});

document.getElementById("modeSelect")?.addEventListener("change", (e) => {
  const v = e.target.value;
  document.getElementById("voucherRow").classList.toggle("hidden", v !== "voucher");
  document.getElementById("clientRow").classList.toggle("hidden", v !== "compte");
});

document.getElementById("btnStart")?.addEventListener("click", async () => {
  const p = state.selected;
  if (!p) return;
  try {
    const body = {
      poste_id: p.id,
      tarif_code: document.getElementById("tarifSelect").value,
      mode_facturation: document.getElementById("modeSelect").value,
      notes: document.getElementById("sessionNotes").value.slice(0, 500) || null,
    };
    if (body.mode_facturation === "voucher") {
      body.voucher_code = document.getElementById("voucherCode").value.trim();
    }
    if (body.mode_facturation === "compte") {
      body.client_id = Number(document.getElementById("clientSelect").value);
      if (!body.client_id) {
        toast("Choisissez un compte client");
        return;
      }
    }
    await Api.post("/sessions/start", body);
    toast("Session démarrée", "success");
    await refreshDashboard();
  } catch (ex) {
    toast(ex.message);
  }
});

document.getElementById("btnStop")?.addEventListener("click", async () => {
  const p = state.selected;
  if (!p?.session_id) return;
  try {
    await Api.post("/sessions/stop", { session_id: p.session_id });
    const t = await Api.get(`/sessions/${p.session_id}/ticket`);
    showModal("Ticket de caisse", `
      <p><strong>${escapeHtml(t.numero_ticket)}</strong></p>
      <p>Poste ${t.poste_numero} — ${escapeHtml(t.tarif_libelle)}</p>
      <p>Durée: ${t.duree_minutes} min</p>
      <p>PC: ${formatXaf(t.montant_pc)} | POS: ${formatXaf(t.montant_pos)} | Taxes: ${formatXaf(t.montant_taxes)}</p>
      <p class="total">Total: ${formatXaf(t.montant)}</p>`);
    toast("Session terminée", "success");
    await refreshDashboard();
    if (can("clients")) await loadClients();
  } catch (ex) {
    toast(ex.message);
  }
});

document.getElementById("btnPause")?.addEventListener("click", async () => {
  try {
    await Api.post("/sessions/pause", { session_id: state.selected.session_id });
    await refreshDashboard();
  } catch (ex) {
    toast(ex.message);
  }
});

document.getElementById("btnResume")?.addEventListener("click", async () => {
  try {
    await Api.post("/sessions/reprendre", { session_id: state.selected.session_id });
    await refreshDashboard();
  } catch (ex) {
    toast(ex.message);
  }
});

document.getElementById("btnExtend")?.addEventListener("click", async () => {
  try {
    const minutes = Number(document.getElementById("extendMin").value);
    await Api.post("/sessions/prolonger", { session_id: state.selected.session_id, minutes });
    toast(`+${minutes} min`, "success");
    await refreshDashboard();
  } catch (ex) {
    toast(ex.message);
  }
});

document.getElementById("btnTransfer")?.addEventListener("click", async () => {
  try {
    const newId = Number(document.getElementById("transferSelect").value);
    await Api.post("/sessions/transferer", {
      session_id: state.selected.session_id,
      new_poste_id: newId,
    });
    toast("Session transférée", "success");
    await refreshDashboard();
  } catch (ex) {
    toast(ex.message);
  }
});

document.getElementById("btnWol")?.addEventListener("click", async () => {
  try {
    const r = await Api.post("/infrastructure/wol", {});
    toast(r.message, "success");
  } catch (ex) {
    toast(ex.message);
  }
});

document.getElementById("btnLockUnused")?.addEventListener("click", async () => {
  try {
    const r = await Api.post("/postes/verrouiller-libres", {});
    toast(r.message || `${r.verrouilles} poste(s) verrouillé(s)`, "success");
    await refreshDashboard();
  } catch (ex) {
    toast(ex.message);
  }
});

document.getElementById("voucherCreateForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await Api.post("/vouchers", {
      code: document.getElementById("newVoucherCode").value,
      duree_minutes: Number(document.getElementById("newVoucherMin").value),
    });
    toast("Code créé", "success");
    document.getElementById("newVoucherCode").value = "";
    await refreshVouchersPanel();
  } catch (ex) {
    toast(ex.message);
  }
});

document.getElementById("filterGroupe")?.addEventListener("change", renderFloorPlan);
document.getElementById("modalClose")?.addEventListener("click", hideModal);
document.getElementById("modalOverlay")?.addEventListener("click", (e) => {
  if (e.target.id === "modalOverlay") hideModal();
});

document.querySelectorAll(".quick-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const perm = btn.dataset.perm;
    if (perm && !can(perm)) {
      toast("Fonction non autorisée pour votre rôle");
      return;
    }
    openQuickModal(btn.dataset.modal);
  });
});

async function openQuickModal(type) {
  try {
    if (type === "pos") await modalPos();
    else if (type === "logs") await modalLogs();
    else if (type === "stock") await modalStock();
    else if (type === "chat") await modalChat();
    else if (type === "manual") await modalManual();
    else showModal("Module", "<p>Réservations — à planifier (manager/admin).</p>");
  } catch (ex) {
    toast(ex.message);
  }
}

async function modalPos() {
  if (!can("pos")) {
    toast("Ventes POS réservées aux rôles autorisés");
    return;
  }
  const produits = await Api.get("/produits");
  if (!state.selected?.session_id) {
    toast("Sélectionnez un poste avec session active");
    return;
  }
  const html = `
    <p class="hint">Poste <strong>${escapeHtml(state.selected.libelle)}</strong> — clic pour ajouter à la note.</p>
    <div class="pos-grid" id="posGrid">
      ${produits
        .map(
          (p) => `
        <button type="button" class="pos-tile ${p.stock <= p.seuil_alerte ? "low-stock" : ""}" data-id="${p.id}">
          <strong>${escapeHtml(p.libelle)}</strong><br/>
          ${formatXaf(p.prix)}<br/><small>Stock: ${p.stock}</small>
        </button>`
        )
        .join("")}
    </div>`;
  showModal("Point de vente (POS)", html);
  document.getElementById("posGrid")?.addEventListener("click", async (e) => {
    const tile = e.target.closest(".pos-tile");
    if (!tile || !state.selected?.session_id) return;
    try {
      await Api.post("/pos/vente", {
        session_id: state.selected.session_id,
        poste_id: state.selected.id,
        items: [{ produit_id: Number(tile.dataset.id), quantite: 1 }],
      });
      toast("Article ajouté", "success");
      hideModal();
      await refreshDashboard();
    } catch (ex) {
      toast(ex.message);
    }
  });
}

async function modalLogs() {
  const logs = await Api.get("/journaux");
  showModal(
    "Journal d'audit",
    `<table class="log-table"><tr><th>Date</th><th>Action</th><th>Agent</th></tr>
    ${logs.map((l) => `<tr><td>${escapeHtml(l.created_at)}</td><td>${escapeHtml(l.action)}</td><td>${escapeHtml(l.employe_nom || "—")}</td></tr>`).join("")}
    </table>`
  );
}

async function modalStock() {
  const alerts = await Api.get("/produits/alertes");
  showModal(
    "Alertes stock",
    alerts.length
      ? `<ul>${alerts.map((a) => `<li>${escapeHtml(a.libelle)} — ${a.stock} restant</li>`).join("")}</ul>`
      : "<p>Stocks OK</p>"
  );
}

async function modalChat() {
  const msgs = await Api.get("/messages");
  const p = state.selected;
  showModal(
    "Messagerie",
    `${msgs.map((m) => `<p><strong>${escapeHtml(m.expediteur)}</strong> → ${escapeHtml(m.poste_libelle || "Tous")}: ${escapeHtml(m.contenu)}</p>`).join("")}
    <div style="margin-top:1rem">
      <input id="chatInput" placeholder="Message au poste…" style="width:70%" />
      <button type="button" id="chatSend" class="btn-sm">Envoyer</button>
    </div>`
  );
  document.getElementById("chatSend")?.addEventListener("click", async () => {
    if (!p) return toast("Sélectionnez un poste");
    try {
      await Api.post(`/postes/${p.id}/message`, {
        contenu: document.getElementById("chatInput").value,
      });
      hideModal();
      toast("Message envoyé", "success");
    } catch (ex) {
      toast(ex.message);
    }
  });
}

async function modalManual() {
  const s = await Api.get("/services-manuels");
  showModal(
    "Minuteurs manuels (billard, console…)",
    `<ul>${s.map((x) => `<li><strong>${escapeHtml(x.libelle)}</strong> — ${formatXaf(x.prix_par_heure)}/h</li>`).join("")}</ul>`
  );
}

function clientMessage(msg, isError = false) {
  const el = document.getElementById("clientMessage");
  if (!el) return;
  el.textContent = msg;
  el.classList.toggle("error", isError);
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 5000);
}

async function fetchClientStatus() {
  const num = state.clientPosteNum;
  const data = await Api.get(`/client/poste/${num}/status`);
  state.clientPoste = data.poste;
  state.clientProduits = data.produits || [];
  return data;
}

async function loadClientTarifs() {
  try {
    const tarifs = await Api.get(`/client/poste/${state.clientPosteNum}/tarifs`);
    const sel = document.getElementById("clVoucherTarif");
    if (sel) {
      sel.innerHTML = tarifs
        .map((t) => `<option value="${t.code}">${escapeHtml(t.libelle)} — ${formatXaf(t.prix_par_heure)}/h</option>`)
        .join("");
    }
  } catch (ex) {
    console.error("Erreur chargement tarifs client:", ex);
  }
}

async function syncClientView() {
  try {
    const data = await fetchClientStatus();
    const occ = data.poste;
    
    // Update login screen tags
    const clPosteTag = document.getElementById("clPosteTag");
    if (clPosteTag) clPosteTag.textContent = occ.libelle || `PC-${state.clientPosteNum}`;
    
    const active = occ.etat === "occupe" || occ.etat === "pause";
    const loginScreen = document.getElementById("client-login-screen");
    const activeScreen = document.getElementById("client-active-screen");
    
    if (active) {
      if (loginScreen.classList.contains("active")) {
        loginScreen.classList.remove("active");
        activeScreen.classList.add("active");
        switchClientTab("accueil");
        resetSnakeGame();
      }
      
      document.getElementById("clientPosteLabel").textContent = occ.libelle || `PC-${state.clientPosteNum}`;
      document.getElementById("clientStatus").textContent = occ.etat === "pause" ? "En pause" : "Session active";
      
      const welcome = document.getElementById("clientWelcome");
      if (occ.client_nom) {
        welcome.textContent = `Client: ${escapeHtml(occ.client_nom)}`;
        welcome.classList.remove("hidden");
      } else if (occ.mode_facturation === "voucher") {
        welcome.textContent = `Ticket prépayé : ${escapeHtml(occ.numero_ticket || "Actif")}`;
        welcome.classList.remove("hidden");
      } else {
        welcome.textContent = `Session caisse / Post-payé`;
        welcome.classList.remove("hidden");
      }
      
      if (occ.session_debut) {
        const elapsed = elapsedSeconds(occ.session_debut);
        document.getElementById("clientTimer").textContent = formatTimer(elapsed);
        const est = (elapsed / 3600) * hourlyRate(occ);
        document.getElementById("clientPc").textContent = formatXaf(est);
        document.getElementById("clientPos").textContent = formatXaf(occ.montant_pos || 0);
        document.getElementById("clientTotal").textContent = formatXaf(est + Number(occ.montant_pos || 0));
      }
      
      const grid = document.getElementById("clientSnacksGrid");
      if (grid && grid.children.length === 0) {
        renderClientSnacks(data.produits || []);
      }
    } else {
      if (activeScreen.classList.contains("active")) {
        activeScreen.classList.remove("active");
        loginScreen.classList.add("active");
        
        document.getElementById("clVoucherCode").value = "";
        document.getElementById("clClientCode").value = "";
        
        // Reset snacks grid so it re-renders on next login
        const grid = document.getElementById("clientSnacksGrid");
        if (grid) grid.innerHTML = "";
      }
      
      const waitLabel = document.getElementById("clWaitingStatus");
      if (waitLabel) {
        waitLabel.textContent = "En attente d'activation par le caissier...";
      }
    }
  } catch (ex) {
    console.error("syncClientView error:", ex);
  }
}

function renderClientSnacks(produits) {
  const grid = document.getElementById("clientSnacksGrid");
  if (!grid) return;
  grid.innerHTML = produits
    .map(
      (p) => `
      <button type="button" class="pos-tile" data-id="${p.id}" ${p.stock <= 0 ? "disabled" : ""}>
        <strong>${escapeHtml(p.libelle)}</strong>
        <span class="pos-tile-price">${formatXaf(p.prix)}</span>
        <span class="pos-tile-stock">Stock: ${p.stock > 0 ? p.stock : "Épuisé"}</span>
      </button>`
    )
    .join("");
    
  grid.querySelectorAll(".pos-tile").forEach((tile) => {
    tile.onclick = async () => {
      try {
        await Api.post(`/client/poste/${state.clientPosteNum}/commande`, {
          produit_id: Number(tile.dataset.id),
        });
        toast("Commande envoyée !", "success");
        clientMessage("Commande snacks enregistrée et ajoutée à votre compte.");
        await syncClientView();
      } catch (ex) {
        clientMessage(ex.message, true);
      }
    };
  });
}

function switchClientTab(tab) {
  document.querySelectorAll(".taskbar-tab").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tab === tab);
  });
  document.querySelectorAll(".desktop-pane").forEach((pane) => {
    pane.classList.toggle("active", pane.id === `pane-${tab}`);
  });
  
  if (tab === "internet") {
    const webview = document.getElementById("browserWebview");
    const urlInput = document.getElementById("browserUrlInput");
    if (webview && urlInput && !webview.src) {
      webview.src = urlInput.value;
    }
  }
}

// Bind tabs click
document.querySelectorAll(".cl-tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".cl-tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".cl-mode").forEach((m) => m.classList.remove("active"));
    btn.classList.add("active");
    const mode = btn.dataset.mode;
    document.getElementById(`cl-mode-${mode}`).classList.add("active");
  });
});

document.querySelectorAll(".taskbar-tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    switchClientTab(btn.dataset.tab);
  });
});

// Also bind clicks from home dashboard cards
document.addEventListener("click", (e) => {
  const card = e.target.closest(".accueil-card");
  if (card && card.dataset.triggerTab) {
    switchClientTab(card.dataset.triggerTab);
  }
});

// Login Handlers
document.getElementById("btnClVoucher")?.addEventListener("click", async () => {
  const err = document.getElementById("clLoginError");
  err.classList.add("hidden");
  try {
    const code = document.getElementById("clVoucherCode").value.trim();
    const tarif = document.getElementById("clVoucherTarif").value;
    if (!code) {
      err.textContent = "Veuillez entrer un code voucher";
      err.classList.remove("hidden");
      return;
    }
    const res = await Api.post(`/client/poste/${state.clientPosteNum}/auth/voucher`, {
      voucher_code: code,
      tarif_code: tarif,
    });
    toast("Connexion réussie", "success");
    await syncClientView();
  } catch (ex) {
    err.textContent = ex.message || "Échec connexion voucher";
    err.classList.remove("hidden");
  }
});

document.getElementById("btnClCompte")?.addEventListener("click", async () => {
  const err = document.getElementById("clLoginError");
  err.classList.add("hidden");
  try {
    const code = document.getElementById("clClientCode").value.trim();
    if (!code) {
      err.textContent = "Veuillez entrer votre code client";
      err.classList.remove("hidden");
      return;
    }
    const res = await Api.post(`/client/poste/${state.clientPosteNum}/auth/compte`, {
      client_code: code,
    });
    toast(res.message || "Connexion réussie", "success");
    await syncClientView();
  } catch (ex) {
    err.textContent = ex.message || "Échec connexion compte client";
    err.classList.remove("hidden");
  }
});

// Mini browser toolbar logic
const webview = document.getElementById("browserWebview");
const urlInput = document.getElementById("browserUrlInput");

document.getElementById("btnBrowserBack")?.addEventListener("click", () => {
  if (webview && typeof webview.canGoBack === "function" && webview.canGoBack()) {
    webview.goBack();
  }
});

document.getElementById("btnBrowserForward")?.addEventListener("click", () => {
  if (webview && typeof webview.canGoForward === "function" && webview.canGoForward()) {
    webview.goForward();
  }
});

document.getElementById("btnBrowserReload")?.addEventListener("click", () => {
  webview?.reload();
});

function navigateBrowser() {
  if (!urlInput) return;
  let url = urlInput.value.trim();
  if (!url) return;
  if (!/^https?:\/\//i.test(url)) {
    url = "https://" + url;
  }
  if (webview) {
    webview.src = url;
  }
}

document.getElementById("btnBrowserGo")?.addEventListener("click", navigateBrowser);
urlInput?.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    navigateBrowser();
  }
});

// Update urlInput value when webview navigates
webview?.addEventListener("did-navigate", (e) => {
  if (urlInput) {
    urlInput.value = e.url;
  }
});
webview?.addEventListener("did-navigate-in-page", (e) => {
  if (urlInput) {
    urlInput.value = e.url;
  }
});

// Notepad save logic
document.getElementById("btnSaveNotepad")?.addEventListener("click", () => {
  const text = document.getElementById("notepadTextarea").value;
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `notes_poste_${state.clientPosteNum}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
});

// Calculator Logic
let calcState = {
  current: "0",
  operator: null,
  previous: null,
  resetOnNext: false,
};

function updateCalcDisplay() {
  const display = document.getElementById("calcDisplay");
  if (display) {
    display.textContent = calcState.current;
  }
}

document.querySelectorAll(".calc-key").forEach((key) => {
  key.addEventListener("click", () => {
    const val = key.dataset.val;
    if (!val) return;
    
    if ((val >= "0" && val <= "9") || val === ".") {
      if (calcState.current === "0" || calcState.resetOnNext) {
        calcState.current = val === "." ? "0." : val;
        calcState.resetOnNext = false;
      } else {
        if (val === "." && calcState.current.includes(".")) return;
        calcState.current += val;
      }
      updateCalcDisplay();
    } else if (val === "C") {
      calcState.current = "0";
      calcState.operator = null;
      calcState.previous = null;
      calcState.resetOnNext = false;
      updateCalcDisplay();
    } else if (val === "back") {
      if (calcState.current.length > 1) {
        calcState.current = calcState.current.slice(0, -1);
      } else {
        calcState.current = "0";
      }
      updateCalcDisplay();
    } else if (["+", "-", "*", "/"].includes(val)) {
      calcState.previous = calcState.current;
      calcState.operator = val;
      calcState.resetOnNext = true;
    } else if (val === "=") {
      if (calcState.previous && calcState.operator) {
        const prev = parseFloat(calcState.previous);
        const curr = parseFloat(calcState.current);
        let res = 0;
        switch (calcState.operator) {
          case "+": res = prev + curr; break;
          case "-": res = prev - curr; break;
          case "*": res = prev * curr; break;
          case "/": res = curr !== 0 ? prev / curr : "Error"; break;
        }
        calcState.current = String(res);
        calcState.previous = null;
        calcState.operator = null;
        calcState.resetOnNext = true;
        updateCalcDisplay();
      }
    }
  });
});

// Neon Snake Arcade logic
let gameCanvas = document.getElementById("gameCanvas");
let gameCtx = gameCanvas ? gameCanvas.getContext("2d") : null;
let gameInterval = null;
let gameRunning = false;
let snake = [];
let food = {};
let dx = 10;
let dy = 0;
let score = 0;
let highScore = 0;
const gridSize = 10;

function resetSnakeGame() {
  clearInterval(gameInterval);
  gameInterval = null;
  gameRunning = false;
  score = 0;
  dx = gridSize;
  dy = 0;
  snake = [
    { x: 150, y: 150 },
    { x: 140, y: 150 },
    { x: 130, y: 150 },
  ];
  const gScore = document.getElementById("gameScore");
  if (gScore) gScore.textContent = "0";
  document.getElementById("gameOverlay")?.classList.remove("hidden");
  drawSnakeGameInit();
}

function drawSnakeGameInit() {
  if (!gameCtx || !gameCanvas) return;
  gameCtx.fillStyle = "#050811";
  gameCtx.fillRect(0, 0, gameCanvas.width, gameCanvas.height);
}

function startSnakeGame() {
  if (gameRunning) return;
  gameRunning = true;
  document.getElementById("gameOverlay")?.classList.add("hidden");
  food = getRandomFoodPos();
  gameInterval = setInterval(gameStep, 80);
}

function getRandomFoodPos() {
  if (!gameCanvas) return { x: 100, y: 100 };
  const max = gameCanvas.width - gridSize;
  const x = Math.floor(Math.random() * (max / gridSize)) * gridSize;
  const y = Math.floor(Math.random() * (max / gridSize)) * gridSize;
  return { x, y };
}

function gameStep() {
  if (!gameCanvas) return;
  if (checkGameOver()) {
    resetSnakeGame();
    return;
  }
  
  const head = { x: snake[0].x + dx, y: snake[0].y + dy };
  snake.unshift(head);
  
  if (head.x === food.x && head.y === food.y) {
    score += 10;
    const gScore = document.getElementById("gameScore");
    if (gScore) gScore.textContent = String(score);
    if (score > highScore) {
      highScore = score;
      const gHi = document.getElementById("gameHighScore");
      if (gHi) gHi.textContent = String(highScore);
    }
    food = getRandomFoodPos();
  } else {
    snake.pop();
  }
  
  drawGame();
}

function checkGameOver() {
  if (!gameCanvas) return true;
  const head = snake[0];
  if (head.x < 0 || head.x >= gameCanvas.width || head.y < 0 || head.y >= gameCanvas.height) {
    return true;
  }
  for (let i = 1; i < snake.length; i++) {
    if (snake[i].x === head.x && snake[i].y === head.y) {
      return true;
    }
  }
  return false;
}

function drawGame() {
  if (!gameCtx || !gameCanvas) return;
  gameCtx.fillStyle = "#050811";
  gameCtx.fillRect(0, 0, gameCanvas.width, gameCanvas.height);
  
  gameCtx.fillStyle = "#ef4444";
  gameCtx.shadowColor = "#ef4444";
  gameCtx.shadowBlur = 10;
  gameCtx.fillRect(food.x, food.y, gridSize, gridSize);
  
  snake.forEach((part, index) => {
    gameCtx.fillStyle = index === 0 ? "#60a5fa" : "#3b82f6";
    gameCtx.shadowColor = "#3b82f6";
    gameCtx.shadowBlur = index === 0 ? 8 : 4;
    gameCtx.fillRect(part.x, part.y, gridSize - 1, gridSize - 1);
  });
  
  gameCtx.shadowBlur = 0;
}

document.addEventListener("keydown", (e) => {
  if (!gameRunning) {
    if (e.key === "Enter" && document.getElementById("pane-jeux")?.classList.contains("active")) {
      startSnakeGame();
    }
    return;
  }
  
  const key = e.key;
  if ((key === "ArrowLeft" || key === "q" || key === "Q") && dx === 0) {
    dx = -gridSize;
    dy = 0;
  } else if ((key === "ArrowUp" || key === "z" || key === "Z") && dy === 0) {
    dx = 0;
    dy = -gridSize;
  } else if ((key === "ArrowRight" || key === "d" || key === "D") && dx === 0) {
    dx = gridSize;
    dy = 0;
  } else if ((key === "ArrowDown" || key === "s" || key === "S") && dy === 0) {
    dx = 0;
    dy = gridSize;
  }
  
  if (["ArrowLeft", "ArrowUp", "ArrowRight", "ArrowDown", " "].includes(e.key) && document.getElementById("pane-jeux")?.classList.contains("active")) {
    e.preventDefault();
  }
});

document.getElementById("gameOverlay")?.addEventListener("click", startSnakeGame);

// View Client Launch
document.getElementById("btnClientMode")?.addEventListener("click", () => {
  state.clientPosteNum = Number(document.getElementById("clientPosteNum")?.value || 1);
  showView("view-client");
  loadClientTarifs();
  syncClientView();
  if (!state.clientPollStarted) {
    state.clientPollStarted = true;
    setInterval(() => {
      if (document.getElementById("view-client").classList.contains("active")) syncClientView();
    }, REFRESH_MS);
  }
});

document.getElementById("btnBackAdmin")?.addEventListener("click", () => {
  if (state.token) {
    showView("view-admin");
    showPanel(state.activePanel || "main");
  } else showView("view-login");
});

document.getElementById("btnEndClient")?.addEventListener("click", async () => {
  try {
    const r = await Api.post(`/client/poste/${state.clientPosteNum}/demande-fin`, {});
    clientMessage(r.message || "Demande envoyée à la caisse.");
  } catch (ex) {
    clientMessage(ex.message, true);
  }
});

function tick() {
  const now = new Date().toLocaleTimeString("fr-FR");
  const clockTop = document.getElementById("clockTop");
  if (clockTop) clockTop.textContent = now;
  const clClockLogin = document.getElementById("clClockLogin");
  if (clClockLogin) clClockLogin.textContent = now;
  const clientClock = document.getElementById("clientClock");
  if (clientClock) clientClock.textContent = now;
  updateChrono();
}

async function poll() {
  if (!state.token) return;
  try {
    await refreshDashboard();
    document.getElementById("serverStatus").className = "badge badge-ok";
    document.getElementById("serverStatus").textContent = "Serveur connecté";
  } catch {
    document.getElementById("serverStatus").className = "badge badge-err";
    document.getElementById("serverStatus").textContent = "Serveur hors ligne";
  }
}

setInterval(tick, 1000);

