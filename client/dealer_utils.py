import json
import os
import sys
import requests
try:
    import questionary
except ImportError:  # optional dependency
    questionary = None

REPOSITORY = "denetzwerkkabel/volkswagentv"
DEALER_LIST_FILE = "dealers.json"
DEALER_LOCK_FILE = "dealer.lock"


def fetch_github_release_assets(repository: str = REPOSITORY):
    """Return assets of the latest GitHub release or an empty list."""
    resp = requests.get(f"https://api.github.com/repos/{repository}/releases", timeout=10)
    resp.raise_for_status()
    releases = resp.json()
    if not releases:
        print("Keine Releases gefunden.")
        return []
    last_release = releases[0]  # GitHub returns newest first
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


def download_dealer_list(dest_path: str = DEALER_LIST_FILE) -> bool:
    assets = fetch_github_release_assets()
    ok = _download_asset(assets, DEALER_LIST_FILE, dest_path)
    if not ok:
        print("Fehler: dealers.json nicht in den Release-Assets gefunden.")
    return ok


def download_dealer_config(dealer_id: str, dest_path: str) -> bool:
    assets = fetch_github_release_assets()
    asset_name = f"{dealer_id}.json"
    ok = _download_asset(assets, asset_name, dest_path)
    if not ok:
        print(f"Fehler: {asset_name} nicht in den Release-Assets gefunden.")
    return ok


def load_dealer_list(file_path: str = DEALER_LIST_FILE):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("dealers"), list):
        return data["dealers"]
    raise ValueError(f"Unerwartete Struktur in {file_path}")


def read_dealer_lock(lock_path: str = DEALER_LOCK_FILE):
    if not os.path.exists(lock_path):
        return None
    with open(lock_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def write_dealer_lock(dealer_id: str, lock_path: str = DEALER_LOCK_FILE):
    with open(lock_path, "w", encoding="utf-8") as f:
        f.write(dealer_id)


def _dealer_label(dealer) -> str:
    if isinstance(dealer, dict):
        name = dealer.get("name", "Unbekannt")
        dealer_id = dealer.get("id", "Unbekannt")
        city = None
        address = dealer.get("address")
        if isinstance(address, dict):
            city = address.get("city")
        suffix = f" – {city}" if city else ""
        return f"{name} (ID: {dealer_id}){suffix}"
    value = str(dealer)
    return f"{value} (ID: {value})"


def _dealer_identity(dealer):
    if isinstance(dealer, dict):
        address = dealer.get("address")
        country_code = address.get("countryCode", "") if isinstance(address, dict) else ""
        dealer_id = country_code + dealer.get("id", str(dealer))
        name = dealer.get("name", "Unbekannt")
        return dealer_id, name
    value = str(dealer)
    return value, value


def select_dealer(dealers):
    choices = [_dealer_label(d) for d in dealers]
    selected_dealer = None

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
        selected_dealer = dealers[choices.index(answer)]
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
        selected_dealer = dealers[selection]

    return _dealer_identity(selected_dealer)


def ensure_dealer_list(no_download: bool, dealer_list_path: str = DEALER_LIST_FILE):
    if os.path.exists(dealer_list_path):
        return True
    if no_download:
        print("Fehler: dealers.json fehlt und --no-download ist aktiv.")
        return False
    return download_dealer_list(dealer_list_path)


def ensure_dealer_config(dealer_id: str, no_download: bool, dest_path: str):
    if os.path.exists(dest_path):
        return True
    if no_download:
        print(f"Fehler: {dest_path} fehlt und --no-download ist aktiv.")
        return False
    return download_dealer_config(dealer_id, dest_path)
