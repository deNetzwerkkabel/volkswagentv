import sys
import requests
import json
from pathlib import Path
from html_generator import createHTMLPagesForCars as generateHTML
from dealer_utils import (
    DEALER_CONFIG_FILE,
    read_dealer_lock,
    write_dealer_lock,
    load_dealer_config,
    find_dealer_config,
    select_dealer,
    ensure_dealer_config,
)

def fetchCarsByDealerId(id, dealer_api_url):
    page = 1
    lastPage = 2
    all_cars = []
    while page < lastPage:
        url = fetchCarsByPage(dealer_api_url, id, page)
        response = requests.get(url)
        data = response.json()
        if 'cars' not in data:
            break
        all_cars.extend(data['cars'])
        lastPage = data['meta']['pageMax']
        page += 1
    return all_cars

def fetchCarsByPage(dealer_api_url, id, page):
    return f"{dealer_api_url}/bff/car/search?t_partner={id}&sort=DEFAULT&sortdirection=ASC&pageitems=12&page={page}&country=DE&endpoint=%7B%22endpoint%22%3A%7B%22type%22%3A%22publish%22%2C%22country%22%3A%22de%22%2C%22language%22%3A%22de%22%2C%22content%22%3A%22onehub_pkw%22%2C%22envName%22%3A%22prod%22%2C%22testScenarioId%22%3Anull%7D%2C%22signature%22%3A%22eXxF3Vp4siIxU67pK2Vs14eGqdMbD0HzeFcn3b058j8%3D%22%7D&language=de&market=passenger&oneapiKey=nOqkwPxxu8ViK9aaHvTkglzVZAlX4yIx"

def fetchAndProcessCars(dealer_config, global_base_data):
    """Fetch cars and generate HTML pages for a selected dealer."""
    dealer_id = dealer_config['dealer_id']
    dealer_info = dealer_config['dealer']
    
    car_api_url = global_base_data['car_api_url']
    
    print(f"Starte Fetching der Autos für Händler ID: {dealer_id}...")
    cars = fetchCarsByDealerId(dealer_id, car_api_url)
    
    # Build data structure for HTML generation
    data = {
        'base_data': {
            'dealer_id': dealer_id,
            'car_api_url': car_api_url,
            'dealer_api_url': global_base_data['dealer_api_url'],
            'version': dealer_config.get('version', ''),
            'fetched_at': dealer_config.get('fetched_at', ''),
        },
        'dealer': dealer_info,
        'cars': cars
    }
    
    for car in data['cars']:
        title = car.get('title', '')
        subtitle = car.get('subtitle', {}).get('value', '')
        price = (car.get('prices', {}).get('sale', {}).get('value', '') + " " + 
                car.get('prices', {}).get('sale', {}).get('symbol', ''))
        motor_data = car.get('motor', {})
        motor = (motor_data.get('fuel', {}).get('value', '') + " (" + 
                motor_data.get('powerPs', {}).get('value', '') + " " + 
                motor_data.get('powerPs', {}).get('unit', '') + ")")
        modelYear = car.get('modelyear', {}).get('value', '')
        gear = car.get('gear', {}).get('value', '')
        mileage = car.get('mileage', {}).get('value', '') + " km"
        print(f"Gefundenes Auto: {title} - {subtitle} - {price} - {motor} - {modelYear} - {gear} - {mileage}")
    
    with open("cars.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Autos für Händler ID: {dealer_id} wurden in cars.json gespeichert.")
    
    # Generate HTML pages
    generateHTML(data)

if __name__ == "__main__":
    no_download = "--no-download" in sys.argv

    # Load or download dealers_config.json
    if not ensure_dealer_config(no_download, DEALER_CONFIG_FILE):
        sys.exit(1)

    try:
        config_data = load_dealer_config(DEALER_CONFIG_FILE)
    except Exception as exc:
        print(f"Fehler beim Laden der Konfiguration: {exc}")
        sys.exit(1)

    # Get global base data (APIs)
    global_base_data = config_data['base_data']

    # Check for existing dealer selection
    dealer_id = read_dealer_lock()
    if dealer_id:
        print(f"Händlerkonfiguration gefunden: Händler ID {dealer_id}")
        dealer_config = find_dealer_config(dealer_id, config_data)
        if not dealer_config:
            print(f"Fehler: Konfiguration für Händler ID {dealer_id} nicht gefunden.")
            sys.exit(1)
    else:
        # Let user select a dealer
        dealer_id, dealer_name = select_dealer(config_data)
        write_dealer_lock(dealer_id)
        print(f"Händler {dealer_name} mit ID {dealer_id} wurde ausgewählt und gespeichert.")
        dealer_config = find_dealer_config(dealer_id, config_data)

    # Fetch cars and generate HTML
    fetchAndProcessCars(dealer_config, global_base_data)
