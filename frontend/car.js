// Global variables
let map;
let carMarkers = [];
let directionsService;
let directionsRenderer;

document.addEventListener('DOMContentLoaded', function () {
  const userMessage = document.getElementById('user-message');
  const signInBtn = document.getElementById('signin-link');
  const signUpBtn = document.getElementById('register-link');
  const logOutBtn = document.getElementById('logout-link');

function isLoggedIn() {
  return localStorage.getItem('loggedIn');
}
//Updates Page when logged in or out
function updateUI() {
  if (isLoggedIn()) {
    userMessage.textContent = 'Welcome!';
    signInBtn.style.display = 'none';
    signUpBtn.style.display = 'none';
    logOutBtn.style.display = 'inline-block';
  } else {
    userMessage.textContent = '';
    signInBtn.style.display = 'inline-block';
    signUpBtn.style.display = 'inline-block';
    logOutBtn.style.display = 'none';
  }
}

signInBtn.addEventListener('click', () => {
  localStorage.setItem('loggedIn', 'true');
  updateUI();
});

signUpBtn.addEventListener('click', () => {
  localStorage.setItem('loggedIn', 'true');
  updateUI();
});

logOutBtn.addEventListener('click', () => {
  localStorage.removeItem('loggedIn');
  updateUI(); // Stays on same page, just updates view
});

updateUI();

});

// Initialize the map
window.initMap = function() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 1.3521, lng: 103.8198 },
    zoom: 12,
    mapId: "f24fbfecd1ca2bd",
  });

  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer({
    map: map,
    suppressMarkers: false,
    preserveViewport: false
  });
  // Get current location
  initializeLocationButton();

    // Initial data fetch
  fetchCarData();  
}

// Fetch car data from the microservice
function fetchCarData() {
  fetch("http://127.0.0.1:5001/get_cars_by_location")
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((carData) => {
      console.log("Car data received for google map markers:", carData);
      
      // Add defensive checks for the data structure
      if (!carData) {
        throw new Error("Car data is undefined");
      }
      if (!carData.cars) {
        throw new Error("Car data.cars is undefined");
      }
      
      displayCarsOnMap(carData.cars);
    })
    .catch((error) => {
      console.error("Error fetching car data:", error);
      // Display error message on the map
      const mapElement = document.getElementById("map");
      if (mapElement) {
        const errorDiv = document.createElement("div");
        errorDiv.className = "error-message";
        errorDiv.textContent = "Failed to load car data. Please try again later.";
        errorDiv.style.position = "absolute";
        errorDiv.style.top = "50%";
        errorDiv.style.left = "50%";
        errorDiv.style.transform = "translate(-50%, -50%)";
        errorDiv.style.backgroundColor = "rgba(255, 0, 0, 0.7)";
        errorDiv.style.color = "white";
        errorDiv.style.padding = "10px";
        errorDiv.style.borderRadius = "5px";
        mapElement.appendChild(errorDiv);
      }
    });
}

// Display cars on the map
function displayCarsOnMap(cars) {
  // Clear existing markers
  carMarkers.forEach((marker) => (marker.map = null));
  carMarkers = [];

  // Add markers for cars
  cars.forEach((car) => {
    // Create marker
    const marker = new google.maps.marker.AdvancedMarkerElement({
      position: {
        lat: parseFloat(car.latitude),
        lng: parseFloat(car.longitude),
      },
      map: map,
      title: `${car.make} ${car.model}`,
      content: createMarkerContent(car),
    });

    // Create info window
    const infoWindow = new google.maps.InfoWindow({
      content: createInfoWindowContent(car),
    });

    // Add click event
    marker.addEventListener("gmp-click", () => {
      console.log("Marker clicked:", car.make, car.model);
      infoWindow.open({
        map: map,
        anchor: marker
      });
      setTimeout(() => {
        const directionsButton = document.getElementById(`get-directions-${car.id}`);
        if (directionsButton) {
          directionsButton.addEventListener('click', () => {
            calculateAndDisplayRoute(marker.position);
          });
        }
      }, 300);
    });

    // Add marker to the array
    carMarkers.push(marker);
  });
}

// Create the marker content element - car-marker.svg
function createMarkerContent(car) {
  const markerElement = document.createElement("div");
  markerElement.className = 'car-marker';
  
  const img = document.createElement('img');
  img.setAttribute('src', './src/car-travel-svgrepo-com.svg');
  img.setAttribute('width', '20px');
  img.setAttribute('height', '20px');
  img.style.display = 'block';
  
  markerElement.appendChild(img);
  return markerElement;
}

// Create info window content
function createInfoWindowContent(car) {
  return `
    <div>
      <strong>${car.make} ${car.model}</strong><br>
      Price: $${car.price_per_hour}/hour<br>
      Color: ${car.color}<br>
      Year: ${car.year}
      <button id="get-directions-${car.id}" class="directions-btn">Get Directions</button>
    </div>
  `;
}

// To get current location of user 
function initializeLocationButton() {
  const currentLocationBtn = document.getElementById('current-location-btn');
  
  if (currentLocationBtn) {
    currentLocationBtn.addEventListener('click', () => {
      if (navigator.geolocation) {
        // Show loading state
        currentLocationBtn.textContent = 'Getting location...';
        currentLocationBtn.disabled = true;
        
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const pos = {
              lat: position.coords.latitude,
              lng: position.coords.longitude,
            };
            
            // Update hidden input fields
            document.getElementById('location-lat').value = pos.lat;
            document.getElementById('location-lng').value = pos.lng;
            
            // Use reverse geocoding to get address
            const geocoder = new google.maps.Geocoder();
            geocoder.geocode({ location: pos }, (results, status) => {
              if (status === "OK" && results[0]) {
                document.getElementById('location-input').value = results[0].formatted_address;
              } else {
                document.getElementById('location-input').value = `Lat: ${pos.lat.toFixed(4)}, Lng: ${pos.lng.toFixed(4)}`;
              }
              
              // Reset button
              currentLocationBtn.innerHTML = '<i class="fa fa-map-marker"></i> Current Location';
              currentLocationBtn.disabled = false;
              
              // Center map on user's location if map exists
              if (map) {
                map.setCenter(pos);
                map.setZoom(16);
              }
              
            });
          },
          (error) => {
            let errorMessage;
            switch(error.code) {
              case error.PERMISSION_DENIED:
                errorMessage = "User denied the request for geolocation.";
                break;
              case error.POSITION_UNAVAILABLE:
                errorMessage = "Location information is unavailable. Check your device settings and internet connection.";
                break;
              case error.TIMEOUT:
                errorMessage = "The request to get user location timed out.";
                break;
              default:
                errorMessage = "An unknown error occurred getting location.";
                break;
            }
            console.error("Geolocation error:", errorMessage);

            // console.error("Error getting location:", error);
            // alert("Unable to retrieve your location. Please check your browser settings.");
            
            // Reset button
            currentLocationBtn.innerHTML = '<i class="fa fa-map-marker"></i> Current Location';
            currentLocationBtn.disabled = false;
          },
          {
            enableHighAccuracy: true,
            timeout: 5000,
            maximumAge: 0
          }
        );
      } else {
        alert("Geolocation is not supported by this browser.");
      }
    });
  }
}

// Call this function after the page loads and Google Maps is initialized
document.addEventListener('DOMContentLoaded', function() {
  // Initialize the current location button
  initializeLocationButton();
});

// Calculate and display route to the selected marker
function calculateAndDisplayRoute(destination) {
  // Get user's current position or use a default starting point
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const origin = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };
        
        requestDirections(origin, destination);
      },
      (error) => {
        console.error("Error getting current location:", error);
        
        // Use default location when geolocation fails
        const defaultLocation = {
          lat: 1.29716, // Default location": 80 stamford road, scis1
          lng: 103.84903
        };
        
        console.log("Using default location:", defaultLocation);
        requestDirections(defaultLocation, destination);
      },
      {
        timeout: 10000,        // 10-second timeout
        maximumAge: 300000,    // Cache position for 5 minutes
        enableHighAccuracy: false // Don't need high accuracy for directions
      }
    );
  } else {
    // Browser doesn't support geolocation
    const defaultLocation = {
      lat: 1.29716, // Default location": 80 stamford road, scis1
      lng: 103.84903
    };
    
    console.log("Geolocation not supported. Using default location:", defaultLocation);
    requestDirections(defaultLocation, destination);
  }
}

// Extracted the directions request into a separate function for reusability
function requestDirections(origin, destination) {
  directionsService.route(
    {
      origin: origin,
      destination: destination,
      travelMode: google.maps.TravelMode.WALKING,
    },
    (response, status) => {
      if (status === "OK") {
        // Display the route on the map
        directionsRenderer.setDirections(response);
        
        // Optionally display additional info about the route
        const route = response.routes[0].legs[0];
        alert(`Distance: ${route.distance.text}\nEstimated time: ${route.duration.text}`);
      } else {
        window.alert("Directions request failed due to " + status);
      }
    }
  );
}
