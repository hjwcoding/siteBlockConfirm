const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  // Load the index.html of the app.
  // In development, this will be served by webpack-dev-server.
  // In production, it will be a file path.
  mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));

  // Open the DevTools.
  mainWindow.webContents.openDevTools();
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

const { exec } = require('child_process');
const fs = require('fs');

ipcMain.handle('run-domain-check', async (event, domain) => {
  return new Promise((resolve) => {
    exec(`nslookup ${domain}`, (error, stdout, stderr) => {
      let ip = null;

      // Check for explicit failure indicators first.
      const isFailure = error || stdout.includes("can't find") || stdout.includes("Non-existent domain");

      if (!isFailure) {
        // If no explicit failure, try to parse a valid IP from the answer block.
        let searchBlock = stdout;
        const nonAuthMarker = 'Non-authoritative answer:';
        const nonAuthIndex = stdout.indexOf(nonAuthMarker);

        if (nonAuthIndex !== -1) {
          searchBlock = stdout.substring(nonAuthIndex);
        } else {
          const serverAddrMatch = stdout.match(/Address:\s+((?:[0-9]{1,3}\.){3}[0-9]{1,3})/);
          if (serverAddrMatch) {
              const serverAddrEndIndex = stdout.indexOf(serverAddrMatch[0]) + serverAddrMatch[0].length;
              searchBlock = stdout.substring(serverAddrEndIndex);
          }
        }

        const ipMatches = searchBlock.match(/((?:[0-9]{1,3}\.){3}[0-9]{1,3})/g);
        if (ipMatches && ipMatches.length > 0) {
          ip = ipMatches[0];
        }
      }

      // Final decision: if we found an IP and there was no failure, it's a success.
      // Otherwise, it's a failure with the unified error message.
      if (ip) {
        resolve(`IP 확인 성공! :: ${ip}`);
      } else {
        resolve(`오류: '${domain}'을(를) 찾을 수 없습니다.`);
      }
    });
  });
});


ipcMain.handle('get-tuples-list', async (event) => {
  try {
    const filePath = path.join(__dirname, '..', 'tuples_list.json');
    const data = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('Failed to read tuples_list.json:', error);
    return [];
  }
});

ipcMain.handle('get-domain-list', async (event) => {
  try {
    const filePath = path.join(__dirname, '..', 'domain_list.json');
    const data = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('Failed to read domain_list.json:', error);
    return [];
  }
});
