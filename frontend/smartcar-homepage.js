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
        
        // Store in sessionStorage
        console.log(`Storing location: ${locationInput}`);
        sessionStorage.setItem('selectedLocation', locationInput);
        
        // Direct user to booking.html
        window.location.href = './booking.html';
    });
}

// Handle current location button
document.getElementById('current-location-btn')?.addEventListener('click', function() {
    console.log('Selected location from sessionStorage:', sessionStorage.getItem('selectedLocation'));
    
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