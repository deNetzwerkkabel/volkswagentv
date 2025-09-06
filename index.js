const { app, BrowserWindow, autoUpdater, dialog } = require('electron');
const { updateElectronApp } = require('update-electron-app');

const server = 'https://update.electronjs.org';
const feed = `${server}/deNetzwerkkabel/volkswagentv/${process.platform}-${process.arch}/${app.getVersion()}`;

autoUpdater.setFeedURL({ url: feed });

app.on('ready', () => {
  autoUpdater.checkForUpdatesAndNotify();

  autoUpdater.on('update-available', () => {
    dialog.showMessageBox({
      type: 'info',
      title: 'Update verfügbar',
      message: 'Ein neues Update wird heruntergeladen und installiert.'
    });
  });

  autoUpdater.on('update-downloaded', () => {
    autoUpdater.quitAndInstall();
  });

  const createWindow = () => {
    const win = new BrowserWindow({
      kiosk: true,
      autoHideMenuBar: true
    });

    win.loadFile('index.html');
  }

  app.whenReady().then(() => {
    createWindow()
  })

  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
  });
});