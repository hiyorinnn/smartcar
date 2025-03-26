// Global variables to store selected car and user details
let selectedCar = null;

// Fetch nearby cars on page load
async function fetchNearbyCars() {
    try {
        const response = await axios.get('/car/available');
        const carsContainer = document.getElementById('cars-container');
        carsContainer.innerHTML = ''; // Clear loading text

        response.data.data.cars.forEach(car => {
            const carCard = document.createElement('div');
            carCard.className = 'car-card';
            carCard.innerHTML = `
                <h3>${car.make} ${car.model}</h3>
                <p>Year: ${car.year}</p>
                <p>Color: ${car.color}</p>
                <p>Price: $${car.price_per_hour}/hour</p>
            `;
            carCard.addEventListener('click', () => selectCar(car, carCard));
            carsContainer.appendChild(carCard);
        });
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

    // Prepare booking log data
    const bookingData = {
        user_id: email, // Using email as user ID
        user_name: `${firstName} ${lastName}`,
        start_time: pickupDate,
        end_time: returnDate,
        contact_number: phone,
        email_address: email,
        car_id: selectedCar.id,
        action: 'created',
        payment_status: 'pending',
        payment_method: paymentMethod,
        total_amount: calculateTotalAmount(selectedCar, pickupDate, returnDate),
        details: {
            car_details: selectedCar
        }
    };

    try {
        // Log booking to booking log microservice
        const response = await axios.post('/api/booking-log', bookingData);
        
        // Update car availability 
        await axios.put(`/car/${selectedCar.id}/availability`, { available: false });

        alert('Booking successful! Your booking has been logged.');
    } catch (error) {
        console.error('Booking error:', error);
        alert('Booking failed. Please try again.');
    }
}

function calculateTotalAmount(car, startTime, endTime) {
    const start = new Date(startTime);
    const end = new Date(endTime);
    const hours = (end - start) / (1000 * 60 * 60);
    return (hours * car.price_per_hour).toFixed(2);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('book-now').addEventListener('click', bookCar);

    // Fetch cars when page loads
    fetchNearbyCars();
});