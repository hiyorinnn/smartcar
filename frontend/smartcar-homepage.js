// SmartCar Homepage JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize date pickers
    initializeDatePickers();
    
    // Initialize location search 
    initializeBasicLocationSearch();
    
    // Setup search button functionality
    setupSearchButton();
    
    // Setup authentication buttons
    setupAuthButtons();
    
    // Setup navigation links
    setupNavLinks();

    // Check if Google Maps API is loaded and initialize if available
    if (typeof google !== 'undefined' && typeof google.maps !== 'undefined') {
        initGoogleMapsAutocomplete();
    }
});


/**
 * Initialize the date pickers for pickup and return dates using Flatpickr
 */
function initializeDatePickers() {
    // This uses the Flatpickr library that's loaded in the HTML
    if (typeof flatpickr !== 'undefined') {
        const pickupDateEl = document.getElementById('pickup-date');
        const returnDateEl = document.getElementById('return-date');
        
        // Set default dates
        const today = new Date();
        const tomorrow = new Date();
        tomorrow.setDate(today.getDate() + 1);
        
        // Default pickup: today + 1 hour
        const defaultPickup = new Date();
        defaultPickup.setHours(defaultPickup.getHours() + 1);
        
        // Configure pickup date picker
        const pickupPicker = flatpickr(pickupDateEl, {
            minDate: "today",
            enableTime: true,
            dateFormat: "D j M, H:i",
            defaultDate: defaultPickup,
            onChange: function(selectedDates) {
                // When pickup date changes, update the minimum date for return
                returnPicker.set('minDate', selectedDates[0]);
                
                // If return date is earlier than new pickup date, update it
                if (returnPicker.selectedDates[0] < selectedDates[0]) {
                    const newReturnDate = new Date(selectedDates[0]);
                    newReturnDate.setDate(newReturnDate.getDate() + 1);
                    returnPicker.setDate(newReturnDate);
                }
            }
        });
        
        // Configure return date picker
        const returnPicker = flatpickr(returnDateEl, {
            minDate: tomorrow,
            enableTime: true,
            dateFormat: "D j M, H:i",
            defaultDate: tomorrow
        });
    } else {
        console.warn("Flatpickr library not loaded. Date inputs will use browser defaults.");
    }
}

/**
 * Initialize basic location search without Google Maps
 */
function initializeBasicLocationSearch() {
    const locationInput = document.getElementById('location-input');
    
    // Basic suggestions for common cities
    const locationSuggestions = [
        'Ang Mo Kio',
        'Bedok',
        'Bishan',
        'Bukit Batok',
        'Bukit Merah',
        'Bukit Panjang',
        'Bukit Timah',
        'Central Area',
        'Choa Chu Kang',
        'Clementi',
        'Hougang',
        'Geylang',
        'Jurong East',
        'Jurong West',
        'Kallang',
        'Marine Parade',
        'Pasir Ris',
        'Punggol',
        'Queenstown',
        'Sembawang',
        'Serangoon',
        'Tampines',
        'Toa Payoh',
        'Woodlands',
        'Yishun'
    ];
    
    // Create datalist element for suggestions
    const datalist = document.createElement('datalist');
    datalist.id = 'location-suggestions';
    
    // Add options to datalist
    locationSuggestions.forEach(location => {
        const option = document.createElement('option');
        option.value = location;
        datalist.appendChild(option);
    });
    
    // Add datalist to document
    document.body.appendChild(datalist);
    
    // Connect input to datalist
    locationInput.setAttribute('list', 'location-suggestions');
}

/**
 * Initialize Google Maps Places Autocomplete - called by the API callback
 */
function initGoogleMapsAutocomplete() {
    const locationInput = document.getElementById('location-input');
    
    if (!locationInput) return;
    
    // Create the autocomplete object
    const autocomplete = new google.maps.places.Autocomplete(locationInput, {
        types: ['(cities)'], // Restrict to cities only
    });
    
    // Remove the datalist if using Google Maps
    locationInput.removeAttribute('list');
    const datalist = document.getElementById('location-suggestions');
    if (datalist) {
        datalist.remove();
    }
    
    // Add place_changed event listener
    autocomplete.addListener('place_changed', function() {
        const place = autocomplete.getPlace();
        
        if (!place.geometry) {
            console.warn("No location details available for this input: " + place.name);
            return;
        }
        
        // Get location details
        const locationData = {
            name: place.name,
            address: place.formatted_address,
            latitude: place.geometry.location.lat(),
            longitude: place.geometry.location.lng()
        };
        
        // Store location data for search
        window.selectedLocation = locationData;
        
        // Update hidden fields with the coordinates
        const latInput = document.getElementById('location-lat');
        const lngInput = document.getElementById('location-lng');
        
        if (latInput) latInput.value = locationData.latitude;
        if (lngInput) lngInput.value = locationData.longitude;
    });
}

/**
 * Setup search button functionality
 */
function setupSearchButton() {
    const searchButton = document.getElementById('search-button');
    
    searchButton.addEventListener('click', function() {
        const locationInput = document.getElementById('location-input').value;
        const pickupDate = document.getElementById('pickup-date').value;
        const returnDate = document.getElementById('return-date').value;
        
        // Validate inputs
        if (!locationInput) {
            alert('Please enter a location');
            return;
        }
        
        if (!pickupDate) {
            alert('Please select a pickup date');
            return;
        }
        
        if (!returnDate) {
            alert('Please select a return date');
            return;
        }
        
        // Get coordinates if available
        const latInput = document.getElementById('location-lat');
        const lngInput = document.getElementById('location-lng');
        const lat = latInput ? latInput.value : null;
        const lng = lngInput ? lngInput.value : null;
        
        // Construct search parameters
        const searchParams = {
            location: locationInput,
            pickupDate: pickupDate,
            returnDate: returnDate,
            lat: lat,
            lng: lng
        };
        
        // For demo purposes, show search details
        alert(`Searching for cars in ${locationInput}\nFrom: ${pickupDate}\nTo: ${returnDate}`);
        
        console.log('Search parameters:', searchParams);
        
        // In a real application, you would redirect to search results or make an API call
        // window.location.href = `/search-results?location=${encodeURIComponent(locationInput)}&pickup=${encodeURIComponent(pickupDate)}&return=${encodeURIComponent(returnDate)}`;
    });
}

/**
 * Setup authentication buttons (sign in and sign up)
 */
function setupAuthButtons() {
    const signInButton = document.getElementById('sign-in-button');
    const signUpButton = document.getElementById('sign-up-button');
    
    if (signInButton) {
        signInButton.addEventListener('click', function() {
            alert('Opening sign in page');
            // In a real application: window.location.href = '/signin';
        });
    }
    
    if (signUpButton) {
        signUpButton.addEventListener('click', function() {
            alert('Opening sign up page');
            // In a real application: window.location.href = '/signup';
        });
    }
}

function setupNavLinks() {
    const becomeRenterLink = document.getElementById('become-renter-link');
    
    if (becomeRenterLink) {
        becomeRenterLink.addEventListener('click', function(e) {
            e.preventDefault();
            alert('Navigating to: Become a Renter');
        });
    }
    
}