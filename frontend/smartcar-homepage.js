document.addEventListener('DOMContentLoaded', function() {
    // Initialize location search 
    initializeBasicLocationSearch();
    
    // Setup search button functionality
    setupSearchButton();
});

/**
 * Initialize basic location search without Google Maps
 */
function initializeBasicLocationSearch() {
    const locationInput = document.getElementById('location-input');
    
    // Basic suggestions for common cities
    const locationSuggestions = [
        'Ang Mo Kio', 'Bedok', 'Bishan', 'Bukit Batok', 'Bukit Merah',
        'Bukit Panjang', 'Bukit Timah', 'Central Area', 'Choa Chu Kang',
        'Clementi', 'Hougang', 'Geylang', 'Jurong East', 'Jurong West',
        'Kallang', 'Marine Parade', 'Pasir Ris', 'Punggol', 'Queenstown',
        'Sembawang', 'Serangoon', 'Tampines', 'Toa Payoh', 'Woodlands', 'Yishun'
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
 * Setup search button functionality
 */
function setupSearchButton() {
    const searchButton = document.getElementById('search-button');
    
    searchButton.addEventListener('click', function() {
        const locationInput = document.getElementById('location-input').value;
        
        // Validate location input
        if (!locationInput) {
            alert('Please enter a location');
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
            lat: lat,
            lng: lng
        };
        
        // Create URLSearchParams object from searchParams
        const queryParams = new URLSearchParams();
        for (const [key, value] of Object.entries(searchParams)) {
            if (value) queryParams.append(key, value);
        }
        
        // Direct user to booking.html with search parameters
        window.location.href = './booking.html';
    });
}

// Handle current location button
document.getElementById('current-location-btn')?.addEventListener('click', function() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            document.getElementById('location-lat').value = position.coords.latitude;
            document.getElementById('location-lng').value = position.coords.longitude;
            document.getElementById('location-input').value = "Current location";
        }, function() {
            alert("Unable to get your location. Please enter it manually.");
        });
    } else {
        alert("Geolocation is not supported by your browser. Please enter your location manually.");
    }
});