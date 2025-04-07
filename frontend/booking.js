// Global variables to store selected car and user details
let selectedCar = null;

async function fetchNearbyCars() {
    try {
        const response = await axios.get('http://127.0.0.1:5001/get_cars_by_location');
        console.log('Fetched cars:', response.data);
        const carsContainer = document.getElementById('cars-container');
        carsContainer.innerHTML = ''; // Clear loading text

        // Directly use the cars array from the response
        const availableCars = response.data.cars;
        console.log('Available cars:', availableCars);

        if (availableCars.length === 0) {
            carsContainer.innerHTML = '<p>No cars available at the moment.</p>';
            return;
        }

        availableCars.forEach(car => {
            const carCard = document.createElement('div');
            carCard.className = 'car-card';
            carCard.innerHTML = `
                <h3>${car.make} ${car.model}</h3>
                <p>Year: ${car.year}</p>
                <p>Color: ${car.color}</p>
                <p>Price: $${car.price_per_hour}/hour</p>
                <p>Location: (${car.latitude}, ${car.longitude})</p>
            `;
            carCard.addEventListener('click', () => selectCar(car, carCard));
            carsContainer.appendChild(carCard);
        });

        console.log('Fetched cars:', availableCars);
    } catch (error) {
        console.error('Error fetching cars:', error);
        const carsContainer = document.getElementById('cars-container');
        carsContainer.innerHTML = '<p>Error loading cars. Please try again later.</p>';
    }
}

function selectCar(car, cardElement) {
    // Remove selected class from all car cards
    document.querySelectorAll('.car-card').forEach(card => {
        card.classList.remove('selected');
    });

    // Add selected class to clicked card
    cardElement.classList.add('selected');

    selectedCar = car;
    document.getElementById('selected-car').value = `${car.make} ${car.model} (${car.id})`;
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
  sessionStorage.setItem('currentBooking', JSON.stringify(bookingData));
  
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
    document.getElementById('book-now').addEventListener('click', bookCar);

    // Fetch cars when page loads
    fetchNearbyCars();
});
