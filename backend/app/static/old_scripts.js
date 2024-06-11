let map;
let markers = [];
let locationMode = false;

document.addEventListener('DOMContentLoaded', function() {
    initializeMap();

    const mapModeToggle = document.getElementById('cycleMapModeButton');
    if (mapModeToggle) {
        mapModeToggle.addEventListener('click', function() {
            cycleMapMode();
        });
    }

    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            toggleDarkMode();
        });
    }

    const mapDarkModeToggle = document.getElementById('map-dark-mode-toggle');
    if (mapDarkModeToggle) {
        mapDarkModeToggle.addEventListener('click', function() {
            toggleMapDarkMode();
        });
    }

    // Apply general dark mode based on saved preference
    if (localStorage.getItem('darkMode') === 'enabled') {
        enableDarkMode();
    } else {
        disableDarkMode();
    }

    // Apply map dark mode based on saved preference
    if (localStorage.getItem('mapDarkMode') === 'enabled') {
        applyMapDarkMode();
    } else {
        removeMapDarkMode();
    }

    autoSelectMap();  // Request user's location on load
});

const locations = {
    israelCentral: [32.06607860466994, 34.78687443031782],
    amsterdam: [52.3723, 4.8924],
    jeraOnAir: [51.49037413994993, 5.892837121201148]
};

let mapModes = ['default', 'moderate', 'dark', 'white'];
let currentMapModeIndex = mapModes.indexOf(localStorage.getItem('mapMode')) || 0;

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

function cycleMapMode() {
    currentMapModeIndex++;
    if (currentMapModeIndex === mapModes.indexOf('default')) {
        currentMapModeIndex++;
    }
    currentMapModeIndex %= mapModes.length;

    const selectedMode = mapModes[currentMapModeIndex];
    localStorage.setItem('mapMode', selectedMode);
    applyMapMode(selectedMode);
    refreshLocations();
}

function applyMapMode(mode) {
    if (map) {
        map.eachLayer(function(layer) {
            map.removeLayer(layer);
        });

        let tileLayerUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

        if (mode === 'moderate') {
            tileLayerUrl = 'http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.png';
            removeMapDarkMode();
        } else if (mode === 'dark') {
            tileLayerUrl = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
        }

        L.tileLayer(tileLayerUrl, {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
    }
}

function toggleDarkMode() {
    const darkModeStylesheet = document.getElementById('dark-mode-stylesheet');
    if (darkModeStylesheet.disabled) {
        enableDarkMode();
    } else {
        disableDarkMode();
    }
}

function enableDarkMode() {
    const darkModeStylesheet = document.getElementById('dark-mode-stylesheet');
    darkModeStylesheet.disabled = false;
    localStorage.setItem('darkMode', 'enabled');
}

function disableDarkMode() {
    const darkModeStylesheet = document.getElementById('dark-mode-stylesheet');
    darkModeStylesheet.disabled = true;
    localStorage.setItem('darkMode', 'disabled');
}

function toggleMapDarkMode() {
    if (localStorage.getItem('mapDarkMode') === 'enabled') {
        removeMapDarkMode();
        localStorage.setItem('mapDarkMode', 'disabled');
    } else {
        applyMapDarkMode();
        localStorage.setItem('mapDarkMode', 'enabled');
    }
}

function applyMapDarkMode() {
    if (map) {
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        }).addTo(map);
    }
}

function removeMapDarkMode() {
    if (map) {
        map.eachLayer(function(layer) {
            map.removeLayer(layer);
        });

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
    }
}

function loadMap(location) {
    map.setView(locations[location], 11);
    refreshLocations();
}

function refreshLocations() {
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];

    fetch('/locations')
        .then(response => response.json())
        .then(data => {
            data.locations.forEach(location => {
                const position = [location.latitude, location.longitude];
                const iconColorClass = getIconColorClass(location);
                const customIcon = L.divIcon({
                    className: `custom-marker ${iconColorClass}`,
                    html: `<div class="marker-image" style="background-image: url('${location.profile_image}');"></div>`,
                    iconSize: [50, 60],
                    iconAnchor: [25, 60],
                    popupAnchor: [0, -60]
                });

                let popupContent = `
                    <b>${location.username}</b><br>
                    <p>${location.note || ''}</p>
                    <p>Last updated: ${location.created_at}</p>
                `;
                if (location.isMeetingPoint) {
                    popupContent += `<p>Remaining time: ${location.remaining_time}</p>`;
                }
                popupContent += `
                    <a href="https://www.google.com/maps/dir/?api=1&destination=${location.latitude},${location.longitude}" target="_blank">
                        Navigate to this location
                    </a>
                `;

                const marker = L.marker(position, { icon: customIcon }).addTo(map)
                    .bindPopup(popupContent);
                markers.push(marker);
            });
        })
        .catch(error => {
            console.error('Error fetching locations:', error);
        });
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

function showLocationForm(lat, lng) {
    const formHtml = `
        <div id="locationForm" style="position: absolute; top: 20px; left: 20px; background: white; padding: 20px; border: 1px solid #ccc; z-index: 1000;">
            <h3>Create Location</h3>
            <label for="locUsername">Name of the place:</label>
            <input type="text" id="locUsername" name="locUsername"><br>
            <label for="locNote">Note</label>
            <textarea id="locNote" name="locNote"></textarea><br>
            <label for="locImage">Image</label>
            <input type="file" id="locImage" name="locImage"><br>
            <label for="locType">Type</label><br>
            <input type="radio" id="meetingPoint" name="locType" value="meetingPoint" checked>
            <label for="meetingPoint">Meeting Point</label><br>
            <input type="radio" id="staticPoint" name="locType" value="staticPoint">
            <label for="staticPoint">Static Location</label><br>
            <label for="locDuration" id="durationLabel">Duration (hours)</label>
            <input type="number" id="locDuration" name="locDuration" value="3"><br>
            <button onclick="submitLocation(${lat}, ${lng})">Submit</button>
            <button onclick="cancelLocation()">Cancel</button>
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

    fetch('/create_location', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Location created successfully:', data);
        fetchLocations();
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
