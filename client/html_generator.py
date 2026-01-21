import requests
import json
from pathlib import Path
import qrcode

OUTPUT_DIR = "data"
HTML_PRESET_FILE = "vorlage.html"

def downloadImage(url, save_path):
    """Download an image from URL and save it locally"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Fehler beim Herunterladen von {url}: {e}")
        return False

def generateQRCode(url, save_path):
    """Generate QR code for given URL and save it locally"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(save_path)
        return True
    except Exception as e:
        print(f"Fehler beim Generieren des QR-Codes: {e}")
        return False

def generateHTMLForCar(car, dealer_info, car_index, data_dir):
    """Generate HTML file for a single car"""
    # Read template
    with open(HTML_PRESET_FILE, "r", encoding="utf-8") as f:
        template = f.read()
    
    # Extract car data
    title = car.get('title', '')
    subtitle = car['subtitle']['value'] if 'subtitle' in car and 'value' in car['subtitle'] else ''
    price = car['prices']['sale']['value'] + " " + car['prices']['sale']['symbol'] if 'prices' in car else ''
    motor = car['motor']['fuel']['value'] + " (" + car['motor']['powerPs']['value'] + " " + car['motor']['powerPs']['unit'] + ")" if 'motor' in car else ''
    modelYear = car['modelyear']['value'] if 'modelyear' in car and 'value' in car['modelyear'] else ''
    gear = car['gear']['value'] if 'gear' in car and 'value' in car['gear'] else ''
    mileage = car['mileage']['value'] + " km" if 'mileage' in car and 'value' in car['mileage'] else ''
    
    # Dealer information
    dealerLabel = dealer_info['name'] if 'name' in dealer_info else ''
    dealerStreet = dealer_info['address']['street'] if 'address' in dealer_info and 'street' in dealer_info['address'] else ''
    dealerAddress = f"{dealer_info['address']['postalCode']} {dealer_info['address']['city']}" if 'address' in dealer_info else ''
    
    # Download images and create carousel items
    car_images_dir = data_dir / f"car_{car_index}_images"
    car_images_dir.mkdir(exist_ok=True)
    
    carousel_items = []
    if 'images' in car:
        for img_index, img in enumerate(car['images']):
            img_url = img['href']
            img_filename = f"image_{img_index}.jpg"
            img_path = car_images_dir / img_filename
            
            if downloadImage(img_url, img_path):
                active_class = "active" if img_index == 0 else ""
                carousel_items.append(
                    f'<div class="carousel-item {active_class} rounded-3"><img src="car_{car_index}_images/{img_filename}" class="d-block w-100"></div>'
                )
    
    carousel_html = "\n".join(carousel_items)
    
    # Generate QR code
    qr_code_path = ""
    if 'stockLinks' in car and 'vwdeb' in car['stockLinks'] and 'value' in car['stockLinks']['vwdeb']:
        stock_url = car['stockLinks']['vwdeb']['value']
        qr_filename = f"qr_code.png"
        qr_path = car_images_dir / qr_filename
        if generateQRCode(stock_url, qr_path):
            qr_code_path = f"car_{car_index}_images/{qr_filename}"
            print(f"QR-Code generiert für: {stock_url}")
    
    # Replace template variables
    html = template.replace('${title}', title)
    html = html.replace('${subtitle}', subtitle)
    html = html.replace('${price}', price)
    html = html.replace('${motor}', motor)
    html = html.replace('${modelYear}', modelYear)
    html = html.replace('${gear}', gear)
    html = html.replace('${mileage}', mileage)
    html = html.replace('${dealerLabel}', dealerLabel)
    html = html.replace('${dealerStreet}', dealerStreet)
    html = html.replace('${dealerAddress}', dealerAddress)
    html = html.replace('src=""', f'src="{qr_code_path}"')
    
    # Replace carousel items
    html = html.replace(
        '<div class="carousel-item ${activeClass} rounded-3"><img src="${img.href}" class="d-block w-100"></div>',
        carousel_html
    )
    
    # Save HTML file
    html_filename = data_dir / f"car_{car_index}.html"
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML-Seite erstellt: {html_filename}")
    return html_filename

def createHTMLPagesForCars(data):
    """Create HTML pages for all cars in the data"""
    # Create data directory
    data_dir = Path(OUTPUT_DIR)
    data_dir.mkdir(exist_ok=True)
    print(f"\nErstelle HTML-Seiten im Verzeichnis '{OUTPUT_DIR}/'...")
    
    # Get dealer information
    dealer_info = data.get('dealer', {})
    
    # Generate HTML for each car
    for index, car in enumerate(data['cars']):
        print(f"\nVerarbeite Auto {index + 1}/{len(data['cars'])}...")
        generateHTMLForCar(car, dealer_info, index, data_dir)
    
    print(f"\n✓ Fertig! {len(data['cars'])} HTML-Seiten wurden im Verzeichnis '{OUTPUT_DIR}/' erstellt.")
