from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from urllib.parse import urlparse
import re

options = Options()
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
driver = webdriver.Chrome(options=options,service=ChromeService(ChromeDriverManager().install()))

driver.get("https://www.volkswagen.de/de/modelle/verfuegbare-fahrzeuge.html")
iframe = driver.find_element(By.ID, "schnellsuche")
ActionChains(driver)\
    .scroll_to_element(iframe)\
    .perform()

time.sleep(10)
logs = driver.get_log("performance")
requests = [json.loads(lr["message"])["message"] for lr in logs]


file = open("requests.json", "w")
json.dump(requests, file, indent=4)


for entry in requests:
    if entry.get("method") == "Network.requestWillBeSent":
        params = entry.get("params", {})
        initiator = params.get("initiator", {})
        request = params.get("request", {})
            
        # Identifikation durch Initiator-Stack, falls vorhanden
        if initiator.get("type") == "script" and "stack" in initiator:
            if ".feature-app.io/bff/" in request.get("url"):
                domain = urlparse(request.get("url")).hostname
                print(domain)
                break

print(f"Folgende Domain gefunden: {domain}")
extracted_domain = domain

# HTML-Dateien aktualisieren
def update_html_file(file_path, pattern, replacement):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    updated_content = re.sub(pattern, replacement, content)
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_content)
    print(f"Datei {file_path} wurde aktualisiert.")

# Ersetze die Domain in den HTML-Dateien
update_html_file("showCars.html", r"https://v\d+-\d+-\d+\.gsl\.feature-app\.io", f"https://{extracted_domain}")
update_html_file("index.html", r"https://prod-ds\.dcc\.feature-app\.io", f"https://{extracted_domain}")
