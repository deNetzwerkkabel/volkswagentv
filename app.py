import requests
import json
import datetime

def fetchDealerApiUrl():
    req = requests.get("https://www.volkswagen.de/de.global-config.json")
    data = req.json()
    dealer_api_url = data['spaAsyncConfig']['featureHubModel']['featureAppsForFeatureAppService']['/content/vwa-ngw18-feature-apps/standalone-dealer-search']['baseUrl']
    car_api_url = data['spaAsyncConfig']['featureHubModel']['featureAppsForFeatureAppService']['/content/vwa-ngw18-feature-apps/gsl_quicksearch']['baseUrl']
    return dealer_api_url, car_api_url

def getDealerData(api_url):
    fetch_url = f"{api_url}/bff-search/dealers?serviceConfigEndpoint=%7B%22endpoint%22%3A%7B%22type%22%3A%22publish%22%2C%22country%22%3A%22de%22%2C%22language%22%3A%22de%22%2C%22content%22%3A%22onehub_pkw%22%2C%22envName%22%3A%22prod%22%2C%22testScenarioId%22%3Anull%7D%2C%22signature%22%3A%22eXxF3Vp4siIxU67pK2Vs14eGqdMbD0HzeFcn3b058j8%3D%22%7D&lufthansaApiKey=h0CQWvPYSBvp5KYXUpRU4FpZrnl0tZx1&query=%7B%22type%22%3A%22DEALER%22%2C%22language%22%3A%22de-DE%22%2C%22countryCode%22%3A%22DE%22%2C%22dealerServiceFilter%22%3A%5B%5D%2C%22usePrimaryTenant%22%3Atrue%2C%22name%22%3A%22+%22%7D"
    response = requests.get(fetch_url)
    return response.json()

def checkDealerId(id):
    if len(id) != 5:
        return False
    if not id.isnumeric():
        return False
    return True

if __name__ == "__main__":
    print("Starte Fetching der API-URL...")
    dealer_api_url, car_api_url = fetchDealerApiUrl()
    print(f"Gefundene API-URL: {dealer_api_url}")
    print("Starte Fetching der Händlerdaten...")
    dealer_data = getDealerData(dealer_api_url)
    with open("dealers.json", "w", encoding="utf-8") as f:
        json.dump(dealer_data, f, ensure_ascii=False, indent=4)
    print("Händlerdaten wurden in dealers.json gespeichert.")

    dealers_config = {
        "base_data": {
            "dealer_api_url": dealer_api_url,
            "car_api_url": car_api_url,
        },
        "dealers": []
    }

    for dealer in dealer_data['dealers']:
        if not checkDealerId(dealer['id']):
            print(f"Händler ID: {dealer['id']} ist ungültig, überspringe...")
            continue
        dealer_id = dealer['address']['countryCode'] + dealer['id']
        now = datetime.datetime.now()
        dealer_config = {
            "dealer_id": dealer_id,
            "version": now.strftime("%Y.%m.%d"),
            "fetched_at": now.isoformat(),
            "dealer": dealer
        }
        dealers_config["dealers"].append(dealer_config)
        print(f"Konfiguration für Händler ID: {dealer_id} hinzugefügt.")

    with open("dealers_config.json", "w", encoding="utf-8") as f:
        json.dump(dealers_config, f, ensure_ascii=False, indent=4)
    print(f"\n Fertig! Gesamtkonfiguration für {len(dealers_config['dealers'])} Händler wurde in dealers_config.json gespeichert.")
