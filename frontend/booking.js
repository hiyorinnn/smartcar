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
        const response = await axios.post('http://127.0.0.1:5006/api/booking-log', bookingData);
        console.log('Booking response:', response.data);

        
        // Update car availability 
        await axios.put(`http://localhost:5000/car/${selectedCar.id}/availability`, { available: false });
        alert('Booking successful! Your booking has been logged.');

        // Push bookingID to payment page 
        const bookingId = response.data.data.booking_id;
        // Store it in localStorage (or sessionStorage)
        localStorage.setItem("bookingData", JSON.stringify({ booking_id: bookingId }));
        window.location.href = "./checkout.html";

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
