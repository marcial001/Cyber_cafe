const Api = {
  async setToken(token) {
    await window.cybercafe.setToken(token);
  },

  async login(login, password) {
    return window.cybercafe.login(login, password);
  },

  get(path) {
    return window.cybercafe.api("GET", path);
  },

  post(path, body) {
    return window.cybercafe.api("POST", path, body);
  },
};

function formatXaf(n) {
  const v = Number(n);
  if (!Number.isFinite(v)) return "0 XAF";
  return `${Math.round(v).toLocaleString("fr-FR")} XAF`;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function elapsedSeconds(debutIso) {
  const start = Date.parse(debutIso);
  if (Number.isNaN(start)) return 0;
  return Math.max(0, Math.floor((Date.now() - start) / 1000));
}

function formatTimer(sec) {
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  return [h, m, s].map((x) => String(x).padStart(2, "0")).join(":");
}
