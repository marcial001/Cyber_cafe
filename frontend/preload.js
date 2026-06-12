const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("cybercafe", {
  setToken: (token) => ipcRenderer.invoke("api:setToken", token),
  login: (login, password) =>
    ipcRenderer.invoke("api:login", { login: String(login), password: String(password) }),
  api: (method, path, body) => ipcRenderer.invoke("api:call", method, path, body),
});
