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

def buildBaseData(dealer_api_url, car_api_url, dealer, dealer_id=None):
    now = datetime.datetime.now()
    return {
        "base_data": {
            "version": now.strftime("%Y.%m.%d"),
            "dealer_api_url": dealer_api_url,
            "car_api_url": car_api_url,
            "fetched_at": now.isoformat(),
            "dealer_id": dealer_id if dealer_id is not None else dealer['id'],
        },
        "dealer": dealer
    }

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

    for dealer in dealer_data['dealers']:
        if checkDealerId(dealer['id']) == False:
            print(f"Händler ID: {dealer['id']} ist ungültig, überspringe...")
            continue
        dealer_id = dealer['address']['countryCode'] + dealer['id']
        base_data = buildBaseData(dealer_api_url, car_api_url, dealer, dealer_id)
        with open(f"{dealer_id}.json", "w", encoding="utf-8") as f:
            json.dump(base_data, f, ensure_ascii=False, indent=4)
        print(f"Autos für Händler ID: {dealer_id} wurden in {dealer_id}.json gespeichert.")