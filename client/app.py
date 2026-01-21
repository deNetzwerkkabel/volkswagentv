import sys
import requests
import json
import os
from pathlib import Path
from urllib.parse import urlparse
from html_generator import createHTMLPagesForCars as generateHTML
from dealer_utils import (
    DEALER_LIST_FILE,
    read_dealer_lock,
    write_dealer_lock,
    load_dealer_list,
    select_dealer,
    ensure_dealer_list,
    ensure_dealer_config,
)

DEALER_LIST_FILE = "dealers.json"
HTML_PRESET_FILE = "vorlage.html"
OUTPUT_DIR = "data"

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

def loadData(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def fetchAndProcessCars(config_path):
    data = loadData(config_path)
    car_api_url = data['base_data']['car_api_url']
    dealer_id = data['base_data']['dealer_id']
    print(f"Starte Fetching der Autos für Händler ID: {dealer_id}...")
    cars = fetchCarsByDealerId(dealer_id, car_api_url)
    data['cars'] = cars
    for car in data['cars']:
        title = car['title']
        subtitle = car['subtitle']['value']
        price = car['prices']['sale']['value'] + " " + car['prices']['sale']['symbol']
        motor = car['motor']['fuel']['value'] + " (" + car['motor']['powerPs']['value'] + " " + car['motor']['powerPs']['unit'] + ")"
        modelYear = car['modelyear']['value']
        gear = car['gear']['value']
        mileage = car['mileage']['value'] + " km"
        stockLink = car['stockLinks']['vwdeb']['value']
        images = []
        for img in car['images']:
            images.append(img['href'])
        print(f"Gefundenes Auto: {title} - {subtitle} - {price} - {motor} - {modelYear} - {gear} - {mileage}")
    with open("cars.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Autos für Händler ID: {dealer_id} wurden in cars.json gespeichert.")
    
    # Generate HTML pages using the html_generator module
    generateHTML(data)

if __name__ == "__main__":
    no_download = "--no-download" in sys.argv

    dealer_id = read_dealer_lock()
    if dealer_id:
        print(f"Händlerkonfiguration gefunden: Händler ID {dealer_id}")
    else:
        if not ensure_dealer_list(no_download, DEALER_LIST_FILE):
            sys.exit(1)
        try:
            dealers = load_dealer_list(DEALER_LIST_FILE)
        except Exception as exc:  # minimal surface
            print(f"Fehler beim Laden der Händlerliste: {exc}")
            sys.exit(1)
        dealer_id, dealer_name = select_dealer(dealers)
        write_dealer_lock(dealer_id)
        print(f"Händler {dealer_name} mit ID {dealer_id} wurde ausgewählt und gespeichert.")

    config_path = f"{dealer_id}.json"
    if not ensure_dealer_config(dealer_id, no_download, config_path):
        sys.exit(1)

    fetchAndProcessCars(config_path)
    