const { app, BrowserWindow } = require('electron');

function createWindow() {
    const win = new BrowserWindow({
        width: 1200,
        height: 800,
        title: "Pure Searx",
        webPreferences: {
            nodeIntegration: false, // turn off Node in renderer for security
            contextIsolation: true, // isolate context
        }
    });

    // Load your local SearxNG server
    win.loadURL('http://127.0.0.1:8888');

    // Optional: prevent navigation outside your server
    win.webContents.on('will-navigate', (event, url) => {
        if (!url.startsWith('http://127.0.0.1:8888')) {
            event.preventDefault();
        }
    });
}

app.whenReady().then(createWindow);

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});
