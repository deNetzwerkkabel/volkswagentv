import requests
import re
import os

def check_url(url):
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def update_file(file_path, pattern, replacement):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    updated_content = re.sub(pattern, replacement, content)
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_content)
    print(f"Updated URLs in {file_path}")

def process_files():
    files_to_check = [
        "showCars.html",
        "index.html",
        "css/style.css"
    ]
    url_patterns = [
        (r"https://cdn.jsdelivr.net/.*", "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"),
        (r"https://www.volkswagen.de/.*", "https://www.volkswagen.de")
    ]

    for file_name in files_to_check:
        file_path = os.path.join(file_name)
        for pattern, replacement in url_patterns:
            if not check_url(replacement):
                print(f"URL {replacement} is not reachable.")
            else:
                update_file(file_path, pattern, replacement)

if __name__ == "__main__":
    process_files()
