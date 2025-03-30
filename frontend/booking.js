// Global variables to store selected car and user details
let selectedCar = null;

async function fetchNearbyCars() {
    try {
        const response = await axios.get('http://127.0.0.1:5001/get_cars_in_geofence');
        const carsContainer = document.getElementById('cars-container');
        carsContainer.innerHTML = ''; // Clear loading text

        // Directly use the cars array from the response
        const cars = response.data.cars;

        // Filter only available cars
        const availableCars = cars.filter(car => car.available);

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

    // Ensure dates are in ISO format
    const formatISODate = (dateString) => {
        const date = new Date(dateString);
        return date.toISOString();
    };

    const bookingData = {
        booking_id: generateUniqueId(),
        email: email,  // Change from email_address to email
        start_time: formatISODate(pickupDate),
        end_time: formatISODate(returnDate),
        contact_number: phone,
        car_id: selectedCar.id,
        payment_status: 'pending',
        payment_method: paymentMethod,
        total_amount: calculateTotalAmount(selectedCar, pickupDate, returnDate),
        details: {
          user_name: `${firstName} ${lastName}`,
          car_details: selectedCar
        }
      };

    try {
        // Log booking to booking log microservice with full URL
        const response = await axios.post('http://127.0.0.1:5006/api/booking-log', bookingData);
        
        console.log('Booking response:', response.data);
        
        // Update car availability 
        await axios.put(`/car/${selectedCar.id}/availability`, { available: false });

        alert('Booking successful! Your booking has been logged.');
    } catch (error) {
        console.error('Booking error:', error.response ? error.response.data : error);
        alert('Booking failed. Please check the console for details.');
    }
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