import json
import os
import sys
import requests
try:
    import questionary
except ImportError:
    questionary = None

REPOSITORY = "denetzwerkkabel/volkswagentv"
DEALER_LIST_FILE = "dealers.json"
DEALER_CONFIG_FILE = "dealers_config.json"
DEALER_LOCK_FILE = "dealer.lock"


def fetch_github_release_assets(repository: str = REPOSITORY):
    """Return assets of the latest GitHub release or an empty list."""
    resp = requests.get(f"https://api.github.com/repos/{repository}/releases", timeout=10)
    resp.raise_for_status()
    releases = resp.json()
    if not releases:
        print("Keine Releases gefunden.")
        return []
    last_release = releases[0]
    return last_release.get("assets", [])


def _download_asset(assets, asset_name: str, dest_path: str) -> bool:
    for asset in assets:
        if asset.get("name") == asset_name:
            url = asset.get("browser_download_url")
            if not url:
                continue
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            with open(dest_path, "wb") as f:
                f.write(r.content)
            print(f"{asset_name} wurde heruntergeladen.")
            return True
    return False


def download_dealer_config(dest_path: str = DEALER_CONFIG_FILE) -> bool:
    """Download the combined dealers_config.json file."""
    assets = fetch_github_release_assets()
    ok = _download_asset(assets, DEALER_CONFIG_FILE, dest_path)
    if not ok:
        print("Fehler: dealers_config.json nicht in den Release-Assets gefunden.")
    return ok


def load_dealer_config(file_path: str = DEALER_CONFIG_FILE):
    """Load and parse dealers_config.json."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if not isinstance(data, dict):
        raise ValueError("dealers_config.json sollte ein Dictionary sein")
    if "dealers" not in data or not isinstance(data["dealers"], list):
        raise ValueError("dealers_config.json sollte ein 'dealers'-Array enthalten")
    return data


def read_dealer_lock(lock_path: str = DEALER_LOCK_FILE):
    """Read saved dealer_id from lock file."""
    if not os.path.exists(lock_path):
        return None
    with open(lock_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def write_dealer_lock(dealer_id: str, lock_path: str = DEALER_LOCK_FILE):
    """Save dealer_id to lock file."""
    with open(lock_path, "w", encoding="utf-8") as f:
        f.write(dealer_id)


def find_dealer_config(dealer_id: str, config_data):
    """Find dealer config by dealer_id from loaded config data."""
    for dc in config_data["dealers"]:
        if dc.get("dealer_id") == dealer_id:
            return dc
    return None


def _dealer_label(dealer_config) -> str:
    """Create a display label for a dealer."""
    dealer_id = dealer_config.get("dealer_id", "Unbekannt")
    dealer_info = dealer_config.get("dealer", {})
    if isinstance(dealer_info, dict):
        name = dealer_info.get("name", "Unbekannt")
        city = None
        address = dealer_info.get("address")
        if isinstance(address, dict):
            city = address.get("city")
        suffix = f" – {city}" if city else ""
        return f"{name} (ID: {dealer_id}){suffix}"
    return f"{dealer_id}"


def select_dealer(config_data):
    """Interactively select a dealer from config data."""
    dealers = config_data["dealers"]
    choices = [_dealer_label(d) for d in dealers]
    selected_config = None

    if questionary:
        answer = questionary.autocomplete(
            "Händler wählen (Tippen zum Suchen):",
            choices=choices,
            validate=lambda val: val in choices or "Bitte einen Eintrag wählen",
            match_middle=True,
        ).ask()
        if answer is None:
            print("Auswahl abgebrochen.")
            sys.exit(1)
        selected_config = dealers[choices.index(answer)]
    else:
        print("Bitte wählen Sie Ihren Händler aus der Liste (kein TUI-Modus, questionary nicht installiert):")
        for index, label in enumerate(choices):
            print(f"{index + 1}. {label}")
        try:
            selection = int(input("Geben Sie die Nummer Ihres Händlers ein: ")) - 1
        except ValueError:
            print("Ungültige Eingabe.")
            sys.exit(1)
        if selection < 0 or selection >= len(dealers):
            print("Ungültige Auswahl.")
            sys.exit(1)
        selected_config = dealers[selection]

    dealer_id = selected_config.get("dealer_id", "")
    dealer_info = selected_config.get("dealer", {})
    name = dealer_info.get("name", "Unbekannt") if isinstance(dealer_info, dict) else "Unbekannt"
    return dealer_id, name


def ensure_dealer_config(no_download: bool, dest_path: str = DEALER_CONFIG_FILE) -> bool:
    """Ensure dealers_config.json exists, download if needed."""
    if os.path.exists(dest_path):
        return True
    if no_download:
        print(f"Fehler: {dest_path} fehlt und --no-download ist aktiv.")
        return False
    return download_dealer_config(dest_path)
