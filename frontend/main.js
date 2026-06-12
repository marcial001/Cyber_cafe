const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");

const API_BASE = process.env.CYBERCAFE_API || "http://127.0.0.1:8010/api/v1";

let authToken = null;

async function apiFetch(pathname, options = {}) {
  const url = `${API_BASE}${pathname}`;
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (authToken) headers["X-Auth-Token"] = authToken;
  const res = await fetch(url, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = data.detail?.message || data.message || "Erreur serveur";
    const err = new Error(msg);
    err.status = res.status;
    throw err;
  }
  return data;
}

ipcMain.handle("api:setToken", (_, token) => {
  authToken = token || null;
});

ipcMain.handle("api:login", (_, body) =>
  apiFetch("/auth/login", { method: "POST", body: JSON.stringify(body) })
);

ipcMain.handle("api:call", (_, method, path, body) => {
  const opts = { method: method || "GET" };
  if (body) opts.body = JSON.stringify(body);
  return apiFetch(path, opts);
});

function createWindow() {
  const win = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1200,
    minHeight: 720,
    title: "CyberCafé Manager Pro",
    backgroundColor: "#0a0e17",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      webviewTag: true,
    },
  });
  win.loadFile(path.join(__dirname, "renderer", "index.html"));
}

app.whenReady().then(createWindow);
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
