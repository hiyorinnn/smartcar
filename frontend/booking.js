// Global variables to store selected car and user details
let selectedCar = null;
let map;
let carMarkers = [];
let directionsService;
let directionsRenderer;

// Initialize the map specifically for the booking page
window.initMap = function() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 1.3521, lng: 103.8198 }, // Default to Singapore
    zoom: 12,
    mapId: "f24fbfecd1ca2bd",
  });
  
  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer({
    map: map,
    suppressMarkers: false,
    preserveViewport: false
  });
  
  // Check for saved location coordinates
  const savedLat = sessionStorage.getItem('selectedLocationLat');
  const savedLng = sessionStorage.getItem('selectedLocationLng');
  
  if (savedLat && savedLng) {
    const savedPosition = {
      lat: parseFloat(savedLat),
      lng: parseFloat(savedLng)
    };
    
    // Center map on saved location
    map.setCenter(savedPosition);
    map.setZoom(14);
    
    // Add a marker for the user's location
    new google.maps.marker.AdvancedMarkerElement({
      position: savedPosition,
      map: map,
      title: "Your Location",
      content: createUserLocationMarker(),
    });
  }
  
  // Fetch cars based on location
  fetchNearbyCars();
}

// Create a distinctive marker for user's location
function createUserLocationMarker() {
  const markerElement = document.createElement("div");
  markerElement.className = 'user-location-marker';
  
  const dot = document.createElement('div');
  dot.style.width = '16px';
  dot.style.height = '16px';
  dot.style.backgroundColor = '#4285F4';
  dot.style.border = '2px solid white';
  dot.style.borderRadius = '50%';
  dot.style.boxShadow = '0 0 5px rgba(0,0,0,0.3)';
  
  markerElement.appendChild(dot);
  return markerElement;
}

// Fetch cars based on user's saved location
async function fetchNearbyCars() {
  try {
    const carsContainer = document.getElementById('cars-container');
    carsContainer.innerHTML = '<p>Loading available cars...</p>';
    
    // Retrieve saved location from session storage
    const savedLocation = sessionStorage.getItem('selectedLocation');
    
    // Display the location that was searched
    if (savedLocation) {
      // Create location display if it doesn't exist
      if (!document.getElementById('selected-location')) {
        const locationDisplay = document.createElement('div');
        locationDisplay.id = 'selected-location';
        locationDisplay.className = 'location-display';
        carsContainer.parentNode.insertBefore(locationDisplay, carsContainer);
      }
      
      const locationDisplay = document.getElementById('selected-location');
      locationDisplay.textContent = `Cars available near: ${savedLocation}`;
    }
    
    // Determine which API endpoint to use
    let apiUrl = 'http://127.0.0.1:5001/get_cars_by_location';
    if (savedLocation) {
      apiUrl = `http://127.0.0.1:5001/get_cars_by_location/${encodeURIComponent(savedLocation)}`;
    }
    
    const response = await axios.get(apiUrl);
    console.log('Fetched cars:', response.data);
    
    // Display cars on map and in list
    const availableCars = response.data.cars;
    
    // Clear loading message
    carsContainer.innerHTML = '';
    
    if (availableCars.length === 0) {
      carsContainer.innerHTML = '<p>No cars available at this location.</p>';
      return;
    }
    
    // Add cars to the list and map
    displayCarsOnMap(availableCars);
    displayCarsList(availableCars, carsContainer);
    
  } catch (error) {
    console.error('Error fetching cars:', error);
    const carsContainer = document.getElementById('cars-container');
    carsContainer.innerHTML = '<p>Error loading cars. Please try again later.</p>';
  }
}

// Display cars in the list view
function displayCarsList(cars, container) {
  cars.forEach(car => {
    const carCard = document.createElement('div');
    carCard.className = 'car-card';
    carCard.innerHTML = `
      <h3>${car.make} ${car.model}</h3>
      <p>Year: ${car.year}</p>
      <p>Color: ${car.color}</p>
      <p>Price: $${car.price_per_hour}/hour</p>
      <p>Distance: ${car.distance ? car.distance.toFixed(2) + ' km' : 'Unknown'}</p>
    `;
    carCard.addEventListener('click', () => selectCar(car, carCard));
    container.appendChild(carCard);
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
      // Close any open info windows
      carMarkers.forEach(m => {
        if (m.infoWindow && m.infoWindow.getMap()) {
          m.infoWindow.close();
        }
      });
      
      infoWindow.open({
        map: map,
        anchor: marker
      });
      
      // Store reference to the open info window
      marker.infoWindow = infoWindow;
      
      // Select the car in the list
      selectCarById(car.id);
      
      // Add event listener for directions button
      setTimeout(() => {
        const directionsButton = document.getElementById(`get-directions-${car.id}`);
        if (directionsButton) {
          directionsButton.addEventListener('click', () => {
            calculateAndDisplayRoute(marker.position);
          });
        }
        
        // Add event listener for booking button
        const bookButton = document.getElementById(`book-car-${car.id}`);
        if (bookButton) {
          bookButton.addEventListener('click', () => {
            selectCarById(car.id);
            // Scroll to booking form
            document.getElementById('booking-form').scrollIntoView({ behavior: 'smooth' });
          });
        }
      }, 300);
    });
    
    // Add marker to the array
    carMarkers.push(marker);
  });
}

// Select a car from the map by ID
function selectCarById(carId) {
  const carsContainer = document.getElementById('cars-container');
  const carCards = carsContainer.querySelectorAll('.car-card');
  
  // Find the car in the available cars data
  axios.get('http://127.0.0.1:5001/get_cars_by_location')
    .then(response => {
      const car = response.data.cars.find(c => c.id === carId);
      if (car) {
        // Find the corresponding card
        carCards.forEach((card, index) => {
          if (card.querySelector('h3').textContent === `${car.make} ${car.model}`) {
            selectCar(car, card);
          }
        });
      }
    })
    .catch(error => console.error('Error fetching car details:', error));
}

// Create the marker content element
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

// Create info window content with booking button
function createInfoWindowContent(car) {
  return `
    <div class="info-window">
      <strong>${car.make} ${car.model}</strong><br>
      Price: $${car.price_per_hour}/hour<br>
      Color: ${car.color}<br>
      Year: ${car.year}<br>
      <div class="info-window-buttons">
        <button id="get-directions-${car.id}" class="directions-btn">Get Directions</button>
        <button id="book-car-${car.id}" class="book-btn">Book This Car</button>
      </div>
    </div>
  `;
}

// Select a car from the list
function selectCar(car, cardElement) {
  // Remove selected class from all car cards
  document.querySelectorAll('.car-card').forEach(card => {
    card.classList.remove('selected');
  });
  
  // Add selected class to clicked card
  cardElement.classList.add('selected');
  
  // Set the selected car
  selectedCar = car;
  document.getElementById('selected-car').value = `${car.make} ${car.model} (${car.id})`;
  
  // Highlight the corresponding marker on the map
  carMarkers.forEach(marker => {
    if (marker.title === `${car.make} ${car.model}`) {
      map.panTo(marker.position);
      map.setZoom(15);
      
      // Trigger marker click to show info window
      google.maps.event.trigger(marker, 'click');
    }
  });
}

// Calculate and display route to the selected marker
function calculateAndDisplayRoute(destination) {
  // Get saved location or use a default starting point
  const savedLat = sessionStorage.getItem('selectedLocationLat');
  const savedLng = sessionStorage.getItem('selectedLocationLng');
  
  let origin;
  
  if (savedLat && savedLng) {
    origin = {
      lat: parseFloat(savedLat),
      lng: parseFloat(savedLng)
    };
    requestDirections(origin, destination);
  } else if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        origin = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };
        requestDirections(origin, destination);
      },
      (error) => {
        console.error("Error getting current location:", error);
        
        // Use default location when geolocation fails
        const defaultLocation = {
          lat: 1.29716,
          lng: 103.84903
        };
        
        requestDirections(defaultLocation, destination);
      }
    );
  } else {
    // Browser doesn't support geolocation
    const defaultLocation = {
      lat: 1.29716,
      lng: 103.84903
    };
    
    requestDirections(defaultLocation, destination);
  }
}

// Request directions between two points
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
        
        // Display additional info about the route
        const route = response.routes[0].legs[0];
        
        // Create a nicer notification instead of an alert
        const notification = document.createElement('div');
        notification.className = 'route-notification';
        notification.innerHTML = `
          <div class="notification-content">
            <h4>Route Information</h4>
            <p>Distance: ${route.distance.text}</p>
            <p>Estimated time: ${route.duration.text}</p>
            <button class="close-btn">Close</button>
          </div>
        `;
        
        document.body.appendChild(notification);
        
        // Add style for the notification
        const style = document.createElement('style');
        style.textContent = `
          .route-notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            padding: 15px;
            z-index: 1000;
            max-width: 300px;
          }
          .notification-content h4 {
            margin-top: 0;
            color: #333;
          }
          .close-btn {
            background: #f44336;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            float: right;
          }
        `;
        document.head.appendChild(style);
        
        // Add close button functionality
        notification.querySelector('.close-btn').addEventListener('click', () => {
          document.body.removeChild(notification);
        });
        
        // Auto-close after 10 seconds
        setTimeout(() => {
          if (document.body.contains(notification)) {
            document.body.removeChild(notification);
          }
        }, 10000);
      } else {
        window.alert("Directions request failed due to " + status);
      }
    }
  );
}

// Book the car
async function bookCar() {
  // Validate inputs
  const firstName = document.getElementById('first-name').value;
  const lastName = document.getElementById('last-name').value;
  const email = document.getElementById('email').value;
  const phone = document.getElementById('phone').value;
  const pickupDate = document.getElementById('pickup-date').value;
  const returnDate = document.getElementById('return-date').value;
  const paymentMethod = document.getElementById('payment-method').value;
  
  if (!selectedCar) {
    alert('Please select a car first');
    return;
  }
  
  // Ensure dates are in ISO format compatible with Python's fromisoformat()
  const formatISODate = (dateString) => {
    const date = new Date(dateString);
    // Remove the 'Z' from the ISO string to make it compatible with Python's fromisoformat()
    return date.toISOString().replace('Z', '');
  };
  
  // Get user_id from localStorage if available
  const user_id = localStorage.getItem('userUID');
  
  const bookingData = {
    booking_id: generateUniqueId(),
    email: email,
    user_id: user_id, // Include user_id from localStorage if available
    start_time: formatISODate(pickupDate),
    end_time: formatISODate(returnDate),
    contact_number: phone,
    car_id: selectedCar.id,
    payment_status: 'pending',
    payment_method: paymentMethod,
    total_amount: calculateTotalAmount(selectedCar, pickupDate, returnDate),
    details: {
      user_name: `${firstName} ${lastName}`,
      car_details: {
        id: selectedCar.id,
        make: selectedCar.make,
        model: selectedCar.model,
        year: selectedCar.year,
        color: selectedCar.color,
        price_per_hour: selectedCar.price_per_hour
      }
    }
  };
  
  try {
    // Log booking to booking log microservice with full URL
    console.log('Sending booking data:', bookingData);
    
    // Use window.location.hostname to make it work in different environments
    const hostname = window.location.hostname === 'localhost' ? '127.0.0.1' : window.location.hostname;
    const response = await axios.post(`http://${hostname}:5006/api/booking-log`, bookingData);
    
    console.log('Booking response:', response.data);
    
    // Update car availability - also use the dynamic hostname
    await axios.put(`http://${hostname}:5000/car/${selectedCar.id}/availability`, { available: false });
    
    // Show success message
    showBookingConfirmation(bookingData);
  } catch (error) {
    console.error('Booking error:', error);
    if (error.response) {
      console.error('Error response data:', error.response.data);
      console.error('Error response status:', error.response.status);
    } else if (error.request) {
      console.error('No response received:', error.request);
    }
    alert('Booking failed. Please check the console for details.');
  }
}

// Display booking confirmation
function showBookingConfirmation(bookingData) {
  // Create modal for booking confirmation
  const modal = document.createElement('div');
  modal.className = 'booking-confirmation-modal';
  
  const startDate = new Date(bookingData.start_time);
  const endDate = new Date(bookingData.end_time);
  
  modal.innerHTML = `
    <div class="modal-content">
      <h2>Booking Confirmed!</h2>
      <p>Thank you ${bookingData.details.user_name} for your booking.</p>
      <div class="confirmation-details">
        <p><strong>Booking ID:</strong> ${bookingData.booking_id}</p>
        <p><strong>Car:</strong> ${bookingData.details.car_details.make} ${bookingData.details.car_details.model}</p>
        <p><strong>Pickup:</strong> ${startDate.toLocaleString()}</p>
        <p><strong>Return:</strong> ${endDate.toLocaleString()}</p>
        <p><strong>Total Amount:</strong> $${bookingData.total_amount}</p>
      </div>
      <p>A confirmation email has been sent to ${bookingData.email}</p>
      <button class="close-modal-btn">Close</button>
    </div>
  `;
  
  // Add style for the modal
  const style = document.createElement('style');
  style.textContent = `
    .booking-confirmation-modal {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0,0,0,0.7);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 2000;
    }
    .modal-content {
      background-color: white;
      padding: 30px;
      border-radius: 10px;
      box-shadow: 0 5px 15px rgba(0,0,0,0.3);
      max-width: 500px;
      width: 90%;
      text-align: center;
    }
    .confirmation-details {
      text-align: left;
      margin: 20px 0;
      padding: 15px;
      background-color: #f9f9f9;
      border-radius: 5px;
    }
    .close-modal-btn {
      background-color: #2196F3;
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 5px;
      cursor: pointer;
      font-weight: bold;
      margin-top: 15px;
    }
  `;
  document.head.appendChild(style);
  
  document.body.appendChild(modal);
  
  // Add close button functionality
  modal.querySelector('.close-modal-btn').addEventListener('click', () => {
    document.body.removeChild(modal);
    // Redirect to home page or refresh the current page
    window.location.href = 'index.html';
  });
}

function calculateTotalAmount(car, startTime, endTime) {
  const start = new Date(startTime);
  const end = new Date(endTime);
  const hours = (end - start) / (1000 * 60 * 60);
  return (hours * car.price_per_hour).toFixed(2);
}

function generateUniqueId() {
  return 'booking-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
  // Add book now button event listener
  const bookNowButton = document.getElementById('book-now');
  if (bookNowButton) {
    bookNowButton.addEventListener('click', bookCar);
  }
  
  // Set min date for pickup and return date inputs
  const pickupDateInput = document.getElementById('pickup-date');
  const returnDateInput = document.getElementById('return-date');
  
  if (pickupDateInput && returnDateInput) {
    const now = new Date();
    const formattedDate = now.toISOString().slice(0, 16);
    pickupDateInput.min = formattedDate;
    
    pickupDateInput.addEventListener('change', () => {
      returnDateInput.min = pickupDateInput.value;
    });
  }
  
  // Check if we're on the booking page and need to initialize the map
  // Note: The map will be initialized by the Google Maps callback in the HTML
});