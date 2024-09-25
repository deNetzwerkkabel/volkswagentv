#!/bin/bash

# Variablen
SERVER_URL="http://example.com/path/to/file.zip" # URL der .zip-Datei
ZIP_FILE="/tmp/file.zip"
USER_DIR="$HOME/my_directory"
INDEX_FILE="$USER_DIR/index.html"

# 1. Herunterladen der .zip-Datei
echo "Lade Datei herunter..."
wget -O "$ZIP_FILE" "$SERVER_URL"

# 2. Entpacken der .zip-Datei in das User-Verzeichnis
echo "Entpacke die Datei..."
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
Name=Chromium Kiosk Mode
EOL

echo "Fertig! Chromium wird im Kiosk-Modus bei Systemstart ausgeführt."
