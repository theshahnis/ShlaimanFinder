let map;
let markers = [];
let locationMode = false;

document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    autoSelectMap();  // Request user's location on load

    document.getElementById('refreshButton').addEventListener('click', function() {
        if (!isOnline()) {
            showOfflineAlert();
            return;
        }

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(position => {
                const latitude = position.coords.latitude;
                const longitude = position.coords.longitude;
                updateLocation(latitude, longitude);
            }, showError);
        } else {
            alert('Geolocation is not supported by this browser.');
        }
        refreshLocations();
    });

    // Load cached locations if offline
    if (!isOnline()) {
        loadCachedLocations();
    } else {
        refreshLocations();
    }
});

const locations = {
    israelCentral: [32.06607860466994, 34.78687443031782],
    amsterdam: [52.3723, 4.8924],
    jeraOnAir: [51.49037413994993, 5.892837121201148]
};

function initializeMap() {
    map = L.map('map').setView(locations.israelCentral, 11);  // Default to Israel Central
    applyMapMode(mapModes[currentMapModeIndex]);

    map.on('click', function(e) {
        if (locationMode) {
            const { lat, lng } = e.latlng;
            showLocationForm(lat, lng);
            locationMode = false;
        }
    });
    
}

function loadMap(location) {
    map.setView(locations[location], 11);
    refreshLocations();
}

function loadMap(location) {
    map.setView(locations[location], 11);
    refreshLocations();
}

function updateLocation(latitude, longitude) {
    if (!isOnline()) {
        showOfflineAlert();
        return;
    }

    fetch('/location/update', {  
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ latitude: latitude, longitude: longitude })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Location updated successfully:', data);
        refreshLocations(); 
    })
    .catch(error => {
        console.error('Error updating location:', error);
    });
}

function refreshLocations() {
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
    
    if (!isOnline()) {
        loadCachedLocations();
        return;
    }

    fetch('/location/locations')
        .then(response => response.json())
        .then(data => {

            // Save new data to local storage
            saveToLocalStorage('locations', data);

            // Process user locations
            data.users.forEach(location => {
                addMarker(location);
            });

            // Process static locations
            data.static_locations.forEach(location => {
                addMarker(location);
            });

            // Process meeting points
            data.meeting_points.forEach(location => {
                addMarker(location);
            });

            // Fetch and process hotels
            fetch('/location/hotels')
                .then(response => response.json())
                .then(hotels => {
                    hotels.forEach(hotel => {
                        addHotelMarker(hotel);
                    });
                });
        })
        .catch(error => {
            console.error('Error fetching locations:', error);
            // If fetching fails, load cached locations
            loadCachedLocations();
        });
}

function addHotelMarker(hotel) {
    const position = [hotel.latitude, hotel.longitude];
    const defaultHotelImage = '/images/hotel.jpg'; // Define default hotel image
    const hotelImage = hotel.image ? hotel.image : defaultHotelImage;
    const customIcon = L.divIcon({
        className: 'custom-marker blue',
        html: `<div class="marker-image" style="background-image: url('${hotelImage}');"></div>`,
        iconSize: [50, 60],
        iconAnchor: [25, 60],
        popupAnchor: [0, -60]
    });

    let popupContent = `
        <b>${hotel.name}</b><br>
        <p>Start Date: ${new Date(hotel.start_date).toLocaleDateString()}</p>
        <p>End Date: ${new Date(hotel.end_date).toLocaleDateString()}</p>
        <h4>Users staying in this hotel:</h4>
        <div class="attendees">`;

    hotel.users.forEach(user => {
        popupContent += `
            <img src="/profile_pics/${user.profile_image}" alt="${user.username}" title="${user.username}" class="attendee-icon" onclick="showUserModal('${user.username}', '/profile_pics/${user.profile_image}')">
        `;
    });

    popupContent += `
        </div>
        <a href="https://www.google.com/maps/dir/?api=1&destination=${hotel.latitude},${hotel.longitude}" target="_blank">
            <button class="navigate-button">Navigate to this hotel</button>
        </a>
    `;

    const marker = L.marker(position, { icon: customIcon }).addTo(map)
        .bindPopup(popupContent);
    markers.push(marker);
}

function showUserModal(username, imageUrl) {
    const modal = document.getElementById('userModal');
    const modalContent = document.getElementById('userModalContent');
    modalContent.innerHTML = `
        <h2>${username}</h2>
        <img src="${imageUrl}" alt="${username}" class="attendee-icon">
    `;
    modal.style.display = 'block';

    // Close the modal when clicking outside of it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    };

    // Close the modal when clicking on the close button
    document.querySelector('.user-modal-close').onclick = function() {
        modal.style.display = 'none';
    };
}

function loadCachedLocations() {
    const data = loadFromLocalStorage('locations');
    if (data) {
        console.log('Loaded cached locations:', data);

        // Process user locations
        data.users.forEach(location => {
            addMarker(location);
        });

        // Process static locations
        data.static_locations.forEach(location => {
            addMarker(location);
        });

        // Process meeting points
        data.meeting_points.forEach(location => {
            addMarker(location);
        });
    } else {
        console.log('No cached locations found.');
    }
}

function addMarker(location) {
    const position = [location.latitude, location.longitude];
    const iconColorClass = getIconColorClass(location);
    const profileImage = location.profile_image ? `${location.profile_image}` : 'default.png'; // Default user image
    const customIcon = L.divIcon({
        className: `custom-marker ${iconColorClass}`,
        html: `<div class="marker-image" style="background-image: url('${profileImage}');"></div>`,
        iconSize: [50, 60],
        iconAnchor: [25, 60],
        popupAnchor: [0, -60]
    });

    let popupContent = `
        <div style="background-color: #f9f9f9; padding: 8px; border-radius: 5px; text-align: center; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); font-size: 12px;">
            <b style="color: #333; font-size: 14px;">${location.username}</b><br>
            <p style="color: #555; font-size: 12px;">${location.note || 'No additional notes.'}</p>
            <p style="color: #888; font-size: 10px;">Last updated: ${location.created_at || 'N/A'}</p>
            ${location.isMeetingPoint ? `<p style="color: #555; font-size: 12px;">Remaining time: ${location.remaining_time}</p>` : ''}
            <a href="https://www.google.com/maps/dir/?api=1&destination=${location.latitude},${location.longitude}" target="_blank">
                <button class="navigate-button">Navigate</button>
            </a>
        </div>
    `;

    const marker = L.marker(position, { icon: customIcon }).addTo(map)
        .bindPopup(popupContent);
    markers.push(marker);
}

function startLocationSelection() {
    alert('Click on the map to set the location.');
    locationMode = true;
}

function getIconColorClass(location) {
    if (location.isMeetingPoint) {
        return 'pink';
    }

    if (location.created_at) {
        const now = new Date();
        const updatedAt = new Date(location.created_at);
        const diffHours = Math.abs(now - updatedAt) / 36e5;

        if (diffHours <= 1) {
            return 'green';
        } else if (diffHours <= 3) {
            return 'yellow';
        } else {
            return 'red';
        }
    }

    return 'blue'; // Static locations are marked as blue
}

function autoSelectMap() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            if (latitude >= 51.0 && latitude <= 53.0 && longitude >= 4.0 && longitude <= 5.0) {
                loadMap('amsterdam');
            } else if (latitude >= 51.0 && latitude <= 52.0 && longitude >= 5.0 && longitude <= 6.0) {
                loadMap('jeraOnAir');
            } else {
                loadMap('israelCentral');
            }

            updateLocation(latitude, longitude);
        }, showError);
    } else {
        alert('Geolocation is not supported by this browser.');
    }
}

function showError(error) {
    switch(error.code) {
        case error.PERMISSION_DENIED:
            alert('User denied the request for Geolocation.');
            break;
        case error.POSITION_UNAVAILABLE:
            alert('Location information is unavailable.');
            break;
        case error.TIMEOUT:
            alert('The request to get user location timed out.');
            break;
        case error.UNKNOWN_ERROR:
            alert('An unknown error occurred.');
            break;
    }
}

function showLocationForm(lat, lng) {
    const formHtml = `
        <div id="locationForm">
            <h3>Create Location</h3>
            <label for="locUsername">Name of the place:</label>
            <input type="text" id="locUsername" name="locUsername">
            <label for="locNote">Note:</label>
            <textarea id="locNote" name="locNote"></textarea>
            <label for="locImage">Image:</label>
            <input type="file" id="locImage" name="locImage">
            <label for="locType">Type:</label><br>
            <input type="radio" id="meetingPoint" name="locType" value="meetingPoint" checked>
            <label for="meetingPoint">Meeting Point</label><br>
            <input type="radio" id="staticPoint" name="locType" value="staticPoint">
            <label for="staticPoint">Static Location</label>
            <label for="locDuration" id="durationLabel">Duration (hours):</label>
            <input type="number" id="locDuration" name="locDuration" value="3">
            <div style="display: flex; justify-content: space-between;">
                <button onclick="submitLocation(${lat}, ${lng})">Submit</button>
                <button onclick="cancelLocation()">Cancel</button>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', formHtml);
    document.querySelectorAll('input[name="locType"]').forEach(radio => {
        radio.addEventListener('change', toggleDurationInput);
    });
    toggleDurationInput();
}

function toggleDurationInput() {
    const isMeetingPoint = document.getElementById('meetingPoint').checked;
    document.getElementById('locDuration').style.display = isMeetingPoint ? 'block' : 'none';
    document.getElementById('durationLabel').style.display = isMeetingPoint ? 'block' : 'none';
}

function submitLocation(lat, lng) {
    if (!isOnline()) {
        showOfflineAlert();
        return;
    }

    const username = document.getElementById('locUsername').value;
    const note = document.getElementById('locNote').value;
    const image = document.getElementById('locImage').files[0];
    const locType = document.querySelector('input[name="locType"]:checked').value;
    const duration = document.getElementById('locDuration').value;

    const formData = new FormData();
    formData.append('latitude', lat);
    formData.append('longitude', lng);
    formData.append('username', username);
    formData.append('note', note);
    formData.append('locType', locType);
    if (locType === 'meetingPoint') {
        formData.append('duration', duration);
    }
    if (image) {
        formData.append('image', image);
    }

    fetch('/location/create_location', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Location created successfully:', data);
        refreshLocations();
    })
    .catch(error => {
        console.error('Error creating location:', error);
    })
    .finally(() => {
        document.getElementById('locationForm').remove();
    });
}

function cancelLocation() {
    document.getElementById('locationForm').remove();
}

function isOnline() {
    return navigator.onLine;
}

function showOfflineAlert() {
    alert('No active internet connection. Please connect to the internet.');
}

function saveToLocalStorage(key, data) {
    console.log('Saving to Local Storage:', key, data);
    localStorage.setItem(key, JSON.stringify(data));
}

function loadFromLocalStorage(key) {
    const data = localStorage.getItem(key);
    console.log('Loading from Local Storage:', key, data);
    return data ? JSON.parse(data) : null;
}

