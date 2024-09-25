#!/bin/bash

# curl -sSL https://raw.githubusercontent.com/deNetzwerkkabel/volkswagentv/refs/tags/0.1/install.sh | bash

# Variablen
ZIP_FILE="/tmp/volkswagentv.zip"
USER_DIR="$HOME/volkswagentv"
INDEX_FILE="$USER_DIR/index.html"

# 1. Download of the .zip-File
echo "Lade die neuste Version von GitHub herunter"
curl -s https://api.github.com/repos/deNetzwerkkabel/volkswagentv/releases/latest \
| grep "browser_download_url.*zip" \
| cut -d : -f 2,3 \
| tr -d \" \
| wget  -O "$ZIP_FILE" -qi -

# 2. Upacking of the .zip-File into home-Directory
echo "Entpacke alle Dateien..."
mkdir -p "$USER_DIR"
unzip "$ZIP_FILE" -d "$USER_DIR"

# 3. Prüfen, ob Chromium installiert ist
if ! command -v chromium-browser &> /dev/null && ! command -v chromium &> /dev/null; then
    echo "Chromium ist nicht installiert. Installiere Chromium..."
    sudo apt-get update
    sudo apt-get install -y chromium-browser
fi

# 4. Chromium im Autostart setzen
AUTOSTART_DIR="$HOME/.config/autostart"
AUTOSTART_FILE="$AUTOSTART_DIR/chromium_autostart.desktop"

echo "Setze Chromium in den Autostart..."
mkdir -p "$AUTOSTART_DIR"
cat > "$AUTOSTART_FILE" <<EOL
[Desktop Entry]
Type=Application
Exec=chromium-browser --kiosk --disable-infobars --noerrdialogs --disable-session-crashed-bubble --disable-component-update "$INDEX_FILE"
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=VolkswagenTV Kiosk-Mode
EOL

echo "Fertig! VolkswagenTV wird beim nächsten Neustart automatisch gestartet"
