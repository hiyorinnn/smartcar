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

async function fetchNearbyCars() {
  try {
    const carsContainer = document.getElementById('cars-container');
    carsContainer.innerHTML = '<p>Loading available cars...</p>';
    
    // Check if there's a saved location in sessionStorage
    const savedLocation = sessionStorage.getItem('selectedLocation');
    
    // Use hostname to make it work in different environments
    const hostname = window.location.hostname === 'localhost' ? '127.0.0.1' : window.location.hostname;
    let apiUrl;
    
    // Define the valid locations here to avoid dependency on the other file
    const validLocations = [
      'Ang Mo Kio', 'Bedok', 'Bishan', 'Bukit Batok', 'Bukit Merah',
      'Bukit Panjang', 'Bukit Timah', 'Central Area', 'Choa Chu Kang',
      'Clementi', 'Hougang', 'Geylang', 'Jurong East', 'Jurong West',
      'Kallang', 'Marine Parade', 'Pasir Ris', 'Punggol', 'Queenstown',
      'Sembawang', 'Serangoon', 'Tampines', 'Toa Payoh', 'Woodlands', 'Yishun'
    ];
    
    // Display the location that was searched
    if (savedLocation) {
      if (!document.getElementById('selected-location')) {
        const locationDisplay = document.createElement('div');
        locationDisplay.id = 'selected-location';
        locationDisplay.className = 'location-display';
        carsContainer.parentNode.insertBefore(locationDisplay, carsContainer);
      }
      
      const locationDisplay = document.getElementById('selected-location');
      locationDisplay.textContent = `Cars available near: ${savedLocation}`;
      
      // Important: Only use location-specific endpoint when location is in the dropdown
      console.log(`Checking location: ${savedLocation}`);
      
      // Check if the saved location is in our predefined valid locations array
      if (validLocations.includes(savedLocation)) {
        // Use location-specific endpoint
        apiUrl = `http://${hostname}:5001/get_cars_by_location/${encodeURIComponent(savedLocation)}`;
        console.log(`Using location-specific endpoint for: ${savedLocation}`);
      } else {
        // Use default endpoint if location is not in the valid locations list
        apiUrl = `http://${hostname}:5001/get_cars_by_location`;
        console.log(`Location not in dropdown, using default endpoint`);
      }
    } else {
      // If no location specified, use the default endpoint that uses IP location
      apiUrl = `http://${hostname}:5001/get_cars_by_location`;
      console.log('No location set, using default endpoint');
    }
    
    // Make the API request
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

// Validate email format
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// Calculate hours between two datetime inputs
function calculateHoursBetween(startTime, endTime) {
  const start = new Date(startTime);
  const end = new Date(endTime);
  const diffMs = end - start;
  const diffHours = diffMs / (1000 * 60 * 60);
  return diffHours;
}

// Round time to nearest hour (for booking slots)
function roundToNextHour(date) {
  const roundedDate = new Date(date);
  roundedDate.setMinutes(0);
  roundedDate.setSeconds(0);
  roundedDate.setMilliseconds(0);
  // Always move to the next hour to ensure we don't book in the past
  roundedDate.setHours(roundedDate.getHours() + 1);
  return roundedDate;
}

// Show validation error message
function showValidationError(inputElement, message) {
  // Find the corresponding error element
  const errorId = inputElement.id + '-error';
  const errorElement = document.getElementById(errorId);
  
  if (errorElement) {
    // Update the message and display the error
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    inputElement.classList.add('error');
  }
}

// Remove validation error message
function clearValidationError(inputElement) {
  const errorId = inputElement.id + '-error';
  const errorElement = document.getElementById(errorId);
  
  if (errorElement) {
    errorElement.style.display = 'none';
    inputElement.classList.remove('error');
  }
}

// Book the car
async function bookCar() {
  // Get form values
  const firstName = document.getElementById('first-name').value;
  const lastName = document.getElementById('last-name').value;
  const email = document.getElementById('email').value;
  const phone = document.getElementById('phone').value;
  
  // Get date and time from separate inputs
  const pickupDateDay = document.getElementById('pickup-date-day').value;
  const pickupDateHour = document.getElementById('pickup-date-hour').value;
  const returnDateDay = document.getElementById('return-date-day').value;
  const returnDateHour = document.getElementById('return-date-hour').value;
  
  // Combine date and hour into datetime strings
  const pickupDate = `${pickupDateDay}T${pickupDateHour}:00`;
  const returnDate = `${returnDateDay}T${returnDateHour}:00`;
  
  const paymentMethod = document.getElementById('payment-method').value;
  
  let isValid = true;
  
  // Clear any previous validation errors
  document.querySelectorAll('.error-message').forEach(el => {
    el.style.display = 'none';
  });
  document.querySelectorAll('.error').forEach(el => {
    el.classList.remove('error');
  });
  
  // Validation checks
  
  // 1. Check if car is selected
  if (!selectedCar) {
    showValidationError(document.getElementById('selected-car'), 'Please select a car first');
    isValid = false;
  }
  
  // 2. Validate email format
  if (!isValidEmail(email)) {
    showValidationError(document.getElementById('email'), 'Please enter a valid email address');
    isValid = false;
  }
  
  // 3. Check if return time is after pickup time
  const startTime = new Date(pickupDate);
  const endTime = new Date(returnDate);
  
  if (endTime <= startTime) {
    showValidationError(document.getElementById('return-date-day'), 'End time must be after start time');
    isValid = false;
  }
  
  // 4. Calculate hours between pickup and return
  const hours = calculateHoursBetween(startTime, endTime);
  
  // 5. Check if booking duration exceeds the maximum of 6 hours
  if (hours > 6) {
    showValidationError(document.getElementById('return-date-day'), 'Maximum booking duration is 6 hours');
    isValid = false;
  }
  
  // 6. Check if booking is made on hourly basis (no partial hours)
  if (Math.floor(hours) !== hours) {
    showValidationError(document.getElementById('return-date-day'), 'Bookings must be made on an hourly basis');
    isValid = false;
  }
  
  // 7. Check if first name and last name are provided
  if (!firstName.trim()) {
    showValidationError(document.getElementById('first-name'), 'First name is required');
    isValid = false;
  }
  
  if (!lastName.trim()) {
    showValidationError(document.getElementById('last-name'), 'Last name is required');
    isValid = false;
  }
  
  // 8. Check if phone number is provided
  if (!phone.trim()) {
    showValidationError(document.getElementById('phone'), 'Phone number is required');
    isValid = false;
  }
  
  // Check if validation passed
  if (!isValid) {
    console.log('Validation failed. Booking not submitted.');
    return;
  }
  
  // Ensure dates are in ISO format compatible with Python's fromisoformat()
  // This preserves the local time selected by the user
  const formatISODate = (dateString) => {
    const date = new Date(dateString);
    
    // Format the date manually to preserve local time
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    // Return in ISO format without timezone conversion
    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
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
    console.log('Validation passed. Sending booking data:', bookingData);
    
    // Use window.location.hostname to make it work in different environments
    const hostname = window.location.hostname === 'localhost' ? '127.0.0.1' : window.location.hostname;
    const response = await axios.post(`http://${hostname}:5006/api/booking-log`, bookingData);
    
    console.log('Booking response:', response.data);
    
    // Update car availability - also use the dynamic hostname
    await axios.put(`http://${hostname}:5000/car/${selectedCar.id}/availability`, { available: false });
    
    // Show booking summary
    showBookingSummary(bookingData);
  } catch (error) {
    console.error('Booking error:', error);
    if (error.response) {
      console.error('Error response data:', error.response.data);
      console.error('Error response status:', error.response.status);
      
      // Display backend validation errors if available
      if (error.response.data && error.response.data.errors) {
        Object.entries(error.response.data.errors).forEach(([field, message]) => {
          const inputElement = document.getElementById(field);
          if (inputElement) {
            showValidationError(inputElement, message);
          }
        });
      } else {
        alert('Booking failed: ' + (error.response.data.message || 'Unknown error'));
      }
    } else if (error.request) {
      console.error('No response received:', error.request);
      alert('Booking failed: No response from server');
    } else {
      alert('Booking failed. Please check the console for details.');
    }
  }
}

// Display booking summary with proceed to payment button
function showBookingSummary(bookingData) {
  // Create modal for booking summary
  const modal = document.createElement('div');
  modal.className = 'booking-summary-modal';
  
  const startDate = new Date(bookingData.start_time);
  const endDate = new Date(bookingData.end_time);
  
  // Store booking data in sessionStorage for the checkout page
  localStorage.setItem('bookingData', JSON.stringify(bookingData));
  
  modal.innerHTML = `
    <div class="modal-content">
      <h2>Booking Summary</h2>
      <p>Thank you ${bookingData.details.user_name} for your booking.</p>
      <div class="confirmation-details">
        <p><strong>Booking ID:</strong> ${bookingData.booking_id}</p>
        <p><strong>Car:</strong> ${bookingData.details.car_details.make} ${bookingData.details.car_details.model}</p>
        <p><strong>Pickup:</strong> ${startDate.toLocaleString()}</p>
        <p><strong>Return:</strong> ${endDate.toLocaleString()}</p>
        <p><strong>Total Amount:</strong> $${bookingData.total_amount}</p>
      </div>
      <button class="proceed-payment-btn">Proceed to Payment</button>
    </div>
  `;
  
  // Add style for the modal
  const style = document.createElement('style');
  style.textContent = `
    .booking-summary-modal {
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
    .proceed-payment-btn {
      background-color: #2196F3;
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 5px;
      cursor: pointer;
      font-weight: bold;
      margin-top: 15px;
      transition: background-color 0.3s;
    }
    .proceed-payment-btn:hover {
      background-color: #0d8bf2;
    }
  `;
  document.head.appendChild(style);
  
  document.body.appendChild(modal);
  
  // Add proceed to payment button functionality
  modal.querySelector('.proceed-payment-btn').addEventListener('click', () => {
    window.location.href = 'checkout.html';
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
  // Parse URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const locationFromUrl = urlParams.get('location');
  const latFromUrl = urlParams.get('lat');
  const lngFromUrl = urlParams.get('lng');
  
  // Store in sessionStorage if they exist in URL
  if (locationFromUrl) {
    sessionStorage.setItem('selectedLocation', locationFromUrl);
  }
  if (latFromUrl) {
    sessionStorage.setItem('selectedLocationLat', latFromUrl);
  }
  if (lngFromUrl) {
    sessionStorage.setItem('selectedLocationLng', lngFromUrl);
  }
  
  // Add book now button event listener
  const bookNowButton = document.getElementById('book-now');
  if (bookNowButton) {
    bookNowButton.addEventListener('click', bookCar);
  }
  
    // Set min date for pickup and return date inputs
  const pickupDateDay = document.getElementById('pickup-date-day');
  const pickupDateHour = document.getElementById('pickup-date-hour');
  const returnDateDay = document.getElementById('return-date-day');
  const returnDateHour = document.getElementById('return-date-hour');
  
  if (pickupDateDay && pickupDateHour && returnDateDay && returnDateHour) {
    // Get current date and time
    const now = new Date();
    
    // Round current time to next hour for hourly bookings
    const nextHour = roundToNextHour(now);
    
    // Format date for date input (YYYY-MM-DD)
    const formatDateInput = (date) => {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    };
    
    // Function to check if a selected date and hour is in the past
    const isTimeInPast = (dateStr, hour) => {
      const selectedDate = new Date(dateStr);
      selectedDate.setHours(parseInt(hour), 0, 0, 0);
      const currentTime = new Date();
      return selectedDate < currentTime;
    };
    
    // Function to get combined datetime from separate inputs
    const getCombinedDateTime = (dateInput, hourInput) => {
      const dateValue = dateInput.value;
      const hourValue = hourInput.value;
      if (!dateValue || !hourValue) return null;
      
      const date = new Date(dateValue);
      date.setHours(parseInt(hourValue), 0, 0, 0);
      return date;
    };
    
    // Populate hour options for both dropdowns
    const populateHourOptions = (selectElement, selectedHour = null, minHour = 0, maxHour = 23) => {
      // Clear existing options
      selectElement.innerHTML = '';
      
      // Add hour options (00-23)
      for (let i = minHour; i <= maxHour; i++) {
        const option = document.createElement('option');
        const hourFormatted = String(i).padStart(2, '0');
        option.value = hourFormatted;
        option.textContent = `${hourFormatted}:00`;
        
        if (selectedHour !== null && parseInt(selectedHour) === i) {
          option.selected = true;
        }
        
        selectElement.appendChild(option);
      }
    };
    
    // Set min values and default values for date inputs
    pickupDateDay.min = formatDateInput(now);
    pickupDateDay.value = formatDateInput(nextHour);
    
    returnDateDay.min = formatDateInput(now);
    returnDateDay.value = formatDateInput(nextHour);
    
    // Default end time is 1 hour after pickup
    const defaultEndTime = new Date(nextHour);
    defaultEndTime.setHours(defaultEndTime.getHours() + 1);
    
    // Populate hour dropdowns with initial values
    populateHourOptions(pickupDateHour, nextHour.getHours());
    populateHourOptions(returnDateHour, defaultEndTime.getHours());
    
    // Update available hours when pickup date changes
    pickupDateDay.addEventListener('change', () => {
      const selectedDate = pickupDateDay.value;
      const today = formatDateInput(now);
      
      // If selected date is today, restrict hours to future hours only
      if (selectedDate === today) {
        const currentHour = now.getHours();
        // Populate with hours after the current hour
        populateHourOptions(pickupDateHour, null, currentHour + 1, 23);
      } else {
        // For future dates, show all hours
        populateHourOptions(pickupDateHour);
      }
      
      // Validate the combined date and time
      validatePickupDateTime();
    });
    
    // Validate pickup date and time when hour changes
    pickupDateHour.addEventListener('change', validatePickupDateTime);
    
    // Function to validate pickup date and time
    function validatePickupDateTime() {
      const selectedDate = pickupDateDay.value;
      const selectedHour = pickupDateHour.value;
      
      // Check if selected time is in the past
      if (isTimeInPast(selectedDate, selectedHour)) {
        // Set to next hour from current time
        const nextAvailableHour = roundToNextHour(new Date());
        pickupDateDay.value = formatDateInput(nextAvailableHour);
        populateHourOptions(pickupDateHour, nextAvailableHour.getHours());
        showValidationError(pickupDateDay, "Cannot book times in the past");
      } else {
        clearValidationError(pickupDateDay);
      }
      
      // Update return date constraints
      updateReturnDateConstraints();
    }
    
    // Function to update return date constraints based on pickup date
    function updateReturnDateConstraints() {
      const pickupDateTime = getCombinedDateTime(pickupDateDay, pickupDateHour);
      if (!pickupDateTime) return;
      
      // Set minimum return date to pickup date
      returnDateDay.min = formatDateInput(pickupDateTime);
      
      // If return date is before pickup date, update it
      const returnDateTime = getCombinedDateTime(returnDateDay, returnDateHour);
      if (!returnDateTime || returnDateTime <= pickupDateTime) {
        // Set return time to 1 hour after pickup
        const newEndTime = new Date(pickupDateTime);
        newEndTime.setHours(newEndTime.getHours() + 1);
        
        returnDateDay.value = formatDateInput(newEndTime);
        
        // Update hour options for return date
        if (formatDateInput(pickupDateTime) === formatDateInput(newEndTime)) {
          // Same day: show hours after pickup hour
          populateHourOptions(returnDateHour, newEndTime.getHours(), parseInt(pickupDateHour.value) + 1, 23);
        } else {
          // Different day: show all hours
          populateHourOptions(returnDateHour, newEndTime.getHours());
        }
      }
    }
    
    // Update available return hours when return date changes
    returnDateDay.addEventListener('change', () => {
      const pickupDateTime = getCombinedDateTime(pickupDateDay, pickupDateHour);
      if (!pickupDateTime) return;
      
      const isSameDay = pickupDateDay.value === returnDateDay.value;
      
      // If same day as pickup, restrict hours to after pickup hour
      if (isSameDay) {
        const pickupHour = parseInt(pickupDateHour.value);
        populateHourOptions(returnDateHour, null, pickupHour + 1, 23);
      } else {
        // For future dates, show all hours
        populateHourOptions(returnDateHour);
      }
      
      validateReturnDateTime();
    });
    
    // Validate return date and time when hour changes
    returnDateHour.addEventListener('change', validateReturnDateTime);
    
    // Function to validate return date and time
    function validateReturnDateTime() {
      const pickupDateTime = getCombinedDateTime(pickupDateDay, pickupDateHour);
      const returnDateTime = getCombinedDateTime(returnDateDay, returnDateHour);
      
      if (!pickupDateTime || !returnDateTime) return;
      
      // Ensure return time is after pickup time
      if (returnDateTime <= pickupDateTime) {
        showValidationError(returnDateDay, 'Return time must be after pickup time');
        
        // Reset to valid value (pickup time + 1 hour)
        const newEndTime = new Date(pickupDateTime);
        newEndTime.setHours(newEndTime.getHours() + 1);
        
        returnDateDay.value = formatDateInput(newEndTime);
        returnDateHour.value = String(newEndTime.getHours()).padStart(2, '0');
      } else {
        clearValidationError(returnDateDay);
      }
      
      // Check if booking exceeds max duration (6 hours)
      const hoursDiff = calculateHoursBetween(pickupDateTime, returnDateTime);
      if (hoursDiff > 6) {
        showValidationError(returnDateDay, 'Maximum booking duration is 6 hours');
        
        // Reset to valid value (pickup time + 6 hours)
        const maxEndTime = new Date(pickupDateTime);
        maxEndTime.setHours(maxEndTime.getHours() + 6);
        
        returnDateDay.value = formatDateInput(maxEndTime);
        returnDateHour.value = String(maxEndTime.getHours()).padStart(2, '0');
      }
    }
    
    // This section is no longer needed as it's handled by the new date/hour inputs
  }
  
  // Email validation
  const emailInput = document.getElementById('email');
  if (emailInput) {
    emailInput.addEventListener('blur', () => {
      if (emailInput.value && !isValidEmail(emailInput.value)) {
        showValidationError(emailInput, 'Please enter a valid email address');
      } else {
        clearValidationError(emailInput);
      }
    });
  }
});

