const { app, BrowserWindow } = require('electron')
const { updateElectronApp } = require('update-electron-app');

updateElectronApp();

const createWindow = () => {
  const win = new BrowserWindow({
    kiosk: true,
    autoHideMenuBar: true
  })

  win.loadFile('index.html')
}

app.whenReady().then(() => {
  createWindow()
})

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit()
  })