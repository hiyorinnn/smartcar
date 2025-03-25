// Global variables
let map;
let carMarkers = [];
// Initialize the map
function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    center: { lat: 1.3521, lng: 103.8198 },
    zoom: 12,
    mapId: 'f24fbfecd1ca2bd'
  });

  // Initial data fetch
  fetchCarData();
}

// Fetch car data from the microservice
function fetchCarData() {
  fetch('http://localhost:5000/car/available')
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(carData => {
      displayCarsOnMap(carData.data.cars);
    })
    .catch(error => {
      console.error('Error fetching car data:', error);
    });
}

// Display cars on the map
function displayCarsOnMap(cars) {
  // Clear existing markers
  carMarkers.forEach(marker => marker.map = null);
  carMarkers = [];
  
  // Add markers for cars
  cars.forEach(car => {
    // Create marker
    const marker = new google.maps.marker.AdvancedMarkerElement({
      position: { lat: parseFloat(car.latitude), lng: parseFloat(car.longitude) },
      map: map,
      title: `${car.make} ${car.model}`,
      content: createMarkerContent(car)
    });

    // Create info window
    const infoWindow = new google.maps.InfoWindow({
      content: createInfoWindowContent(car)
    });

    // Add click event
    marker.addEventListener('gmp-click', () => {
      infoWindow.open(map, marker);
    });

    // Add marker to the array
    carMarkers.push(marker);
  });
}

// Create the marker content element
function createMarkerContent(car) {
  const markerElement = document.createElement('div');
  markerElement.className = 'car-marker';
  markerElement.style.backgroundColor = car.available ? 'green' : 'red';
  markerElement.style.color = 'white';
  markerElement.style.padding = '5px';
  markerElement.style.borderRadius = '50%';
  markerElement.textContent = car.make.substring(0, 1) + car.model.substring(0, 1);
  return markerElement;
}

// Create info window content
function createInfoWindowContent(car) {
  return `
    <div>
      <strong>${car.make} ${car.model}</strong><br>
      Price: $${car.price_per_hour}/hour<br>
      Availability: ${car.available ? 'Available' : 'Unavailable'}<br>
      Year: ${car.year}
    </div>
  `;
}
