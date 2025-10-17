const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  getTuplesList: () => ipcRenderer.invoke('get-tuples-list'),
  getDomainList: () => ipcRenderer.invoke('get-domain-list'),
  runDomainCheck: (domain) => ipcRenderer.invoke('run-domain-check', domain),
});
