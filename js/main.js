document.addEventListener("DOMContentLoaded", function () {
    let cars = [];
    let currentCarIndex = 0;
    const dealerId = 'DEU38628'; // Beispiel-ID

    const loadCars = async (dealerId) => {
        try {
            const initialRequest = await downloadCars(1, dealerId);
            if (initialRequest && initialRequest.cars && initialRequest.meta) {
                cars = initialRequest.cars;
                const pageMax = initialRequest.meta.pageMax;
                for (let i = 2; i <= pageMax; i++) {
                    const result = await downloadCars(i, dealerId);
                    if (result && result.cars) {
                        cars = cars.concat(result.cars);
                    }
                }
                if (cars.length > 0) {
                    currentCarIndex = 0;
                    console.log(cars[0]);
                    displayCar(cars[0]);
                } else {
                    document.getElementById('loading').textContent = 'Keine Autos gefunden';
                }
            }
        } catch (error) {
            console.error('Error fetching data:', error);
            document.getElementById('loading').textContent = 'Fehler beim Laden der Daten';
        }
    };

    const downloadCars = async (page, dealerId) => {
        try {
            const response = await fetch(`http://v3-66-1.gsl.feature-app.io/bff/car/search?t_partner=${dealerId}&sort=DATE_OFFER&sortdirection=ASC&pageitems=12&page=${page}&market=passenger&country=DE&language=de&oneapiKey=nOqkwPxxu8ViK9aaHvTkglzVZAlX4yIx&endpoint=%7B%22endpoint%22%3A%7B%22type%22%3A%22publish%22%2C%22country%22%3A%22de%22%2C%22language%22%3A%22de%22%2C%22content%22%3A%22onehub_pkw%22%2C%22envName%22%3A%22prod%22%2C%22testScenarioId%22%3Anull%2C%22isCloud%22%3Atrue%7D%2C%22signature%22%3A%22DDI5cVcqgXftyNeQrMuw%2Fbb9jUj%2BZrWtTRzYnLVkHzY%3D%22%7D&dataVersion=2A7706719FE556C689F695D1B263339A`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching data:', error);
            return null;
        }
    };

    const displayCar = (car) => {
        for (let i in car) {
            console.log(i + ": " + car[i]);
        }
        document.getElementById('carTypeLabel').textContent = car.carTypeLabel || '';
        document.getElementById('title').textContent = car.model?.value || '';
        document.getElementById('subtitle').textContent = car.localCarTitle?.value || '';

        const carousel = document.getElementById('carousel');
        carousel.innerHTML = '';
        let l = "active";
        car.images?.forEach(img => {
            const div = document.createElement('div');
            div.className = `carousel-item ${l} rounded-3`;
            const imgElement = document.createElement('img');
            imgElement.src = img.href;
            imgElement.className = 'd-block w-100';
            div.appendChild(imgElement);
            carousel.appendChild(div);
            l = "";
        });

        document.getElementById('price').innerHTML = `${car.parsedPrice?.label} <span class="priceDetails">${car.parsedPrice?.suffix?.label}</span>`;
        document.getElementById('motor').textContent = `${car.motor?.fuel?.value} | ${car.motor?.powerPs?.value} PS`;
        document.getElementById('modelYear').textContent = car.modelyear?.value || '';
        document.getElementById('gear').textContent = car.gear?.value || '';
        document.getElementById('mileage').textContent = `${car.mileage?.value} km`;
        document.getElementById('dealerLabel').textContent = car.contactData?.dealerLabel || '';
        document.getElementById('dealerStreet').textContent = car.contactData?.dealerStreet || '';
        document.getElementById('dealerAddress').textContent = car.contactData?.dealerAddress || '';
        document.getElementById('qrCode').src = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://www.volkswagen.de/de/modelle/verfuegbare-fahrzeuge-suche.html/__app/search/car/${car.key}.app`;
        document.getElementById('loading').style.display = 'none';
        document.getElementById('carContainer').style.display = 'block';
    };

    const nextCar = () => {
        currentCarIndex = (currentCarIndex + 1) % cars.length;
        displayCar(cars[currentCarIndex]);
    };

    loadCars(dealerId);

    setInterval(nextCar, 120000); // Change car every 2 minutes
});
