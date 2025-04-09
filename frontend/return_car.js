// Global variables to store selected booking and details
let selectedBooking = null;
let userEmail = null;
let uploadedPhotos = [];
let assessmentResult = null;

// Function to format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Format currency
function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2);
}

// Set the current date and time in the actual-return-date input
function setCurrentDateTime() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    
    const currentDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;
    document.getElementById('actual-return-date').value = currentDateTime;
}

// Fetch active bookings for the user
async function fetchActiveBookings() {
    // Get user ID from localStorage (consistent with booking.js)
    const userId = localStorage.getItem('userUID');
    
    if (!userId) {
        document.getElementById('active-bookings-container').innerHTML = 
            '<p>User ID not found. Please log in first.</p>';
        return;
    }
    
    try {
        // Use user ID to fetch bookings
        const response = await axios.get(`http://127.0.0.1:5011/api/get-all-bookings/${userId}`);
        const activeBookingsContainer = document.getElementById('active-bookings-container');
        
        activeBookingsContainer.innerHTML = ''; // Clear loading text
        
        // Filter only active bookings (status is 'not_started' or 'in_progress')
        const bookings = response.data.data.booking_logs;
        const activeBookings = bookings.filter(booking => 
            booking.booking_status === 'not_started' || booking.booking_status === 'in_progress');
        
        if (activeBookings.length === 0) {
            activeBookingsContainer.innerHTML = '<p>You have no active bookings.</p>';
            return;
        }
        
        activeBookings.forEach(booking => {
            const bookingCard = document.createElement('div');
            bookingCard.className = 'car-card';
            
            // Get car details from booking
            const carDetails = booking.details?.details?.car_details || { make: 'Unknown', model: 'Unknown' };
            
            bookingCard.innerHTML = `
                <h3>Booking #${booking.booking_id.substring(0, 8)}...</h3>
                <p>Car: ${carDetails.make} ${carDetails.model}</p>
                <p>Start: ${formatDate(booking.start_time)}</p>
                <p>End: ${formatDate(booking.end_time)}</p>
                <p>Status: ${booking.booking_status}</p>
            `;
            
            bookingCard.addEventListener('click', () => selectBooking(booking, bookingCard));
            activeBookingsContainer.appendChild(bookingCard);
        });
        
        console.log('Fetched active bookings:', activeBookings);
        
        // Disable form fields until a booking is selected
        toggleFormFields(false);
        
    } catch (error) {
        console.error('Error fetching bookings:', error);
        document.getElementById('active-bookings-container').innerHTML = 
            '<p>Error loading bookings. Please try again later.</p>';
    }
}

// Toggle form fields enabled/disabled state
function toggleFormFields(enabled) {
    const formElements = [
        'actual-return-date',
        'car-photos',
        'analyze-condition',
        'calculate-charges',
        'confirm-return',
        'update-timing',
        'end-booking'
    ];
    
    formElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.disabled = !enabled;
        }
    });
    
    // Also update the file upload label appearance
    const fileLabel = document.querySelector('.file-upload-label');
    if (fileLabel) {
        if (enabled) {
            fileLabel.classList.remove('disabled');
        } else {
            fileLabel.classList.add('disabled');
        }
    }
}

// Select a booking
function selectBooking(booking, cardElement) {
    // Remove selected class from all booking cards
    document.querySelectorAll('.car-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Add selected class to clicked card
    cardElement.classList.add('selected');
    
    selectedBooking = booking;
    
    // Get car details from booking
    const carDetails = booking.details?.car_details || { make: 'Unknown', model: 'Unknown' };
    
    // Display booking_id as the primary identifier, followed by car details if available
    document.getElementById('selected-booking').value = 
        `Booking ID: ${booking.booking_id} ${carDetails.make !== 'Unknown' ? `(${carDetails.make} ${carDetails.model})` : ''}`;
    document.getElementById('booking-id').value = booking.booking_id;
    
    // Reset charges and condition
    document.getElementById('damage-charge').textContent = '$0.00';
    document.getElementById('total-additional').textContent = '$0.00';
    document.getElementById('condition').value = 'Awaiting analysis...';
    document.getElementById('condition-details').innerHTML = '';
    
    // Hide the end booking button and show the normal workflow initially
    const endBookingBtn = document.getElementById('end-booking');
    if (endBookingBtn) {
        endBookingBtn.style.display = 'none';
    }
    
    const additionalChargesContainer = document.getElementById('additional-charges-container');
    if (additionalChargesContainer) {
        additionalChargesContainer.style.display = 'block';
    }
    
    const calculateChargesBtn = document.getElementById('calculate-charges');
    if (calculateChargesBtn) {
        calculateChargesBtn.style.display = 'block';
    }
    
    const confirmReturnBtn = document.getElementById('confirm-return');
    if (confirmReturnBtn) {
        confirmReturnBtn.style.display = 'block';
    }
    
    // Clear photo previews
    document.getElementById('photo-preview-container').innerHTML = '';
    uploadedPhotos = [];
    assessmentResult = null;
    
    // Enable form fields now that a booking is selected
    toggleFormFields(true);
}

// Handle photo uploads with better UI feedback
function handlePhotoUpload(event) {
    event.preventDefault();
    
    if (!selectedBooking) {
        alert('Please select a booking first');
        return;
    }
    
    const fileInput = document.getElementById('car-photos');
    const previewContainer = document.getElementById('photo-preview-container');
    
    // Clear previous previews
    previewContainer.innerHTML = '';
    uploadedPhotos = [];
    
    if (fileInput.files.length > 0) {
        for (let i = 0; i < fileInput.files.length; i++) {
            const file = fileInput.files[i];
            
            // Store the file for later upload
            uploadedPhotos.push(file);
            
            // Create preview
            const preview = document.createElement('div');
            preview.className = 'photo-preview';
            
            const img = document.createElement('img');
            img.src = URL.createObjectURL(file);
            img.onload = function() {
                URL.revokeObjectURL(this.src);
            };
            
            // Add remove button
            const removeBtn = document.createElement('button');
            removeBtn.className = 'remove-photo';
            removeBtn.innerHTML = '×';
            removeBtn.dataset.index = i;
            removeBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                removePhoto(parseInt(this.dataset.index));
            });
            
            preview.appendChild(img);
            preview.appendChild(removeBtn);
            previewContainer.appendChild(preview);
        }
    }
}

// Remove a photo from the preview and uploaded files array
function removePhoto(index) {
    // Create a new FileList without the removed file
    uploadedPhotos.splice(index, 1);
    
    // Recreate the preview
    const previewContainer = document.getElementById('photo-preview-container');
    previewContainer.innerHTML = '';
    
    // Recreate remaining previews
    uploadedPhotos.forEach((file, i) => {
        const preview = document.createElement('div');
        preview.className = 'photo-preview';
        
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.onload = function() {
            URL.revokeObjectURL(this.src);
        };
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'remove-photo';
        removeBtn.innerHTML = '×';
        removeBtn.dataset.index = i;
        removeBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            removePhoto(parseInt(this.dataset.index));
        });
        
        preview.appendChild(img);
        preview.appendChild(removeBtn);
        previewContainer.appendChild(preview);
    });
}

// Upload and analyze car photos
// Upload and analyze car photos
async function analyzeCarCondition() {
    if (!selectedBooking) {
        alert('Please select a booking first');
        return;
    }
    
    if (uploadedPhotos.length === 0) {
        alert('Please upload photos of the car');
        return;
    }
    
    const uploadStatus = document.getElementById('upload-status');
    
    uploadStatus.textContent = 'Uploading and analyzing photos...';
    uploadStatus.classList.add('uploading-animation');
    
    try {
        // Create a FormData object to send the photos
        const formData = new FormData();
        uploadedPhotos.forEach((photo, index) => {
            formData.append('images', photo);
        });
        
        formData.append('booking_id', selectedBooking.booking_id);
        
        // Send the photos to your backend microservice for analysis
        const response = await axios.post('http://127.0.0.1:5011/api/return-vehicle', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        
        // Check response type and handle accordingly
        if (response.data.message === "no-violations" && response.status === 200) {
            // No violations case - show end booking button
            handleZeroDefects();
            
            uploadStatus.textContent = 'Analysis complete! No violations found.';
            uploadStatus.classList.remove('uploading-animation');
        } 
        else if (response.data.message === "Vehicle return processed with violations" && response.status === 200) {
            // Violations detected - update UI and redirect to payment
            
            // Update charge display if amount is provided
            if (response.data.amount) {
                document.getElementById('damage-charge').textContent = formatCurrency(response.data.amount);
                document.getElementById('total-additional').textContent = formatCurrency(response.data.amount);
            }
            
            // Update status and inform user of redirect
            document.getElementById('condition').value = 'Issues detected - payment required';
            document.getElementById('condition-details').innerHTML = 
                'Vehicle returned with violations. Redirecting to payment page...';
            
            uploadStatus.textContent = 'Analysis complete! Redirecting to payment...';
            uploadStatus.classList.remove('uploading-animation');
            
            // Use the redirect_url from the response, fall back to default if not provided
            const redirectUrl = response.data.redirect_url || 'fines_checkout.html';
            
            // Redirect to the payment URL after a short delay
            setTimeout(() => {
                window.location.href = redirectUrl;
            }, 2000); // 2-second delay to allow the user to see the message
        }
        else {
            // Unexpected response format
            console.error('Unexpected response format:', response.data);
            uploadStatus.textContent = 'Error processing analysis. Please try again.';
            uploadStatus.classList.remove('uploading-animation');
        }
        
    } catch (error) {
        console.error('Error analyzing car condition:', error);
        uploadStatus.textContent = 'Failed to analyze photos. Please try again.';
        uploadStatus.classList.remove('uploading-animation');
    }
}

// Handle zero defects case
function handleZeroDefects() {
    // Hide additional charges section and associated buttons
    document.getElementById('additional-charges-container').style.display = 'none';
    document.getElementById('calculate-charges').style.display = 'none';
    document.getElementById('confirm-return').style.display = 'none';
    
    // Show the end booking button
    const endBookingBtn = document.getElementById('end-booking');
    endBookingBtn.style.display = 'block';
    
    // Update condition display to show perfect condition
    document.getElementById('condition').value = 'Excellent - No issues detected';
}

// End booking and redirect to index.html (for zero defects case)
async function endBooking() {
    if (!selectedBooking) {
        alert('Please select a booking first');
        return;
    }
    
    // Get actual return date
    const actualReturnDate = document.getElementById('actual-return-date').value;
    
    try {
        // 1. Update booking status to 'ended'
        const statusUpdateResponse = await axios.put(
            `http://127.0.0.1:5006/api/booking-logs/${selectedBooking.booking_id}/status`,
            { booking_status: 'ended' }
        );
        
        // 2. Update return information without additional charges
        const returnInfoData = {
            payment_status: 'completed', // Assuming no additional charges means payment is complete
            details: {
                ...selectedBooking.details,
                return_info: {
                    actual_return_time: new Date(actualReturnDate).toISOString(),
                    condition: 'excellent',
                    condition_details: ['No defects detected'],
                    additional_charges: {
                        damage_charge: 0,
                        total_additional: 0
                    }
                }
            }
        };
        
        await axios.put(
            `http://127.0.0.1:5006/api/booking-logs/${selectedBooking.booking_id}/payment`,
            returnInfoData
        );
        
        // 3. Update car availability (make car available again)
        if (selectedBooking.details?.car_details?.id) {
            try {
                await axios.put(
                    `/car/${selectedBooking.details.car_details.id}/availability`, 
                    { available: true }
                );
            } catch (error) {
                console.warn('Could not update car availability:', error);
                // Continue anyway since the booking is already updated
            }
        }
        
        alert('Car returned successfully in perfect condition! Thank you for using SmartCar.');
        
        // Redirect to index.html
        window.location.href = 'index.html';
        
    } catch (error) {
        console.error('Error ending booking:', error.response ? error.response.data : error);
        alert('Failed to process car return. Please try again later.');
    }
}

// Mock assessment result for testing purposes
function mockAssessmentResult() {
    // For testing, alternate between zero defects and some defects
    const useZeroDefects = Math.random() < 0.5; // 50% chance of zero defects
    
    assessmentResult = {
        defect_count: useZeroDefects ? 0 : 2,
        condition_summary: useZeroDefects ? 'Excellent - No issues' : 'Good - Minor wear',
        condition_code: useZeroDefects ? 'excellent' : 'good',
        damage_charge: useZeroDefects ? 0 : 50,
        details: useZeroDefects ? 
            ['No defects detected', 'Car is in excellent condition'] : 
            [
                'Minor scratches detected on rear bumper',
                'Small dent on passenger side door',
                'Interior is clean and well-maintained'
            ]
    };
    
    // Update the condition field with the result
    const conditionInput = document.getElementById('condition');
    const conditionDetails = document.getElementById('condition-details');
    const defectCountDisplay = document.getElementById('defect-count-display');
    
    defectCountDisplay.textContent = `Defect Count: ${assessmentResult.defect_count}`;
    conditionInput.value = assessmentResult.condition_summary;
    
    let detailsHTML = '<h4>Detailed Assessment:</h4><ul>';
    assessmentResult.details.forEach(detail => {
        detailsHTML += `<li>${detail}</li>`;
    });
    detailsHTML += '</ul>';
    conditionDetails.innerHTML = detailsHTML;
    
    // Check for zero defects and adjust UI accordingly
    if (assessmentResult.defect_count === 0) {
        handleZeroDefects();
    } else {
        // Calculate charges based on the assessment for cases with defects
        calculateCharges();
    }
    
    document.getElementById('upload-status').textContent = 'Analysis complete! (Mock data)';
    document.getElementById('upload-status').classList.remove('uploading-animation');
}

// Calculate additional charges
function calculateCharges() {
    if (!selectedBooking) {
        alert('Please select a booking first');
        return;
    }
    
    // Get actual return date
    const actualReturnDate = document.getElementById('actual-return-date').value;
    
    // Get damage charge from assessment result or default to 0
    let damageCharge = 0;
    if (assessmentResult && assessmentResult.damage_charge) {
        damageCharge = assessmentResult.damage_charge;
    } else {
        // If no assessment result, base it on the condition input value
        const condition = document.getElementById('condition').value;
        
        // Default condition-based charges if assessment isn't available
        switch (condition) {
            case 'Excellent - No issues':
                damageCharge = 0;
                break;
            case 'Good - Minor wear':
                damageCharge = 20;
                break;
            case 'Fair - Some issues':
                damageCharge = 50;
                break;
            case 'Poor - Significant issues':
                damageCharge = 100;
                break;
            default:
                damageCharge = 0;
        }
    }
    
    // Show the additional charges container and relevant buttons
    document.getElementById('additional-charges-container').style.display = 'block';
    document.getElementById('calculate-charges').style.display = 'block';
    document.getElementById('confirm-return').style.display = 'block';
    document.getElementById('end-booking').style.display = 'none';
    
    // Update charge display
    document.getElementById('damage-charge').textContent = formatCurrency(damageCharge);
    
    const totalAdditional = damageCharge;
    document.getElementById('total-additional').textContent = formatCurrency(totalAdditional);
    
    return {
        damageCharge,
        totalAdditional: damageCharge
    };
}

// Confirm car return
async function confirmReturn() {
    if (!selectedBooking) {
        alert('Please select a booking first');
        return;
    }
    
    if (!assessmentResult) {
        alert('Please analyze the car condition before confirming return');
        return;
    }
    
    // Calculate charges first
    const charges = calculateCharges();
    
    // Get actual return date
    const actualReturnDate = document.getElementById('actual-return-date').value;
    
    try {
        // 1. Update booking status to 'ended'
        const statusUpdateResponse = await axios.put(
            `http://127.0.0.1:5006/api/booking-logs/${selectedBooking.booking_id}/status`,
            { booking_status: 'ended' }
        );
        
        // 2. Update payment information with additional charges
        const additionalPaymentData = {
            payment_status: 'pending',
            total_amount: parseFloat(selectedBooking.total_amount || 0) + charges.totalAdditional,
            details: {
                ...selectedBooking.details,
                return_info: {
                    actual_return_time: new Date(actualReturnDate).toISOString(),
                    condition: assessmentResult.condition_code || 'unknown',
                    condition_details: assessmentResult.details || [],
                    additional_charges: {
                        damage_charge: charges.damageCharge,
                        total_additional: charges.totalAdditional
                    }
                }
            }
        };
        
        await axios.put(
            `http://127.0.0.1:5006/api/booking-logs/${selectedBooking.booking_id}/payment`,
            additionalPaymentData
        );
        
        // 3. Update car availability (make car available again)
        if (selectedBooking.details?.car_details?.id) {
            try {
                await axios.put(
                    `/car/${selectedBooking.details.car_details.id}/availability`, 
                    { available: true }
                );
            } catch (error) {
                console.warn('Could not update car availability:', error);
                // Continue anyway since the booking is already updated
            }
        }
        
        alert('Car returned successfully! Thank you for using SmartCar.');
        
        // Refresh the bookings list
        fetchActiveBookings();
        
        // Reset form
        document.getElementById('selected-booking').value = '';
        document.getElementById('condition').value = 'Awaiting analysis...';
        document.getElementById('condition-details').innerHTML = '';
        
        // Reset additional charges
        document.getElementById('damage-charge').textContent = '$0.00';
        document.getElementById('total-additional').textContent = '$0.00';
        
        // Clear photo previews
        document.getElementById('photo-preview-container').innerHTML = '';
        uploadedPhotos = [];
        assessmentResult = null;
        
        // Clear selected booking
        selectedBooking = null;
        
        // Disable form fields again
        toggleFormFields(false);
        
    } catch (error) {
        console.error('Error returning car:', error.response ? error.response.data : error);
        alert('Failed to process car return. Please try again later.');
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Button event listeners
    document.getElementById('calculate-charges').addEventListener('click', calculateCharges);
    document.getElementById('confirm-return').addEventListener('click', confirmReturn);
    document.getElementById('update-timing').addEventListener('click', setCurrentDateTime);
    document.getElementById('analyze-condition').addEventListener('click', analyzeCarCondition);
    
    // Add event listener for end booking button (if it exists)
    const endBookingBtn = document.getElementById('end-booking');
    if (endBookingBtn) {
        endBookingBtn.addEventListener('click', endBooking);
    }
    
    // Photo upload event listener
    document.getElementById('car-photos').addEventListener('change', handlePhotoUpload);
    
    // Reset file input when clicking the label directly
    const fileLabel = document.querySelector('.file-upload-label');
    if (fileLabel) {
        fileLabel.addEventListener('click', (e) => {
            if (!selectedBooking) {
                e.preventDefault();
                alert('Please select a booking first');
                return;
            }
            
            if (uploadedPhotos.length > 0) {
                // Only reset if we have already uploaded photos
                // and user is clicking the button again
                const confirmed = confirm("Do you want to clear the current selection and choose new files?");
                if (confirmed) {
                    uploadedPhotos = [];
                    document.getElementById('photo-preview-container').innerHTML = '';
                }
            }
        });
    }
    
    // Set current date and time
    setCurrentDateTime();
    
    // Fetch active bookings when page loads
    fetchActiveBookings();
    
    // Disable form fields initially
    toggleFormFields(false);
});